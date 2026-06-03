"""
Synthesis API router — aggregation tables, pattern extraction, overview stats.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.synthesis import (
    AggregationRequest, AggregationTableResponse,
    FrequencyItem, TrendItem, LimitationItem,
    ClusterRequest, ClusterResponse,
    SynthesisOverviewResponse,
)
from app.utils.auth import get_current_user

router = APIRouter(prefix="/synthesis", tags=["Synthesis"])


@router.get("/overview", response_model=SynthesisOverviewResponse)
def get_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get comprehensive pipeline overview statistics."""
    from app.services.synthesis_service import get_overview_stats
    stats = get_overview_stats(db, user_id=current_user.id)
    return SynthesisOverviewResponse(**stats)


@router.post("/aggregate", response_model=AggregationTableResponse)
def get_aggregation(
    req: AggregationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Build aggregation table across papers using evaluation results."""
    from app.services.synthesis_service import get_aggregation_table
    data = get_aggregation_table(db, req.paper_ids, user_id=current_user.id)
    return AggregationTableResponse(**data)


@router.post("/methods-distribution")
def get_methods_distribution(
    req: AggregationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get methodology distribution across papers."""
    from app.services.synthesis_service import get_methodology_distribution
    data = get_methodology_distribution(db, req.paper_ids, user_id=current_user.id)
    return {"data": [FrequencyItem(**d) for d in data]}


@router.post("/year-trends")
def get_year_trends(
    req: AggregationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get year-wise publication trends."""
    from app.services.synthesis_service import get_year_trends
    data = get_year_trends(db, req.paper_ids, user_id=current_user.id)
    return {"data": [TrendItem(**d) for d in data]}


@router.post("/limitations")
def get_limitations(
    req: AggregationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Extract common limitations across papers."""
    from app.services.synthesis_service import get_limitations_summary
    data = get_limitations_summary(db, req.paper_ids, user_id=current_user.id)
    return {"data": [LimitationItem(**d) for d in data]}


@router.post("/patterns", response_model=list[ClusterResponse])
def extract_patterns(
    req: ClusterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cluster papers by semantic similarity to discover patterns."""
    from app.services.synthesis_service import cluster_papers_by_field
    clusters = cluster_papers_by_field(db, req.num_clusters, req.paper_ids, user_id=current_user.id)
    return [ClusterResponse(**c) for c in clusters]
