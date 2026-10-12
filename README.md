# The Lenny Growth Assistant

A source-grounded AI research and creation workspace engineered for Product Managers, Startup Founders, and Growth Teams. Powered by 60+ verified transcripts and posts from **Lenny's Podcast** and **Lenny's Newsletter** (6,479 indexed chunks).

Built for the **Oogway Forward Deployed Engineer Assessment**.

---

## Key Features

1. **Source-Grounded Transcript Q&A**: Answers product and startup growth questions strictly using evidence from verified podcast and newsletter transcripts.
2. **Traceable Inline Citations**: Every answer includes interactive citation chips `[1]`, `[2]` linking directly to verified excerpts, speakers, episode titles, and original URLs.
3. **Honesty & Limitation Enforcement**: Explicitly acknowledges when evidence is missing in the archive instead of hallucinating.
4. **Ship 30 for 30 Essay Skill**: Synthesizes practitioner wisdom into structured, ~1,250-word editorial essays with clear hooks, tension analysis, skimmable pillars, and 60-second takeaways.
5. **Interactive Artifact Generation & Sandboxed Viewer**: Generates standalone Markdown canvases and complete HTML/CSS tools previewed inside a secure, sandboxed iframe (`sandbox="allow-scripts"` without `allow-same-origin`).
6. **Local & Cloud Inference Switching**: Runs locally with zero-configuration **Ollama** (`qwen2.5:0.5b`) with seamless switching to cloud providers (Google Gemini, Claude, OpenAI).
7. **PostgreSQL Conversation Persistence**: Persistent independent sessions, message history, timestamps, and cascade deletion.
8. **Distinctive Editorial Workspace**: Dark-first, high-density interface inspired by Linear and Claude Workspace.

---

## Architecture Summary

```
                      +-----------------------------------+
                      |   React + TypeScript Frontend     |
                      |   (Vite, Tailwind-free, Port 5173)|
                      +-----------------+-----------------+
                                        | REST API
                      +-----------------v-----------------+
                      |    FastAPI Python Backend         |
                      |   (Pydantic, Uvicorn, Port 8000)  |
                      +---+-------------+---------------+--+
                          |             |               |
       +------------------v--+   +------v-------+   +---v-------------+
       | PostgreSQL 18       |   | Ollama Local |   | Cloud Providers |
       | (Sessions, Messages,|   | Inference    |   | (Gemini, Claude,|
       |  Chunks, Artifacts) |   | (Port 11434) |   |  OpenAI)        |
       +---------------------+   +--------------+   +-----------------+
```

- **Frontend**: React 18, TypeScript, Vite, Vanilla CSS design system, Lucide icons, Marked + DOMPurify.
- **Backend**: FastAPI, Pydantic v2, SQLAlchemy 2.0, Psycopg2, HTTPX.
- **Database**: PostgreSQL (`lenny_growth_db`) storing conversations, messages, artifacts, and knowledge chunks.
- **Knowledge Base**: 60 documents, 6,479 chunks with 256-dimensional semantic projection vectors and lexical matching.

---

## Quick Start & Local Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- PostgreSQL running on `localhost:5432`
- Ollama installed (optional for local inference; cloud models also supported)

### 1. Clone & Setup Environment
```bash
git clone <repo-url> oogway
cd oogway

# Copy environment file
cp .env.example .env
```

Review `.env`:
```env
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/lenny_growth_db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:0.5b
DEFAULT_PROVIDER=local
CLOUD_PROVIDER=gemini
GEMINI_API_KEY=your_key_here  # Optional
```

### 2. Backend Setup
```bash
# Install Python dependencies
pip install -r backend/requirements.txt

# Run initial ingestion (automatically runs on startup if DB is empty)
python -c "from backend.app.db.session import SessionLocal; from backend.app.services.ingestion_service import IngestionService; db = SessionLocal(); IngestionService.ingest_all(db); db.close()"

# Start FastAPI backend server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Backend will be active at: `http://127.0.0.1:8000` (Docs at `/docs`, Health check at `/health`).

