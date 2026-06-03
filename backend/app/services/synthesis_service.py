from __future__ import annotations
"""
Synthesis Service — cross-paper analysis, aggregation, and pattern extraction.

Provides:
- Methodology distribution
- Year trends  
- Common limitations extraction (LLM-powered)
- Pattern extraction via embedding clustering
- Field-specific aggregation
"""
import json
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.paper import Paper, PaperStatus
from app.models.evaluation import EvaluationResult, ResearchQuestion
from app.models.extraction import ExtractionResult
from app.models.chunk import Chunk
from app.services.llm_client import call_llm_sync, extract_json_from_response


def get_overview_stats(db: Session, user_id: str | None = None) -> dict:
    """Dashboard statistics including pipeline phase counts, scoped by user_id."""
    from app.models.screening import ScreeningResult

    paper_query = db.query(Paper)
    eval_query = db.query(EvaluationResult).join(Paper)
    screening_query = db.query(ScreeningResult).join(Paper)
    rq_query = db.query(ResearchQuestion)

    if user_id:
        paper_query = paper_query.filter(Paper.user_id == user_id)
        eval_query = eval_query.filter(Paper.user_id == user_id)
        screening_query = screening_query.filter(Paper.user_id == user_id)
        rq_query = rq_query.filter(ResearchQuestion.user_id == user_id)

    total_papers = paper_query.count()
    processed = paper_query.filter(Paper.status == "processed").count()
    included = paper_query.filter(Paper.status == "included").count()
    excluded = paper_query.filter(Paper.status == "excluded").count()
    pending = paper_query.filter(Paper.status == "pending").count()
    total_evaluations = eval_query.count()
    total_screenings = screening_query.count()
    total_rqs = rq_query.count()

    return {
        "total_papers": total_papers,
        "pending_papers": pending,
        "processed_papers": processed,
        "included_papers": included,
        "excluded_papers": excluded,
        "total_evaluations": total_evaluations,
        "total_screenings": total_screenings,
        "total_research_questions": total_rqs,
    }


def get_methodology_distribution(
    db: Session,
    paper_ids: list[str] | None = None,
    user_id: str | None = None,
) -> list[dict]:
    """
    Extract methodology distribution across papers using evaluation results.
    """
    # Scope papers by user
    if user_id:
        user_paper_ids = [p.id for p in db.query(Paper).filter(Paper.user_id == user_id).all()]
        if paper_ids:
            paper_ids = list(set(paper_ids) & set(user_paper_ids))
        else:
            paper_ids = user_paper_ids

    # 1. Look for methodology-related RQs (broad keyword set)
    method_keywords = ["%method%", "%technique%", "%approach%", "%design%"]
    rqs = []
    for kw in method_keywords:
        rq_query = db.query(ResearchQuestion).filter(ResearchQuestion.question_text.ilike(kw))
        if user_id:
            rq_query = rq_query.filter(ResearchQuestion.user_id == user_id)
        rqs = rq_query.all()
        if rqs:
            break

    if rqs:
        query = db.query(EvaluationResult).filter(
            EvaluationResult.question_id.in_([rq.id for rq in rqs]),
            EvaluationResult.answer.isnot(None),
        )
        if paper_ids is not None:
            query = query.filter(EvaluationResult.paper_id.in_(paper_ids))
        results = query.all()
        if results:
            answers = [r.answer for r in results if r.answer]
            return _categorize_values(answers, "methodology")

    # 2. Fallback: use ALL evaluation answers across every RQ
    rq_query = db.query(ResearchQuestion)
    if user_id:
        rq_query = rq_query.filter(ResearchQuestion.user_id == user_id)
    all_rqs = rq_query.all()
    
    if all_rqs:
        query = db.query(EvaluationResult).filter(
            EvaluationResult.question_id.in_([rq.id for rq in all_rqs]),
            EvaluationResult.answer.isnot(None),
        )
        if paper_ids is not None:
            query = query.filter(EvaluationResult.paper_id.in_(paper_ids))
        results = query.all()
        if results:
            answers = [r.answer for r in results if r.answer]
            return _categorize_values(answers, "all")

    # 3. Last resort: legacy ExtractionResult table
    query = (
        db.query(ExtractionResult.value, func.count(ExtractionResult.id))
        .filter(ExtractionResult.field_name == "methodology")
        .filter(ExtractionResult.value.isnot(None))
    )
    if paper_ids is not None:
        query = query.filter(ExtractionResult.paper_id.in_(paper_ids))

    results = query.group_by(ExtractionResult.value).order_by(
        func.count(ExtractionResult.id).desc()
    ).all()

    return [{"label": r[0], "count": r[1]} for r in results]


