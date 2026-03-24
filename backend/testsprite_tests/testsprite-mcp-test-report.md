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
| **Database** | PostgreSQL 18 @ 127.0.0.1:5432/storm44 (pgvector enabled, HNSW index) |

---

## 2️⃣ Requirement Validation Summary

### REQ-01: Service Availability & Readiness

| Test ID | Title | Status | Notes |
|---|---|---|---|
| TC001 | GET /api/v1/health returns `{"status":"ok"}` | ✅ PASSED | 200 response; health check now performs `SELECT 1` via DB pool to verify full readiness |

**Result:** Health endpoint is a true readiness check — verifies both process liveness and DB pool connectivity.

---

### REQ-02: RAG Question Answering via pgvector

| Test ID | Title | Status | Notes |
|---|---|---|---|
| TC002 | POST /api/v1/ask returns RAG answer with citations | ✅ PASSED | 200 response with non-empty answer and 3 populated citations |

**Result:** Full RAG pipeline verified end-to-end:
- Query embedding via `sentence-transformers/all-MiniLM-L6-v2`
- pgvector cosine similarity search scoped to `source_ids` via `MATERIALIZED CTE`
- GPT-4o-mini answer generation
- Citations with `source_id`, `chunk_id`, `snippet` (null fields excluded from response)

---

## 3️⃣ Coverage & Matching Metrics

- **2 of 2** tests executed
- **2 of 2** tests passed (100%)

| Requirement | Total Tests | ✅ Passed | ❌ Failed |
|---|---|---|---|
| REQ-01: Service Availability | 1 | 1 | 0 |
| REQ-02: RAG Question Answering | 1 | 1 | 0 |
| **Total** | **2** | **2** | **0** |

---

## 4️⃣ Key Gaps / Risks

### Issues fixed during this session

| Issue | Fix Applied |
|---|---|
| `retrieve.py` looked in `artifacts/` instead of `data/` for embeddings | Changed path constants to `data/embeddings` and `data/chunks` |
| HNSW index returned global top-k before applying `source_id` WHERE filter — 0 results | Used `WITH filtered AS MATERIALIZED (...)` CTE to force filter-first execution |
| Scientific notation in vector literal (`1.2e-5`) rejected by pgvector | Used `:.8f` fixed-point formatting for all vector components |
| `url: null` included in citation JSON, test expected string or absent field | Added `response_model_exclude_none=True` to `/ask` route |
| `/ask` called file-based `top_k()` — `source_ids` was ignored | Rewrote endpoint to use `retrieve_similar_chunks()` via pgvector DAL |

### Remaining gaps (outside current scope)

| Gap | Severity | Detail |
|---|---|---|
| No `/ingest` HTTP endpoint | High | `crud.ingest_source()` is complete but not exposed via API — ingestion runs as a standalone ML script |
| No `/flashcards/generate` or `/quiz/generate` endpoints | High | `crud.save_flashcards()` and `crud.save_quiz_questions()` are complete but unwired |
| No `/sources` endpoint | Medium | Frontend cannot list available sources to populate `source_ids`; test had to hardcode a UUID |
| No authentication on any endpoint | Medium | All routes are publicly accessible |
| SentenceTransformer model loads on first request (cold start ~3s) | Low | Model is loaded per-request from `embed_query_local()`; could be cached at startup |
