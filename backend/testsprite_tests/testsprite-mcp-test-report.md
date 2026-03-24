# TestSprite MCP Test Report

---

## 1️⃣ Document Metadata

| Field | Value |
|---|---|
| **Project Name** | storm44- (backend) |
| **Date** | 2026-03-24 |
| **Branch** | database_creation |
| **Prepared by** | TestSprite AI + Claude Code |
| **Backend URL** | http://127.0.0.1:8000 |
| **Database** | PostgreSQL 18 @ 127.0.0.1:5432/storm44 (pgvector enabled) |

---

## 2️⃣ Requirement Validation Summary

### REQ-01: Service Availability

| Test ID | Title | Status | Notes |
|---|---|---|---|
| TC001 | GET /api/v1/health returns `{"status":"ok"}` | ✅ PASSED | 200 response with correct JSON body |

**Result:** Health check is fully functional. DB pool initializes correctly on startup via `asynccontextmanager` lifespan.

---

### REQ-02: RAG Question Answering

| Test ID | Title | Status | Notes |
|---|---|---|---|
| TC002 | POST /api/v1/ask returns RAG answer with citations | ❌ FAILED | 500 — embeddings.npy not found at expected path |

**Root Cause:** `machine_learning/ingest_pipeline/store/retrieve.py` resolved the embeddings directory to `machine_learning/artifacts/embeddings/` but actual data lives at `machine_learning/data/embeddings/`. Same mismatch for chunks directory.

**Fix Applied:** Updated `retrieve.py` — changed `REPO_ROOT / "artifacts"` → `REPO_ROOT / "data"` for both `EMB_DIR` and `CHUNKS_DIR`.

---

## 3️⃣ Coverage & Matching Metrics

- **2 of 2** tests executed
- **1 of 2** tests passed (50%)
- **1 of 2** tests failed (50%)

| Requirement | Total Tests | ✅ Passed | ❌ Failed |
|---|---|---|---|
| REQ-01: Service Availability | 1 | 1 | 0 |
| REQ-02: RAG Question Answering | 1 | 0 | 1 |
| **Total** | **2** | **1** | **1** |

---

## 4️⃣ Key Gaps / Risks

### Fixed in this session
| Issue | Severity | Fix |
|---|---|---|
| `retrieve.py` loads from `artifacts/` instead of `data/` | **Critical** | Changed `REPO_ROOT / "artifacts"` → `REPO_ROOT / "data"` in retrieve.py |

### Remaining gaps (not yet implemented)

| Gap | Severity | Detail |
|---|---|---|
| No `/ingest` HTTP endpoint | High | `crud.ingest_source()` exists but is not exposed via any API route. Ingestion only runs via the standalone ML pipeline script. |
| No `/query` HTTP endpoint | High | `crud.retrieve_similar_chunks()` exists but is not wired to any route. The `/ask` endpoint bypasses the DB and uses file-based retrieval instead. |
| No `/flashcards/generate` or `/quiz/generate` endpoints | High | CRUD functions in `crud.py` are complete but have no API surface. |
| `/ask` endpoint ignores `source_ids` | Medium | `answer_question_structured()` uses file-based retrieval; the `source_ids` field in `AskRequest` has no effect. |
| No authentication on any endpoint | Medium | All routes are publicly accessible — no auth middleware configured. |
| `source_ids` filter not plumbed to pgvector DAL | Medium | `retrieve_similar_chunks()` accepts `source_ids` but the `/ask` route never calls it. |

### Next recommended actions
1. Restart backend and re-run TC002 to confirm the `artifacts/` → `data/` path fix resolves the 500.
2. Wire `/ask` to `crud.retrieve_similar_chunks()` instead of file-based `top_k()`, so `source_ids` scoping and pgvector are actually used.
3. Add `/ingest`, `/query`, `/flashcards/generate`, `/quiz/generate` routes to complete the backend API surface.
