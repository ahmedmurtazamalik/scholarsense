import sys
import os

# Ensure the app directory is in the path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.models.paper import Paper, PaperStatus
from app.models.screening import ScreeningCriteria, ScreeningResult
from app.models.evaluation import ResearchQuestion, EvaluationResult
from app.models.extraction import ExtractionSchema, ExtractionResult
from app.models.matrix import Matrix
from app.models.audit_log import AuditLog
from datetime import datetime, timezone
import uuid


def seed_pipeline():
    db = SessionLocal()
    try:
        # 1. Fetch user (default or first user)
        user = db.query(User).first()
        if not user:
            print("No users found. Please run init_db.py or register a user first.")
            return

        user_id = user.id
        print(f"Seeding pipeline data for user: {user.name} ({user.email})")

        # 2. Find or create the two papers
        attention_paper = (
            db.query(Paper)
            .filter(Paper.user_id == user_id)
            .filter(Paper.title.ilike("%attention%"))
            .first()
        )
        if not attention_paper:
            print("Creating Attention paper placeholder...")
            attention_paper = Paper(
                id=str(uuid.uuid4()),
                title="Attention Is All You Need",
                authors=["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit", "Llion Jones", "Aidan N. Gomez", "Lukasz Kaiser", "Illia Polosukhin"],
                year=2017,
                abstract="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely. Experiments on two machine translation tasks show these models to be superior in quality while being more parallelizable and requiring significantly less time to train.",
                status=PaperStatus.PROCESSED.value,
                user_id=user_id
            )
            db.add(attention_paper)
            db.flush()

        bert_paper = (
            db.query(Paper)
            .filter(Paper.user_id == user_id)
            .filter(Paper.title.ilike("%bert%"))
            .first()
        )
        if not bert_paper:
            print("Creating BERT paper placeholder...")
            bert_paper = Paper(
                id=str(uuid.uuid4()),
                title="BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                authors=["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
                year=2018,
                abstract="We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
                status=PaperStatus.PROCESSED.value,
                user_id=user_id
            )
            db.add(bert_paper)
            db.flush()

        # Update paper status to INCLUDED to represent completed stages
        attention_paper.status = PaperStatus.INCLUDED.value
        bert_paper.status = PaperStatus.INCLUDED.value
        db.flush()

        # 3. Create Screening Criteria & Results
        print("Creating Screening Criteria...")
        criteria = db.query(ScreeningCriteria).filter(ScreeningCriteria.user_id == user_id).first()
        if not criteria:
            criteria = ScreeningCriteria(
                id=str(uuid.uuid4()),
                name="Deep Learning NLP Review",
                description="Filters papers related to modern deep learning architectures in natural language processing.",
                criteria_definition={
                    "year_range": [2015, 2025],
                    "paper_types": ["journal", "conference", "preprint"],
                    "required_keywords": ["transformer", "attention", "nlp", "language"],
                    "excluded_keywords": ["robotics", "hardware"],
                    "min_pages": 4
                },
                threshold=0.6,
                user_id=user_id
            )
            db.add(criteria)
            db.flush()

        # Clear existing screening results to prevent duplicates
        db.query(ScreeningResult).filter(ScreeningResult.criteria_id == criteria.id).delete()
        
        print("Adding Screening Results...")
        r1 = ScreeningResult(
            paper_id=attention_paper.id,
            criteria_id=criteria.id,
            filter_scores={"year": 1.0, "paper_type": 1.0, "required_keywords": 1.0, "excluded_keywords": 1.0},
            final_score=1.0,
            passed=True,
            exclusion_reason=None
        )
        r2 = ScreeningResult(
            paper_id=bert_paper.id,
            criteria_id=criteria.id,
            filter_scores={"year": 1.0, "paper_type": 1.0, "required_keywords": 1.0, "excluded_keywords": 1.0},
            final_score=1.0,
            passed=True,
            exclusion_reason=None
        )
        db.add(r1)
        db.add(r2)

        # 4. Create Research Questions & Evaluation Results
        print("Creating Research Questions...")
        rqs = db.query(ResearchQuestion).filter(ResearchQuestion.user_id == user_id).all()
        if not rqs:
            rq1 = ResearchQuestion(
                id=str(uuid.uuid4()),
                question_text="What is the core architecture introduced?",
                description="Describe the main neural network architecture or representation model proposed by the authors.",
                weight=1.2,
                user_id=user_id
            )
            rq2 = ResearchQuestion(
                id=str(uuid.uuid4()),
                question_text="What NLP tasks was the model evaluated on?",
                description="List the specific datasets and translation/understanding benchmarks used.",
                weight=1.0,
                user_id=user_id
            )
            rq3 = ResearchQuestion(
                id=str(uuid.uuid4()),
                question_text="What are the main limitations or computational demands?",
                description="Identify training bottlenecks, hardware required, or sequence size constraints.",
                weight=0.8,
                user_id=user_id
            )
            db.add(rq1)
            db.add(rq2)
            db.add(rq3)
            db.flush()
            rqs = [rq1, rq2, rq3]

        # Clear existing evaluation results to prevent duplicates
        db.query(EvaluationResult).filter(EvaluationResult.paper_id.in_([attention_paper.id, bert_paper.id])).delete()

        print("Adding Evaluation Results...")
        # Attention Paper evaluations
        e1_att = EvaluationResult(
            paper_id=attention_paper.id,
            question_id=rqs[0].id,
            answer="The core architecture introduced is the Transformer, which dispenses with recurrence and convolutions entirely, relying solely on self-attention mechanisms to compute representations of input and output.",
            score=1.0,
            source_quote="We propose a new simple network architecture, the Transformer, based solely on attention mechanisms...",
            source_page=1,
            reasoning="The paper defines the architecture directly in the abstract and intro.",
            context_chunk_ids=[]
        )
        e2_att = EvaluationResult(
            paper_id=attention_paper.id,
            question_id=rqs[1].id,
            answer="Evaluated on two main machine translation benchmarks: WMT 2014 English-to-German translation and WMT 2014 English-to-French translation.",
            score=0.9,
            source_quote="On the WMT 2014 English-to-German translation task, the big model establishes a new state-of-the-art...",
            source_page=6,
            reasoning="Clearly listed in the Experiments section.",
            context_chunk_ids=[]
        )
        e3_att = EvaluationResult(
            paper_id=attention_paper.id,
            question_id=rqs[2].id,
            answer="The self-attention mechanism has quadratic complexity with respect to the sequence length, making it computationally expensive for very long sequences.",
            score=0.8,
            source_quote="Computational complexity of self-attention layers is O(n^2 * d) where n is sequence length...",
            source_page=5,
            reasoning="Identified in complexity comparison tables.",
            context_chunk_ids=[]
        )

        # BERT Paper evaluations
        e1_bert = EvaluationResult(
            paper_id=bert_paper.id,
            question_id=rqs[0].id,
            answer="Introduces BERT (Bidirectional Encoder Representations from Transformers), a deep bidirectional representation pre-trained by jointly masking left and right context in all layers.",
            score=1.0,
            source_quote="BERT is designed to pre-train deep bidirectional representations from unlabeled text...",
            source_page=1,
            reasoning="Well described in the abstract and model description.",
            context_chunk_ids=[]
        )
        e2_bert = EvaluationResult(
            paper_id=bert_paper.id,
            question_id=rqs[1].id,
            answer="Evaluated on 11 NLP benchmarks including the GLUE (General Language Understanding Evaluation) suite, SQuAD v1.1 / v2.0 question answering, and SWAG.",
            score=1.0,
            source_quote="BERT obtains new state-of-the-art results on eleven NLP tasks...",
            source_page=6,
            reasoning="Extensive results section covers all 11 evaluations.",
            context_chunk_ids=[]
        )
        e3_bert = EvaluationResult(
            paper_id=bert_paper.id,
            question_id=rqs[2].id,
            answer="Pre-training is highly resource-intensive, requiring 4 to 16 Cloud TPUs for multiple days, making it difficult to train from scratch without substantial hardware.",
            score=0.85,
            source_quote="BERT_BASE was trained on 4 Cloud TPUs for 4 days... BERT_LARGE on 16 Cloud TPUs...",
            source_page=7,
            reasoning="Described in model training details.",
            context_chunk_ids=[]
        )
        db.add_all([e1_att, e2_att, e3_att, e1_bert, e2_bert, e3_bert])

        # 5. Create Extraction Schema & Results
        print("Creating Extraction Schema...")
        schema = db.query(ExtractionSchema).filter(ExtractionSchema.user_id == user_id).first()
        if not schema:
            schema = ExtractionSchema(
                id=str(uuid.uuid4()),
                name="NLP Model Specifications",
                description="Extracts parameter size, architecture details, and dataset dimensions.",
                fields_definition=[
                    {"name": "architecture", "type": "string", "description": "Type of neural network"},
                    {"name": "parameters", "type": "string", "description": "Number of weights/parameters"},
                    {"name": "pre_training_data", "type": "string", "description": "Dataset sizes used for training"}
                ],
                template_type="cs",
                user_id=user_id
            )
            db.add(schema)
            db.flush()

        # Clear existing extraction results
        db.query(ExtractionResult).filter(ExtractionResult.schema_id == schema.id).delete()

        print("Adding Extraction Results...")
        # Attention
        ext1_att = ExtractionResult(
            paper_id=attention_paper.id,
            schema_id=schema.id,
            field_name="architecture",
            value="Transformer Encoder-Decoder",
            confidence=0.95,
            source_text="We propose a new simple network architecture, the Transformer...",
            source_page=1,
            is_user_corrected=False
        )
        ext2_att = ExtractionResult(
            paper_id=attention_paper.id,
            schema_id=schema.id,
            field_name="parameters",
            value="65M (base), 213M (big)",
            confidence=0.90,
            source_text="The base model has 65 million parameters, big model has 213 million.",
            source_page=6,
            is_user_corrected=False
        )
        ext3_att = ExtractionResult(
            paper_id=attention_paper.id,
            schema_id=schema.id,
            field_name="pre_training_data",
            value="WMT 2014 English-German (4.5M sentence pairs)",
            confidence=0.88,
            source_text="We trained on the standard WMT 2014 English-German dataset...",
            source_page=5,
            is_user_corrected=False
        )

        # BERT
        ext1_bert = ExtractionResult(
            paper_id=bert_paper.id,
            schema_id=schema.id,
            field_name="architecture",
            value="Bidirectional Transformer Encoder",
            confidence=0.98,
            source_text="BERT is designed to pre-train deep bidirectional representations...",
            source_page=1,
            is_user_corrected=False
        )
        ext2_bert = ExtractionResult(
            paper_id=bert_paper.id,
            schema_id=schema.id,
            field_name="parameters",
            value="110M (base), 340M (large)",
            confidence=0.95,
            source_text="BERT_BASE contains 110M parameters. BERT_LARGE contains 340M parameters.",
            source_page=5,
            is_user_corrected=False
        )
        ext3_bert = ExtractionResult(
            paper_id=bert_paper.id,
            schema_id=schema.id,
            field_name="pre_training_data",
            value="BooksCorpus (800M words) + Wikipedia (2,500M words)",
            confidence=0.92,
            source_text="We train on BooksCorpus and English Wikipedia...",
            source_page=4,
            is_user_corrected=False
        )
        db.add_all([ext1_att, ext2_att, ext3_att, ext1_bert, ext2_bert, ext3_bert])
        db.flush()

        # 6. Create Matrix
        print("Creating Matrix...")
        db.query(Matrix).filter(Matrix.schema_id == schema.id).delete()
        matrix_data = {
            "fields": ["architecture", "parameters", "pre_training_data"],
            "rows": [
                {
                    "paper_id": attention_paper.id,
                    "paper_title": attention_paper.title,
                    "values": {
                        "architecture": "Transformer Encoder-Decoder",
                        "parameters": "65M (base), 213M (big)",
                        "pre_training_data": "WMT 2014 English-German (4.5M sentence pairs)"
                    },
                    "confidences": {
                        "architecture": 0.95,
                        "parameters": 0.90,
                        "pre_training_data": 0.88
                    },
                    "sources": {
                        "architecture": {"text": "We propose a new simple network architecture, the Transformer...", "page": 1},
                        "parameters": {"text": "The base model has 65 million parameters, big model has 213 million.", "page": 6},
                        "pre_training_data": {"text": "We trained on the standard WMT 2014 English-German dataset...", "page": 5}
                    }
                },
                {
                    "paper_id": bert_paper.id,
                    "paper_title": bert_paper.title,
                    "values": {
                        "architecture": "Bidirectional Transformer Encoder",
                        "parameters": "110M (base), 340M (large)",
                        "pre_training_data": "BooksCorpus (800M words) + Wikipedia (2,500M words)"
                    },
                    "confidences": {
                        "architecture": 0.98,
                        "parameters": 0.95,
                        "pre_training_data": 0.92
                    },
                    "sources": {
                        "architecture": {"text": "BERT is designed to pre-train deep bidirectional representations...", "page": 1},
                        "parameters": {"text": "BERT_BASE contains 110M parameters. BERT_LARGE contains 340M parameters.", "page": 5},
                        "pre_training_data": {"text": "We train on BooksCorpus and English Wikipedia...", "page": 4}
                    }
                }
            ]
        }

        matrix = Matrix(
            id=str(uuid.uuid4()),
            name="NLP Models Overview",
            schema_id=schema.id,
            data=matrix_data
        )
        db.add(matrix)

        db.commit()
        print("Pipeline data successfully seeded!")

    except Exception as e:
        print(f"Error seeding pipeline data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_pipeline()
