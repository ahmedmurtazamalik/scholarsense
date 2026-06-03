# ScholarSense — AI-Powered Systematic Literature Review (SLR) Platform

ScholarSense is a production-grade, end-to-end web application designed to automate and streamline the process of **Systematic Literature Reviews (SLRs)**. It leverages advanced Retrieval-Augmented Generation (RAG), section classification, semantic clustering, and LLM-guided evaluation to process academic papers and synthesize insights.

---

## Key Features & RAG Pipeline

The system is structured as a multi-stage SLR pipeline:

1. **Phase 0: Document Processing (Ingestion & Parsing)**
   - Upload and parse academic PDFs with metadata extraction (authors, year, abstract).
   - Dynamic document chunking using token-based classifiers and custom section mapping (introduction, methodology, results, etc.).
   - Local vector store indexing for fast semantic retrieval.
2. **Phase 1: Coarse Programmatic Screening**
   - Apply user-defined filtering criteria (publication years, study types, required/excluded keywords).
   - Fast coarse screening to filter out irrelevant papers before running expensive LLM calls.
3. **Phase 2: Deep LLM-Guided Evaluation**
   - Query papers using custom Research Questions (RQs) with weighted scores.
   - Strict RAG-based context retrieval from targeted sections.
   - Extraction of answers, confidence scores, and source quotes for full verification and provenance.
4. **Phase 3: Synthesis & Analytical Dashboard**
   - Automatically compile structured comparison matrices of papers across extracted schemas.
   - Run semantic clustering to discover common research themes and paradigms.
   - Detect contradictory or conflicting findings across different papers on similar topics.
   - Sync and import papers directly from your **Zotero** collection.

---

## Architectural Layout & Core Modules

The repository is divided into a **FastAPI** backend and a **Next.js** frontend.

### Backend App Structure (`backend/app/`)