def get_year_trends(
    db: Session,
    paper_ids: list[str] | None = None,
    user_id: str | None = None,
) -> list[dict]:
    """Paper count by publication year, filtered by user."""
    # Scope papers by user
    if user_id:
        user_paper_ids = [p.id for p in db.query(Paper).filter(Paper.user_id == user_id).all()]
        if paper_ids:
            paper_ids = list(set(paper_ids) & set(user_paper_ids))
        else:
            paper_ids = user_paper_ids

    query = db.query(Paper.year, func.count(Paper.id)).filter(Paper.year.isnot(None))
    if paper_ids is not None:
        query = query.filter(Paper.id.in_(paper_ids))
    else:
        # If user_id is provided but no paper_ids, we must at least filter papers by user
        if user_id:
            query = query.filter(Paper.user_id == user_id)
            
    results = query.group_by(Paper.year).order_by(Paper.year).all()
    return [{"year": r[0], "count": r[1]} for r in results]


def get_limitations_summary(
    db: Session,
    paper_ids: list[str] | None = None,
    user_id: str | None = None,
) -> list[dict]:
    """
    Extract common limitations across papers using evaluation results or LLM.
    """
    # Scope papers by user
    if user_id:
        user_paper_ids = [p.id for p in db.query(Paper).filter(Paper.user_id == user_id).all()]
        if paper_ids:
            paper_ids = list(set(paper_ids) & set(user_paper_ids))
        else:
            paper_ids = user_paper_ids

    # Look for limitation-related RQs
    rq_query = db.query(ResearchQuestion).filter(
        ResearchQuestion.question_text.ilike("%limitation%")
    )
    if user_id:
        rq_query = rq_query.filter(ResearchQuestion.user_id == user_id)
    rqs = rq_query.all()

    limitations = []

    if rqs:
        query = db.query(EvaluationResult).filter(
            EvaluationResult.question_id.in_([rq.id for rq in rqs]),
            EvaluationResult.answer.isnot(None),
        )
        if paper_ids is not None:
            query = query.filter(EvaluationResult.paper_id.in_(paper_ids))

        results = query.all()
        for r in results:
            paper = db.query(Paper).filter(Paper.id == r.paper_id).first()
            limitations.append({
                "paper_id": r.paper_id,
                "paper_title": paper.title if paper else "Unknown",
                "limitation": r.answer,
                "source_quote": r.source_quote,
                "source_page": r.source_page,
            })

    return limitations


def get_aggregation_table(
    db: Session,
    paper_ids: list[str] | None = None,
    user_id: str | None = None,
) -> dict:
    """
    Build a comprehensive aggregation table across papers.
    Uses evaluation results and paper metadata.
    """
    # Scope papers by user
    if user_id:
        user_paper_ids = [p.id for p in db.query(Paper).filter(Paper.user_id == user_id).all()]
        if paper_ids:
            paper_ids = list(set(paper_ids) & set(user_paper_ids))
        else:
            paper_ids = user_paper_ids

    if paper_ids is not None:
        papers = db.query(Paper).filter(Paper.id.in_(paper_ids)).all()
    else:
        paper_query = db.query(Paper).filter(Paper.status == PaperStatus.INCLUDED.value)
        if user_id:
            paper_query = paper_query.filter(Paper.user_id == user_id)
        papers = paper_query.all()

    rows = []
    rq_query = db.query(ResearchQuestion)
    if user_id:
        rq_query = rq_query.filter(ResearchQuestion.user_id == user_id)
    rqs = rq_query.all()
    field_names = [rq.question_text[:40] for rq in rqs]

    for paper in papers:
        row = {
            "paper_id": paper.id,
            "title": paper.title,
            "year": paper.year,
            "authors": paper.authors,
            "values": {},
            "scores": {},
        }

        for rq in rqs:
            er = db.query(EvaluationResult).filter(
                EvaluationResult.paper_id == paper.id,
                EvaluationResult.question_id == rq.id,
            ).first()

            field_key = rq.question_text[:40]
            if er:
                row["values"][field_key] = er.answer
                row["scores"][field_key] = er.score
            else:
                row["values"][field_key] = None
                row["scores"][field_key] = 0.0

        rows.append(row)

    return {
        "fields": field_names,
        "rows": rows,
        "total_papers": len(rows),
    }


