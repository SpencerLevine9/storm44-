# Storm44 — Comprehensive Project Scope
> Last Updated: March 2026 | Status: MVP In Development | Sprint: Active

---

## Table of Contents
1. [Product Identity & Problem Statement](#1-product-identity--problem-statement)
2. [Team & Ownership Map](#2-team--ownership-map)
3. [System Architecture](#3-system-architecture)
4. [Feature Specification](#4-feature-specification)
5. [Sprint & Delivery Plan](#5-sprint--delivery-plan)
6. [Developer Onboarding & Operational Context](#6-developer-onboarding--operational-context)
7. [Appendix: Glossary](#appendix-glossary)

---

## 1. Product Identity & Problem Statement

### What Is Storm44?
Storm44 is a **free, AI-powered study workspace** that converts a student's own materials — YouTube links and PDF documents — into actionable study assets: organized notes, flashcards, and practice quizzes. An integrated AI Tutor lets users ask questions directly against their uploaded content, with every response traceable to exact source excerpts.

### Problem Statement (SCQ Format)

**Situation**
Learners rely on videos and PDFs but spend significant time manually creating study materials instead of actually practicing.

**Complication**
Existing tools either require manual deck building or produce uncited, occasionally inaccurate AI outputs — reducing trust and wasting effort. Most platforms are also locked behind paywalls, making them inaccessible to a large portion of students.

**Question**
How can we give learners a fast, trustworthy, and free way to turn their own materials into effective practice content with traceable sources?

**Answer**
By building Storm44: a free AI-powered study tool that automatically converts YouTube videos and PDFs into organized notes, flashcards, and quizzes. Its integrated AI Tutor allows users to engage directly with their materials to clarify concepts and reinforce understanding — making learning faster, smarter, and more personalized.

### Intended Audience
- **Primary:** College students, especially deadline-driven cramming scenarios
- **Secondary:** Self-learners and professionals studying from mixed-format materials

### What Success Looks Like at MVP
- A user can upload a PDF or paste a YouTube link and receive generated flashcards and a quiz within a reasonable response window
- The AI Tutor answers questions about uploaded content and returns clickable citations that map back to the exact source passage
- The 3-panel workspace is functional, responsive on desktop, and does not freeze under large source files or long chat threads
- All core flows are instrumented for analytics: `source_added`, `chat_sent`, `flashcards_generated`, `quiz_generated`

### Explicit Out of Scope (MVP)
- Payments, subscriptions, or any monetization layer
- Offline support
- Multi-tenant admin or institutional features
- Collaborative editing between users
- Native mobile applications
- Handwritten note ingestion (OCR)
- Learning games / gamification (deferred post-MVP)
- Fine-tuned or custom model training

---

## 2. Team & Ownership Map

### Members & Roles

| Member | Role | Primary Owned Components |
|---|---|---|
| Spencer | ML Lead / Project Lead | Embedding pipeline, model selection, RAG retrieval logic, project coordination |
| Jason | Backend Framework Engineer | FastAPI application structure, route scaffolding, middleware, request/response contracts, API gateway layer |
| Marcus | RAG & Database Engineer | PostgreSQL + pgvector schema design, vector index strategy, Azure DB infrastructure, chunk storage, citation metadata, query pipeline |
| Ethan | Frontend Engineer | React component architecture, state management, UI/UX implementation, study tools UI |

### Role Boundary: Jason vs. Marcus
Because Jason and Marcus share the backend layer, their boundary is explicitly defined to prevent overlap and conflicts:

| Concern | Owner |
|---|---|
| FastAPI app structure, routers, middleware, dependency injection | Jason |
| Pydantic request/response models and API contracts | Jason (Marcus reviews for DB impact) |
| PostgreSQL schema design and migrations | Marcus |
| pgvector index configuration (HNSW / IVFFlat) | Marcus |
| Azure Database for PostgreSQL provisioning and connection management | Marcus |
| Raw SQL and ORM queries touching `chunks` / `embeddings` tables | Marcus |
| Ingestion endpoint logic (calling the ML pipeline) | Jason builds the endpoint; Marcus owns the storage layer it writes to |
| RAG query endpoint logic (similarity search + reranking) | Marcus owns the DB layer; Jason owns the FastAPI wiring |

Marcus brings direct experience with production database systems from his IT/IS role at city government, including SQL schema design, query optimization, and data migration — applied here to the vector database layer hosted on Azure.

### Cross-Cutting Decision Authority
- **Schema changes or vector index strategy:** Marcus decides; team is notified before implementation
- **API contract changes** (new routes, request/response shape): Jason proposes; Marcus reviews for DB compatibility; Spencer reviews for ML pipeline compatibility
- **Model or embedding changes** (dimension, provider): Spencer leads; Marcus must approve — dimension changes require a schema migration and re-ingestion of all existing vectors
- **Azure infrastructure changes** (connection strings, server tier, firewall rules): Marcus owns; Jason updates `.env` references accordingly
- **UI changes that alter API request shape:** Ethan proposes; Jason implements the backend change; Marcus reviews if DB queries are affected

### Contribution Matrix

| Sprint | Focus | Spencer | Jason | Marcus | Ethan |
|---|---|---|---|---|---|
| 1 | Foundation | ML pipeline scaffold | FastAPI app init, router structure | Azure DB setup, schema v1, pgvector extension enable | UI shell, tokens, routing |
| 2 | Ingestion | PDF/YouTube extraction | Ingest endpoint, file handling | Chunk + embedding storage, source CRUD queries | Sources panel, upload UI |
| 3 | Scope & Chat Base | Embedding + retrieval | Query endpoint wiring, chat route | pgvector similarity search, context scoping queries | Chat panel, scope selector |
| 4 | Citations & Advanced UI | Citation mapping logic | Citation response contracts | Citation chunk metadata, chunk lookup queries | Resizable panels, citation UI |
| 5 | Flashcards | Flashcard generation prompt | Flashcard CRUD endpoints | Flashcard storage schema, CRUD queries | Flashcard component, study mode |
| 6 | Quizzes | Quiz generation prompt | Quiz CRUD endpoints | Quiz storage schema, CRUD queries | Quiz execution UI, results |
| 7 | Polish | Eval & accuracy review | Integration tests, API hardening | DB performance tuning, index optimization, query benchmarks | A11y, E2E, bug bash |

---

## 3. System Architecture

### 3.1 Stack Summary

| Layer | Technology |
|---|---|
| Frontend | React 19 + Vite 7, React Router v7, Context API, Custom CSS |
| Backend API | Python 3.11+, FastAPI |
| Database | Azure Database for PostgreSQL (Flexible Server) + pgvector extension |
| ML / Ingestion | Python pipeline — PyMuPDF, YouTube Transcript API, embedding model |
| Cloud Infra | Microsoft Azure — PostgreSQL Flexible Server (primary DB host) |
| Design System | Radix UI base components, iOS-inspired design, primary blue `#007AFF` |

### 3.2 High-Level Component Map

```
┌──────────────────────────────────────────────────────────────┐
│                       React Frontend                          │
│    [Left: Sources Panel] [Center: Chat] [Right: Tools]        │
└──────────────────┬───────────────────────────────────────────┘
                   │ HTTP / REST
┌──────────────────▼───────────────────────────────────────────┐
│                     FastAPI Backend                           │
│       /ingest  /query  /flashcards  /quizzes  /sources        │
│                  [Jason: routes + middleware]                  │
└──────────────────┬───────────────────────────────────────────┘
                   │ asyncpg / psycopg2 over SSL
┌──────────────────▼───────────────────────────────────────────┐
│       Azure Database for PostgreSQL — Flexible Server         │
│   sources | chunks | embeddings | flashcards | quizzes        │
│              [Marcus: schema, indexes, queries]                │
└──────────────────────────────────────────────────────────────┘
                   ▲
┌──────────────────┴───────────────────────────────────────────┐
│               Python ML Ingestion Pipeline                    │
│         Extract → Chunk → Embed → Store vectors               │
│                  [Spencer: ML logic]                           │
└──────────────────────────────────────────────────────────────┘
```

### 3.3 Azure Infrastructure Notes
Owner: **Marcus**

The PostgreSQL database is hosted on **Azure Database for PostgreSQL — Flexible Server**. All team members connect to the shared cloud instance during development — there is no local PostgreSQL requirement.

**Initial provisioning checklist (Marcus):**
```bash
# Enable pgvector on the Azure server before any migrations
az postgres flexible-server parameter set \
  --resource-group <rg> \
  --server-name <server> \
  --name azure.extensions \
  --value VECTOR
```

- **Connection:** All services connect via SSL. `DATABASE_URL` must include `?sslmode=require`
- **Firewall rules:** Every team member's IP must be added via Azure portal (`Settings → Networking`) before they can connect. When a teammate reports a connection failure, check firewall first — it is almost always the firewall, not credentials
- **Server tier (MVP):** Burstable B-series is acceptable for dev and demo; upgrade to General Purpose if sustained concurrent load is needed before final presentation
- **Backups:** Azure automated backups are enabled by default — do not disable; set retention to at least 7 days

### 3.4 Critical Data Flow Narratives

#### Flow 1: Source Ingestion
1. User uploads a PDF or pastes a YouTube URL in the Sources panel
2. Frontend sends `POST /ingest` to FastAPI with the source payload
3. Jason's ingestion route validates the request via Pydantic model and hands off to Spencer's ML pipeline:
   - **PDF:** PyMuPDF extracts raw text and page metadata
   - **YouTube:** `youtube-transcript-api` fetches timestamped transcript
4. Spencer's pipeline chunks the extracted text into overlapping segments
5. Each chunk is passed to the embedding model to produce a vector
6. Marcus's storage layer writes chunk content + metadata to `chunks` and the vector to `embeddings` in Azure PostgreSQL
7. FastAPI returns a success response; frontend updates the Sources panel

#### Flow 2: AI Tutor Query with Citations
1. User selects sources in the Sources panel (defines scope) and sends a message in Chat
2. Frontend sends `POST /query` with: message, selected source IDs, conversation history
3. Jason's query route validates the request and calls Marcus's RAG query function
4. Marcus's layer executes a pgvector cosine similarity search against `embeddings` filtered to the scoped source IDs:
   ```sql
   SELECT c.id, c.content, c.metadata,
          e.embedding <=> $1::vector AS distance
   FROM   embeddings e
   JOIN   chunks c ON c.id = e.chunk_id
   WHERE  c.source_id = ANY($2)
   ORDER  BY distance
   LIMIT  $3;
   ```
5. Top-k chunks are returned and reranked (strategy owned by Spencer)
6. Retrieved chunks + user message + system prompt are assembled and sent to the LLM
7. LLM streams a response back through FastAPI to the frontend
8. Each claim in the response includes a `chunk_id` reference
9. Frontend renders citations as clickable markers; clicking highlights the passage in the Sources panel

#### Flow 3: Study Tool Generation
1. User triggers "Generate Flashcards" or "Generate Quiz" for a selected source
2. Frontend sends `POST /flashcards/generate` or `POST /quizzes/generate` with `source_id`
3. Jason's route calls Marcus's chunk retrieval function for the source
4. Spencer's generation prompt assembles the chunks and sends them to the LLM
5. LLM returns structured JSON (cards or MCQ questions)
6. Marcus's storage layer writes the results to `flashcards` or `quiz_questions` in Azure PostgreSQL
7. FastAPI returns the generated content; frontend renders it in the Study Tools panel

### 3.5 Database Schema
Owner: **Marcus**

**Design principles:**
- All PKs are `UUID` — never serial integers
- All timestamps are `TIMESTAMPTZ` (UTC stored, display converted client-side)
- `JSONB` for variable metadata (page numbers, timestamps, bounding boxes) — avoid adding columns for metadata variations
- Embedding dimension is **locked at provisioning** — changing it requires a full re-ingestion migration and team alignment

```sql
-- Ingested source materials
CREATE TABLE sources (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  type        TEXT        NOT NULL CHECK (type IN ('pdf', 'youtube')),
  title       TEXT,
  url         TEXT,
  file_path   TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  deleted_at  TIMESTAMPTZ           -- soft delete
);

-- Text chunks extracted from sources
CREATE TABLE chunks (
  id           UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id    UUID        NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  chunk_index  INTEGER     NOT NULL,
  content      TEXT        NOT NULL,
  metadata     JSONB,                -- page_number, timestamp_start, timestamp_end, etc.
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Vector embeddings (one per chunk)
CREATE TABLE embeddings (
  id             UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  chunk_id       UUID        NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
  embedding      VECTOR(1536),       -- dimension locked; must match embedding model output
  model_version  TEXT        NOT NULL, -- record which model produced this vector
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- HNSW index for fast approximate nearest-neighbor search
-- Tune m and ef_construction based on dataset size — owned by Marcus
CREATE INDEX ON embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Generated flashcards
CREATE TABLE flashcards (
  id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id          UUID        NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  front              TEXT        NOT NULL,
  back               TEXT        NOT NULL,
  citation_chunk_id  UUID        REFERENCES chunks(id),
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Generated quiz questions
CREATE TABLE quiz_questions (
  id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id          UUID        NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
  question           TEXT        NOT NULL,
  options            JSONB       NOT NULL,  -- array of answer choice strings
  correct_answer     TEXT        NOT NULL,
  explanation        TEXT,
  citation_chunk_id  UUID        REFERENCES chunks(id),
  created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

**Vector Index Strategy**

| Index | Use Case | Tradeoff |
|---|---|---|
| **HNSW** *(chosen for MVP)* | Low-latency queries, concurrent users, demo reliability | Higher memory at build time; faster and more consistent at query time |
| IVFFlat | Very large datasets (millions of vectors) | Requires `ANALYZE` after bulk inserts; slower cold queries |

HNSW is chosen for MVP because query latency is predictable without warm-up — critical for a live capstone demo environment where cold queries would be visible to evaluators.

### 3.6 FastAPI Route Groups

| Route Group | Endpoints | Jason's Responsibility | Marcus's Responsibility |
|---|---|---|---|
| `/sources` | `GET /`, `GET /{id}`, `DELETE /{id}` | Route, Pydantic models, validation | DB queries, soft delete logic |
| `/ingest` | `POST /ingest` | Route, file handling, pipeline handoff | Chunk + embedding write to Azure DB |
| `/query` | `POST /query` | Route, streaming, history handling | pgvector search, chunk retrieval |
| `/flashcards` | `POST /generate`, `GET /{source_id}`, `DELETE /{id}` | Route, generation orchestration | Storage + retrieval queries |
| `/quizzes` | `POST /generate`, `GET /{source_id}`, `DELETE /{id}` | Route, generation orchestration | Storage + retrieval queries |

### 3.7 External Dependencies

| Dependency | Purpose | Notes |
|---|---|---|
| `PyMuPDF (fitz)` | PDF text + page metadata extraction | Pin version in `requirements.txt` |
| `youtube-transcript-api` | YouTube transcript fetching | May be rate-limited; handle failures gracefully with user-facing error |
| Embedding model | Vector generation | TBD by Spencer — model name and dimension must be documented; dimension locks the schema |
| LLM (inference) | AI Tutor responses, study tool generation | TBD — document provider and exact model string |
| `pgvector` | PostgreSQL vector extension | Must be enabled on Azure server before migrations run |
| Azure Database for PostgreSQL | Managed cloud database host | Flexible Server; SSL required on all connections; Marcus owns provisioning |

### 3.8 Known Architectural Tradeoffs

| Decision | Chosen | Alternative | Rationale |
|---|---|---|---|
| Vector store | pgvector on Azure PostgreSQL | Pinecone, Weaviate, Azure AI Search | Single infra dependency; Marcus's production DB background applies directly; no additional service cost |
| DB host | Azure Database for PostgreSQL | Local PostgreSQL, Supabase | Cloud-hosted for shared team access; Azure available via school subscription; managed backups |
| Vector index | HNSW | IVFFlat | Predictable cold-query performance; better demo reliability |
| Backend language | Python + FastAPI | Node.js/Express | Python-native ML ecosystem; Spencer and Marcus both work in Python |
| State management | Context API | Redux / Zustand | Sufficient for MVP; refactor post-MVP if state complexity grows |
| Auth | Deferred (MVP) | Supabase Auth, Azure AD B2C | Speeds up MVP delivery; known limitation — deployment must remain private until auth is added |

---

## 4. Feature Specification

### Feature 1: Source Ingestion

**What it does:** Users add study materials by uploading PDFs or pasting YouTube URLs. Sources appear in the Sources panel with auto-generated titles.

**How it works:** Jason's FastAPI ingest endpoint receives the payload and triggers Spencer's ML pipeline. Marcus's storage layer writes extracted chunks and their vectors to Azure PostgreSQL.

**Acceptance Criteria:**
- PDF upload: text extracted and chunked within 30 seconds for a standard lecture PDF
- YouTube URL: transcript fetched and chunked; gracefully handles unavailable transcripts with a user-facing error
- Source appears in the Sources panel after ingestion completes
- Duplicate source detection prevents the same URL from being ingested twice

**Status:** In Progress (Sprint 2)
**Owners:** Jason (endpoint) | Spencer (pipeline) | Marcus (chunk + vector storage)
**Dependencies:** Azure DB provisioned, pgvector enabled, schema v1 migrated

---

### Feature 2: AI Tutor with Citations

**What it does:** Users send messages in Chat and receive streamed AI responses. Each factual claim includes a citation marker linking to the exact passage in the source material.

**How it works:** Jason's query route calls Marcus's pgvector similarity search, Spencer's reranking logic assembles the RAG prompt, and the LLM streams a response with `chunk_id` references.

**Acceptance Criteria:**
- Responses stream token-by-token with no blocking wait
- Citations are clickable and highlight the referenced passage in the Sources panel
- The AI Tutor only cites content from currently scoped sources
- If no relevant content is found, the Tutor states it clearly rather than hallucinating
- Conversation history is maintained within a session

**Status:** Planned (Sprint 3)
**Owners:** Jason (route + streaming) | Marcus (pgvector query) | Spencer (RAG prompt)
**Dependencies:** Source ingestion complete, embeddings populated in Azure DB

---

### Feature 3: Scope Selection

**What it does:** Users select which sources the AI Tutor and generators operate against, preventing cross-contamination between unrelated subjects.

**How it works:** Selected source IDs are passed from the frontend with every `/query` and generation request. Marcus's DB queries filter the `embeddings` table by `source_id = ANY($scoped_ids)`.

**Acceptance Criteria:**
- Users can select/deselect individual sources; select-all and deselect-all controls available
- Chat panel visually indicates which sources are currently in scope
- Changing scope mid-conversation starts a new context window
- Scoping filters are enforced at the DB query level, not only in application logic

**Status:** Planned (Sprint 3)
**Owners:** Ethan (UI) | Jason (route) | Marcus (query filter)
**Dependencies:** Sources panel CRUD complete

---

### Feature 4: Flashcard Generation & Study Mode

**What it does:** Users generate a flashcard deck from any ingested source. Each card includes a front, back, and citation linking to the source passage it was derived from.

**How it works:** Jason's endpoint retrieves chunks via Marcus's query function, Spencer's generation prompt produces structured JSON cards, Marcus's storage layer writes them to the `flashcards` table in Azure PostgreSQL.

**Acceptance Criteria:**
- Deck generated within 45 seconds for a standard lecture PDF
- Each card includes a `citation_chunk_id` reference
- Users can flip cards, mark known/unknown, and view a session summary
- Users can delete individual cards or regenerate the full deck
- Generated deck persists between sessions (stored in Azure DB)

**Status:** Planned (Sprint 5)
**Owners:** Jason (endpoint) | Marcus (storage + retrieval) | Spencer (generation prompt) | Ethan (UI)
**Dependencies:** Source ingestion complete, `/flashcards` route defined

---

### Feature 5: Quiz Generation

**What it does:** Users generate a multiple-choice quiz from any ingested source. Each question includes answer choices, the correct answer, an explanation, and a citation.

**How it works:** Mirrors the flashcard generation pattern. Spencer's prompt produces JSON quiz objects; Marcus's storage layer writes to `quiz_questions` in Azure PostgreSQL.

**Acceptance Criteria:**
- Well-formed MCQ format with 4 answer choices per question
- Correct answer and explanation are accurate relative to source material
- Each question cites its source chunk
- Users can take the quiz, see results, and review answers with explanations
- Quiz results persist and are viewable after the session ends

**Status:** Planned (Sprint 6)
**Owners:** Jason (endpoint) | Marcus (storage + retrieval) | Spencer (generation prompt) | Ethan (UI)
**Dependencies:** Flashcard generation pattern established

---

### Feature 6: 3-Panel Workspace Layout

**What it does:** The core UI — resizable left (Sources), center (Chat), and right (Study Tools) panels.

**How it works:** React layout with drag handles, localStorage persistence for panel sizes, and bottom-drawer mobile fallback at ≤768px.

**Acceptance Criteria:**
- All three panels are independently resizable via drag handles
- Panel size state persists to localStorage on resize
- On mobile (≤768px), panels convert to bottom sliding drawers
- Preset "Docked Resize Mode" (Chat 1/3, Study Tools 2/3) available
- Layout does not break or freeze with large source files loaded

**Status:** In Progress (Sprint 1)
**Owner:** Ethan
**Dependencies:** None — foundational

---

## 5. Sprint & Delivery Plan

### Sprint Schedule

| Sprint | Focus | Dates | Status |
|---|---|---|---|
| 1 | Foundation: Azure DB setup, schema v1, FastAPI init, UI shell | TBD | Active |
| 2 | Ingestion: ML pipeline, upload UI, chunk + vector storage | TBD | Planned |
| 3 | Scope & Chat Base: pgvector RAG query, context selection, streaming chat | TBD | Planned |
| 4 | Citations & Advanced UI: citation metadata, resizable panels, virtualized threads | TBD | Planned |
| 5 | Flashcards: generation, CRUD, study mode | TBD | Planned |
| 6 | Quizzes: MCQ generation, execution, results | TBD | Planned |
| 7 | Polish: A11y, DB performance tuning, E2E tests, bug bash | TBD | Planned |

### Sprint 7 Prioritization (Risk Flag)
Sprint 7 is dense. Ranked by capstone evaluation impact:

**Committed:**
- Keyboard navigation and ARIA labels on core interactions
- E2E happy-path tests: ingestion → chat → flashcard generation
- Marcus: pgvector HNSW index tuning and query benchmarks before demo day

**Stretch (ship if time allows):**
- Full ARIA conformance audit
- Analytics instrumentation (`source_added`, `chat_sent`, etc.)
- Comprehensive bug bash beyond happy-path flows

### Risk Register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Azure DB firewall blocking team connections | Medium | High | Marcus adds all team IPs during Sprint 1 setup; connection issues default to firewall check first |
| pgvector cold-query latency visible at demo | Low | High | HNSW index; Marcus warms queries before demo; validate index config in Sprint 7 |
| YouTube transcript API rate limits or unavailability | Medium | High | Graceful error handling; test with local transcript fixtures |
| Azure DB tier insufficient for demo load | Low | Medium | Upgrade to General Purpose tier before final demo if B-series shows strain |
| Embedding model dimension change mid-project | Low | High | Lock `EMBEDDING_DIMENSION` in config; any change = migration + re-ingestion + Marcus + Spencer alignment required |
| LLM response latency making generation feel slow | Medium | Medium | Progress indicators in UI; consider async generation with polling |
| Sprint 7 compression — insufficient polish time | High | Medium | Cut stretch items early; A11y + E2E take priority over analytics |
| Auth absence creates data isolation issues | Medium | Low (MVP) | Keep deployment private for capstone; document as known post-MVP requirement |

### Sprint Dependency Graph
```
Sprint 1 (Foundation — Azure DB + schema + FastAPI init + UI shell)
    └─► Sprint 2 (Ingestion — ML pipeline + chunk/vector storage)
            └─► Sprint 3 (Chat + RAG — pgvector search + streaming)
                    └─► Sprint 4 (Citations + Advanced UI)
                            ├─► Sprint 5 (Flashcards)
                            │       └─► Sprint 6 (Quizzes)
                            │               └─► Sprint 7 (Polish)
                            └─► Sprint 7 (Polish)
```

---

## 6. Developer Onboarding & Operational Context

### Prerequisites
- Python 3.11+
- Node.js 20+
- Access to the Azure PostgreSQL instance — request the `DATABASE_URL` from Marcus
- A completed `.env` file (see Environment Variables below)
- Azure CLI installed if you need to manage firewall or server settings

### Local Setup

**1. Clone and configure environment**
```bash
git clone <repo-url>
cd storm44
cp .env.example .env
# Request DATABASE_URL from Marcus
# Request LLM_API_KEY and EMBEDDING_MODEL from Spencer
```

**2. Start the backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**3. Run database migrations**
```bash
# DATABASE_URL in .env must point to Azure with ?sslmode=require
python backend/db/migrate.py
```

**4. Verify your database connection**
```bash
psql "<your DATABASE_URL>"

# Confirm pgvector is enabled
SELECT * FROM pg_extension WHERE extname = 'vector';

# Confirm tables are present
\dt
```

**5. Start ML pipeline (if running locally)**
```bash
cd machine_learning
pip install -r requirements.txt
python pipeline/run.py
```

**6. Start the frontend**
```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:5173
```

> **Connection issues?** The Azure DB firewall requires your IP to be explicitly allowed. Ping Marcus with your IP and he will add it via the Azure portal. This is the cause of ~90% of connection failures.

### Environment Variables

| Variable | Required | Owner | Description |
|---|---|---|---|
| `DATABASE_URL` | ✅ | Marcus | Azure PostgreSQL connection string — must include `?sslmode=require`. Format: `postgresql://user:pass@<server>.postgres.database.azure.com:5432/storm44?sslmode=require` |
| `EMBEDDING_MODEL` | ✅ | Spencer | Embedding model identifier used for vector generation |
| `EMBEDDING_DIMENSION` | ✅ | Spencer → Marcus | Vector dimension — must exactly match the `VECTOR()` size in the schema |
| `LLM_PROVIDER` | ✅ | Spencer | LLM provider identifier (e.g. `openai`, `anthropic`) |
| `LLM_MODEL` | ✅ | Spencer | Exact model string for AI Tutor and generation |
| `LLM_API_KEY` | ✅ | Spencer | API key for LLM provider |
| `YOUTUBE_API_KEY` | ⚠️ Optional | Spencer | Required for YouTube metadata enrichment; transcript fetch may work without it |
| `VITE_API_BASE_URL` | ✅ (frontend) | Jason | Backend base URL for frontend API calls e.g. `http://localhost:8000` |

### Running Tests

```bash
# Backend unit + integration tests
cd backend
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=term-missing

# Frontend
cd frontend
npm run test
```

**Coverage expectation:** Ingestion and RAG query routes must maintain ≥ 80% line coverage. PRs that reduce coverage on these paths are blocked from merging.

### Branching & PR Conventions
- `main` — stable, demo-ready at all times; no direct commits
- `dev` — integration branch; all feature PRs merge here first
- Feature branches: `feature/<sprint-number>/<short-description>` e.g. `feature/2/pdf-ingestion`
- PRs require at least one reviewer approval before merging to `dev`
- CI tests must pass before merge — no exceptions

### CLAUDE.md / Agent Rules
A `CLAUDE.md` file at the repo root governs how AI coding agents (Claude Code, Cursor) interact with this codebase.

**Database rules — owned by Marcus:**
- Always use `UUID` as primary key type — never `SERIAL` or `INTEGER`
- All timestamps must be `TIMESTAMPTZ` — never `TIMESTAMP`
- pgvector distance operator must be explicit: `<=>` for cosine similarity, `<->` for L2 distance
- Never modify or delete existing migration files — always create a new migration
- Embedding dimension is locked — never change `VECTOR()` size without a new migration file and explicit Marcus + Spencer approval
- `DATABASE_URL` must include `?sslmode=require` for Azure — never strip this parameter

**Backend rules — owned by Jason:**
- All FastAPI endpoints must have Pydantic request and response models — no bare `dict` returns
- All new routes must have a corresponding pytest test before the PR is opened
- Raw SQL and ORM query logic lives in Marcus's database module — routes call functions, they do not write inline SQL

**General:**
- Never commit `.env` or any file containing credentials or API keys
- Run `pytest tests/` before opening a PR — do not open PRs with failing tests

---

## Appendix: Glossary

| Term | Definition |
|---|---|
| **RAG** | Retrieval-Augmented Generation — retrieving relevant chunks from a vector store to ground an LLM prompt before generating a response |
| **Chunk** | A fixed-size overlapping segment of extracted source text; the atomic unit of retrieval in the RAG pipeline |
| **Embedding** | A numerical vector representing a text chunk, enabling semantic similarity search |
| **pgvector** | A PostgreSQL extension that adds vector column types and similarity search operators (`<=>`, `<->`) |
| **HNSW** | Hierarchical Navigable Small World — a vector index algorithm optimized for fast approximate nearest-neighbor queries at query time |
| **IVFFlat** | Inverted File Flat — an alternative vector index better suited for very large datasets; requires warm-up after bulk inserts |
| **Citation** | A `chunk_id` reference returned by the AI Tutor that maps a response claim to a specific passage in the source material |
| **Scope** | The user-selected set of sources the AI Tutor and generators are restricted to operate against |
| **Azure Flexible Server** | The Azure-managed PostgreSQL service tier hosting Storm44's database |
| **Cosine similarity (`<=>`)** | The pgvector operator measuring directional similarity between vectors — used for semantic search in this project |