| Component | File / Path | Core Logic & Responsibilities |
| :--- | :--- | :--- |
| **Models** | [user.py](file:///e:/scholarsense/backend/app/models/user.py) | User account management, multi-tenancy configurations, and Zotero integrations. |
| | [paper.py](file:///e:/scholarsense/backend/app/models/paper.py) | Ingested paper representation, state management (processing, included, excluded). |
| | [chunk.py](file:///e:/scholarsense/backend/app/models/chunk.py) | Extracted PDF text chunks, section mappings, and vector embeddings. |
| | [screening.py](file:///e:/scholarsense/backend/app/models/screening.py) | Screening criteria blueprints and filter evaluations. |
| | [evaluation.py](file:///e:/scholarsense/backend/app/models/evaluation.py) | Weighted Research Questions (RQs) and deep evaluation outcomes. |
| | [extraction.py](file:///e:/scholarsense/backend/app/models/extraction.py) | Schema definitions and fine-grained values extracted from papers. |
| | [matrix.py](file:///e:/scholarsense/backend/app/models/matrix.py) | Cross-paper comparison matrices mapping schemas to papers. |
| | [audit_log.py](file:///e:/scholarsense/backend/app/models/audit_log.py) | Full transparency logs detailing all prompts, models, and LLM completions. |
| | [zotero_mapping.py](file:///e:/scholarsense/backend/app/models/zotero_mapping.py) | Sync mappings mapping Zotero item keys to internal paper records. |
| **Routers** | [auth.py](file:///e:/scholarsense/backend/app/routers/auth.py) | Registration, login, and secure JWT-based session checks. |
| | [papers.py](file:///e:/scholarsense/backend/app/routers/papers.py) | PDF uploads, bulk processing, state overrides, and chunk queries. |
| | [screening.py](file:///e:/scholarsense/backend/app/routers/screening.py) | CRUD for screening criteria and batch screening invocation. |
| | [evaluation.py](file:///e:/scholarsense/backend/app/routers/evaluation.py) | Custom Research Questions CRUD and batch RAG evaluation. |
| | [synthesis.py](file:///e:/scholarsense/backend/app/routers/synthesis.py) | Aggregation, limitations summaries, year trends, and methodology distributions. |
| | [extraction.py](file:///e:/scholarsense/backend/app/routers/extraction.py) | Schema builder and fine-grained value correction endpoints (backward compatibility). |
| | [matrix.py](file:///e:/scholarsense/backend/app/routers/matrix.py) | Endpoints to dynamically compile and retrieve comparative tables. |
| | [zotero.py](file:///e:/scholarsense/backend/app/routers/zotero.py) | Key verification and batch library sync. |
| | [analytics.py](file:///e:/scholarsense/backend/app/routers/analytics.py) | Distribution stats (legacy analytics). |
| | [clusters.py](file:///e:/scholarsense/backend/app/routers/clusters.py) | Semantic clustering triggers. |
| | [conflicts.py](file:///e:/scholarsense/backend/app/routers/conflicts.py) | Endpoints to detect and query contradictions across evaluations. |
| **Services** | [pdf_parser.py](file:///e:/scholarsense/backend/app/services/pdf_parser.py) | PDF reading, raw text extraction, and page boundaries parsing. |
| | [chunker.py](file:///e:/scholarsense/backend/app/services/chunker.py) | Token-aware overlapping text chunking. |
| | [section_classifier.py](file:///e:/scholarsense/backend/app/services/section_classifier.py) | Regex heading detection with LLM-fallback heuristic for chunk placement. |
| | [vector_store.py](file:///e:/scholarsense/backend/app/services/vector_store.py) | ChromaDB embedding indexing and cosine similarity retrieval. |
| | [llm_client.py](file:///e:/scholarsense/backend/app/services/llm_client.py) | Structured LLM prompt building and client interactions. |
| | [screening_service.py](file:///e:/scholarsense/backend/app/services/screening_service.py) | Rules engine evaluating papers against year and keyword filters. |
| | [evaluation_engine.py](file:///e:/scholarsense/backend/app/services/evaluation_engine.py) | Targeted section retrieval, RAG evaluation, and provenance formatting. |
| | [synthesis_service.py](file:///e:/scholarsense/backend/app/services/synthesis_service.py) | Compiles matrix summaries, limitations, trends, and clusters. |
| | [clustering_service.py](file:///e:/scholarsense/backend/app/services/clustering_service.py) | Semantic embedding clustering using K-Means with optional FAISS acceleration. |
| | [conflict_detector.py](file:///e:/scholarsense/backend/app/services/conflict_detector.py) | Evaluates answer contradictions using semantic comparison. |
| | [zotero_service.py](file:///e:/scholarsense/backend/app/services/zotero_service.py) | Pulls collection lists and synchronizes paper downloads from Zotero API. |
| **Schemas** | [Pydantic Schemas](file:///e:/scholarsense/backend/app/schemas/) | Input/output models mapping FastAPI endpoints cleanly to DB records. |
| **Utils** | [provenance.py](file:///e:/scholarsense/backend/app/utils/provenance.py) | Character matching and fuzzy highlighting markers for text citations. |
| | [auth.py](file:///e:/scholarsense/backend/app/utils/auth.py) | Hash matching and JWT creation. |

### Frontend App Structure (`frontend/src/`)

- **Pages (`src/app/`)**
  - `/` (Dashboard) — Overview statistics, quick action shortcuts, and pipeline health.
  - `/papers` — Document management panel (drag-and-drop upload, processing state viewer).
  - `/screening` — Coarse programmatic filter configurations and quick inclusion/exclusion tables.
  - `/evaluation` — Evaluation workspace. Run research questions, rank papers, and click results to trace visual quotes.
  - `/synthesis` — Comparative synthesis analytics (year trends, limitations, methodology charts).
  - `/matrix` — Dynamic grid showing extraction schemas mapping fields across papers with confidence charts.
  - `/clusters` — Semantic paper clustering cards grouping papers into common topics.
  - `/conflicts` — Contradiction analyzer indicating which papers hold opposite findings on identical topics.
  - `/zotero` — Connection page to register keys and select collections.
  - `/login` — Secure JWT login/registration screen.
- **Shared Components (`src/components/`)**
  - `Sidebar.tsx` — Responsive layout sidebar defining the step-by-step pipeline.
  - `AuthContext.tsx` — Handles JWT logins, local storage, and page guarding.

---

## Environment Variables Configuration

The backend supports configuration using a `.env` file inside the `backend/` directory. If a variable is not specified, safe defaults are loaded from [config.py](file:///e:/scholarsense/backend/app/config.py).

Create a `backend/.env` file with:

```env
# Groq API Key (REQUIRED for LLM RAG pipelines)
GROQ_API_KEY=your_groq_api_key_here

# Database (Defaults to SQLite for a quick zero-config start)
# DATABASE_URL=sqlite:///./slr_db.sqlite
# Or configure external PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost:5432/scholarsense

# LLM Providers & Models
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Security & JWT Tokens
JWT_SECRET=your-custom-jwt-signing-secret
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

> [!IMPORTANT]
> A valid `GROQ_API_KEY` is required to run the automated LLM evaluation, schema extraction, and conflict detection services.

---

## How to Run Locally

### Prerequisites

- **Python** 3.10+
- **Node.js** 20+
- **npm** or equivalent packager

### 1. Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   # Create environment
   python -m venv venv

   # Activate on Windows
   venv\Scripts\activate

   # Activate on macOS/Linux
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database schema and default admin user:
   ```bash
   python init_db.py
   ```
5. *(Optional)* Seed complete sample literature review data (Attention is All You Need & BERT):
   ```bash
   python seed_test_pipeline.py
   ```
6. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
   - Interactive docs will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Install the packages:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to: [http://localhost:3000](http://localhost:3000)

### 3. Log In

Use the default admin credentials seeded in step 4:
- **Email:** `default@slr.local`
- **Password:** `admin123`

---

## API Summary

All endpoints are prefixed with `/api`.

| Router Group | Prefix | Key Endpoints | Description |
| :--- | :--- | :--- | :--- |
| **Auth** | `/api/auth` | `POST /register`, `POST /login`, `GET /me` | Session management. |
| **Papers** | `/api/papers` | `GET /`, `POST /upload`, `POST /upload/bulk`, `POST /{id}/process`, `GET /{id}/chunks`, `DELETE /{id}` | Ingest, chunk, embed, and query research papers. |
| **Screening** | `/api/screening` | `POST /criteria`, `GET /criteria`, `POST /run`, `GET /results` | Fast rule-based inclusion/exclusion filters. |
| **Evaluation** | `/api/evaluation` | `POST /questions`, `GET /questions`, `POST /run`, `GET /results/{paper_id}`, `GET /summary` | Deep, section-aware RAG evaluations. |
| **Synthesis** | `/api/synthesis` | `GET /overview`, `POST /aggregate`, `POST /methods-distribution`, `POST /year-trends`, `POST /limitations`, `POST /patterns` | Aggregation matrix and review insights. |
| **Matrix** | `/api/matrix` | `POST /build`, `GET /{id}` | Compile comparative paper matrices. |
| **Zotero** | `/api/zotero` | `POST /connect`, `GET /collections`, `POST /sync` | Sync and download papers from Zotero collections. |
| **Conflicts** | `/api/conflicts` | `POST /detect`, `GET /` | Identify contradictions across evaluations. |
| **Clusters** | `/api/clusters` | `POST /generate`, `GET /` | Legacy semantic clustering endpoints. |
| **Analytics** | `/api/analytics` | `GET /methods-frequency`, `GET /year-trends` | Legacy stats charts. |