def cluster_papers_by_field(
    db: Session,
    num_clusters: int = 5,
    paper_ids: list[str] | None = None,
    user_id: str | None = None,
) -> list[dict]:
    """
    Cluster papers using embedding similarity.
    Enhanced with LLM-generated cluster labels.
    """
    import numpy as np
    from app.services.vector_store import generate_embeddings

    # Scope papers by user
    if user_id:
        user_paper_ids = [p.id for p in db.query(Paper).filter(Paper.user_id == user_id).all()]
        if paper_ids:
            paper_ids = list(set(paper_ids) & set(user_paper_ids))
        else:
            paper_ids = user_paper_ids

    if paper_ids is not None:
        papers = db.query(Paper).filter(Paper.id.in_(paper_ids)).all()
    else:
        paper_query = db.query(Paper).filter(
            Paper.status.in_([PaperStatus.INCLUDED.value, PaperStatus.PROCESSED.value])
        )
        if user_id:
            paper_query = paper_query.filter(Paper.user_id == user_id)
        papers = paper_query.all()

    if len(papers) < 2:
        return [{
            "cluster_id": 0,
            "label": "All Papers",
            "paper_ids": [p.id for p in papers],
            "paper_titles": [p.title for p in papers],
            "size": len(papers),
        }]

    # Generate embeddings from titles + abstracts
    texts = []
    for p in papers:
        text = p.title
        if p.abstract:
            text += " " + p.abstract[:500]
        texts.append(text)

    embeddings = generate_embeddings(texts)
    matrix = np.array(embeddings).astype("float32")

    num_clusters = min(num_clusters, len(papers))

    try:
        from sklearn.cluster import KMeans
        km = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        labels = km.fit_predict(matrix)
    except ImportError:
        import faiss
        d = matrix.shape[1]
        kmeans = faiss.Kmeans(d, num_clusters, niter=20, verbose=False)
        kmeans.train(matrix)
        _, labels = kmeans.assign(matrix)
        labels = labels.flatten()

    # Group papers by cluster
    clusters_map: dict[int, list] = {}
    for idx, label in enumerate(labels):
        label_int = int(label)
        if label_int not in clusters_map:
            clusters_map[label_int] = []
        clusters_map[label_int].append(papers[idx])

    clusters = []
    for cluster_id, cluster_papers in sorted(clusters_map.items()):
        # Generate descriptive label from paper titles
        titles = [p.title for p in cluster_papers[:5]]
        label = _generate_cluster_label(titles, cluster_id)

        clusters.append({
            "cluster_id": cluster_id,
            "label": label,
            "paper_ids": [p.id for p in cluster_papers],
            "paper_titles": [p.title for p in cluster_papers],
            "size": len(cluster_papers),
        })

    return clusters


def _categorize_values(answers: list[str], field_name: str) -> list[dict]:
    """Deduplicate and count methodology answers."""
    counts: dict[str, int] = {}
    for answer in answers:
        key = answer.strip()[:100].lower()
        counts[key] = counts.get(key, 0) + 1

    result = [{"label": k, "count": v} for k, v in counts.items()]
    result.sort(key=lambda x: x["count"], reverse=True)
    return result[:20]


def _generate_cluster_label(titles: list[str], cluster_id: int) -> str:
    """Generate a descriptive cluster label from paper titles."""
    if not titles:
        return f"Cluster {cluster_id + 1}"

    try:
        titles_text = "\n".join(f"- {t}" for t in titles[:5])
        prompt = f"""Given these paper titles from a cluster, provide a short 2-4 word topic label:

{titles_text}

Respond with ONLY the topic label, nothing else."""

        response = call_llm_sync(prompt, max_tokens=30)
        label = response.strip().strip('"').strip("'")
        if label and len(label) < 60:
            return label
    except Exception:
        pass

    return f"Topic Cluster {cluster_id + 1}"
