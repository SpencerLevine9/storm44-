# Test Suite Report — TC009–TC017
**Date:** 2026-05-05  
**Backend:** FastAPI + asyncpg + pgvector @ http://localhost:8000  
**Result: 9/9 PASS**

---

## 1. Summary Table

| ID | Name | Category | Result |
|----|------|----------|--------|
| TC009 | Temp directory writable for PDF processing | Config | PASS |
| TC010 | Database pgvector extension installed | Config | PASS |
| TC011 | Embedding model returns correct dimension (384) | Config | PASS |
| TC012 | PDF upload populates source, chunk, embedding tables | Verification | PASS |
| TC013 | YouTube upload populates all tables (incl. video_segment) | Verification | PASS |
| TC014 | Invalid YouTube URLs return 400, no DB rows | Verification | PASS |
| TC015 | PDF delete removes all related DB rows | Verification | PASS |
| TC016 | PDF retrieval accuracy via unique fact (gallium) | Validation | PASS |
| TC017 | YouTube retrieval returns answer + citations + timestamps | Validation | PASS |

---

## 2. Bugs Found and Fixed During Run

### Bug 1 — Missing `user_account` seed row
**Symptom:** TC011/TC012 returned 500: `insert or update on table "source" violates foreign key constraint "source_user_id_fkey"`.  
**Root cause:** The hardcoded MVP `USER_ID = 00000000-0000-0000-0000-000000000001` did not exist in the `user_account` table.  
**Fix:** Inserted the seed row directly:
```sql
INSERT INTO user_account (id, username, password_hash)
VALUES ('00000000-0000-0000-0000-000000000001', 'mvp_user', 'placeholder');
```

### Bug 2 — `youtube-transcript-api` 1.x API change
**Symptom:** TC013/TC017 returned 400: "Could not fetch transcript."  
**Root cause:** `youtube-transcript-api` 1.x removed the `YouTubeTranscriptApi.get_transcript()` class method. The new API requires an instance: `YouTubeTranscriptApi().fetch(video_id)`. Segment objects are now typed snippets with `.text`, `.start`, `.duration` attributes rather than plain dicts.  
**Fix:** Updated `machine_learning/ingest_pipeline/extract_text/videos.py` — `fetch_transcript_text()` now instantiates `YouTubeTranscriptApi()` and normalises snippet objects to plain dicts.  
Also updated `sources.py` `/youtube-title` endpoint to use `api.list(vid)` instead of the removed `list_transcripts()` class method.

### Bug 3 — YouTube chunks had no `start_time`, so `start_seconds` was null in citations
**Symptom:** TC013/TC017 passed upload and ask, but failed: "No citation had a start_seconds value."  
**Root cause:** The transcript was chunked as flat text with no timestamp metadata. The `chunk` table columns `start_time`/`end_time` were left `NULL`, so retrieval returned `NULL` for `start_seconds` in every citation.  
**Fix:** Updated `sources.py` `/upload/youtube` to compute `start_time`/`end_time` for each chunk by mapping character offsets of the chunk text back to the segment timeline. Each chunk's `start_time` is set to the `start_time` of the segment whose text begins at or before the chunk's position in the raw transcript string.

### Bug 4 — Missing Python dependencies
**Symptom:** Backend failed to start with `ModuleNotFoundError`.  
**Missing packages:** `pymupdf`, `youtube-transcript-api`, `ftfy`, `sentence-transformers`, `python-multipart`.  
**Fix:** Installed all missing packages into `backend/.venv`.  
**Recommendation:** Add these to `backend/requirements.txt`:
```
pymupdf>=1.27
youtube-transcript-api>=1.2
ftfy>=6.0
sentence-transformers>=3.0
python-multipart>=0.0.9
```

---

## 3. Coverage

| Area | Covered by |
|------|-----------|
| Temp filesystem write access | TC009 |
| pgvector DB extension | TC010 |
| Embedding model dimensions | TC011 |
| PDF ingest → DB (source + chunk + embedding) | TC012 |
| YouTube ingest → DB (all 4 tables) | TC013 |
| Input validation (invalid YouTube URLs → 400) | TC014 |
| Cascading delete of all source-related rows | TC015 |
| End-to-end RAG accuracy (PDF) | TC016 |
| End-to-end RAG structural correctness (YouTube + timestamps) | TC017 |

---

## 4. Key Observations

- The `retrieve_similar_chunks` query uses `chunk.start_time` — this is only populated if the ingestion code explicitly sets it. Any future ingestion paths (e.g. handwritten notes) must also populate this field or citations will have `null` timestamps.
- The `video_segment` table rows are inserted via a separate `insert_video_segments()` call after `ingest_source()`. If that call fails after `ingest_source()` succeeds, segment rows will be missing but the source and chunks will exist. Consider wrapping both in a single transaction in a future iteration.
- `youtube-transcript-api` 1.x does not expose `video_title` on the `TranscriptList` object — the `/youtube-title` endpoint falls back to returning the raw `video_id` when title resolution fails.