### 3. Frontend Setup
In a new terminal window:
```bash
cd frontend
npm install
npm run dev
```

Frontend will open at: `http://localhost:5173`.

### 4. Local Model Setup (Ollama)
```bash
# Start Ollama service
ollama serve

# Pull the lightweight configured local model (397 MB)
ollama pull qwen2.5:0.5b
```

---

## Running with Docker Compose

A complete multi-container workflow is provided:

```bash
docker-compose up --build
```
This launches:
- `lenny_postgres`: PostgreSQL container on port 5432
- `lenny_backend`: FastAPI backend on port 8000
- `lenny_frontend`: Nginx-served React SPA on port 3000

---

## Automated Test Suite

Run the full automated test suite:
```bash
python -m pytest backend/tests/ -v
```

Tests cover:
- Health and diagnostic endpoint checks (`test_api_validation.py`)
- Session creation and strict cross-session isolation (`test_api_validation.py`)
- Semantic embedding computation & vector normalization (`test_retrieval_rag.py`)
- Source-grounded transcript retrieval accuracy (`test_retrieval_rag.py`)
- Out-of-domain query abstention & limitation enforcement (`test_retrieval_rag.py`)
- Agent intent routing across skills (`test_agents_routing.py`)
- Artifact creation, PostgreSQL persistence & iframe sandbox rules (`test_artifacts_security.py`)

---

## Project Structure

```
oogway/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entrypoint
│   │   ├── core/                    # Config, logging, error handlers
│   │   ├── db/                      # SQLAlchemy models & session factory
│   │   ├── schemas/                 # Pydantic request/response schemas
│   │   ├── services/                # Session, Ingestion, Retrieval, Artifact services
│   │   ├── agents/                  # Orchestrator, Skills, Provider adapters
│   │   │   ├── orchestrator.py      # Skill intent classification & execution
│   │   │   ├── skills/              # Knowledge QA, Ship 30 Writer, Artifact Generator
│   │   │   └── providers/           # Base, Ollama local, Cloud (Gemini/Claude/OpenAI)
│   │   └── api/v1/                  # Versioned API routes (health, models, sessions, chat)
│   ├── tests/                       # Automated test suite
│   └── requirements.txt             # Python backend dependencies
├── frontend/
│   ├── src/
│   │   ├── App.tsx                  # Main workspace coordinator
│   │   ├── index.css                # Editorial dark design system
│   │   ├── types/                   # TypeScript interfaces
│   │   ├── services/                # API client
│   │   └── components/
│   │       ├── layout/              # Collapsible Sidebar
│   │       ├── chat/                # Composer, MessageItem, EmptyState
│   │       ├── artifacts/           # Sandboxed ArtifactViewer (Preview + Source)
│   │       ├── sources/             # EvidenceModal for deep transcript inspection
│   │       └── settings/            # Workspace Settings & Diagnostics
│   ├── package.json
│   └── vite.config.ts
├── data/
│   └── transcripts/                 # 60 Markdown transcripts & index.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
├── PRD.md                           # Product Requirements Document
├── design.md                        # Design System & UI Specification
├── architecture.md                  # System Architecture & Technical Contracts
└── tests/test_plan.md               # Quality Assurance & Acceptance Checklist
```

---

## Troubleshooting & FAQ

1. **Ollama connection failed**:
   - Ensure `ollama serve` is running. You can check status anytime in **Workspace Settings** in the app UI.
   - Verify that `qwen2.5:0.5b` is downloaded (`ollama list`).
2. **PostgreSQL connection refused**:
   - Check that PostgreSQL is running on port 5432 and database `lenny_growth_db` exists.
   - The application includes resilience logic: if PostgreSQL is temporarily unreachable, it safely logs a diagnostic warning.
3. **Using Cloud Models**:
   - Set `DEFAULT_PROVIDER=cloud` and configure `GEMINI_API_KEY` (or `ANTHROPIC_API_KEY` / `OPENAI_API_KEY`) in `.env`.
   - Never commit `.env` containing sensitive keys.
