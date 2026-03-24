# Database Connectivity & RAG Storage Implementation Plan

Provide a brief description of the problem, any background context, and what the change accomplishes.
This implementation plan covers setting up the core database connectivity for the Storm44 FastAPI backend and establishing the data pipeline for the application's Retrieval-Augmented Generation (RAG) capabilities. The goal is to connect to the Azure Database for PostgreSQL (Flexible Server) using `pgvector` and implement the necessary logic to store and retrieve chunks and their embeddings.

## Proposed Changes

### Database Connection Layer
This component handles the secure connection to the database (Azure PostgreSQL) using async drivers for high performance.

#### [NEW] `backend/app/db/database.py`
- Implement an asynchronous connection pool using `asyncpg` or `SQLAlchemy`'s async core.
- Ensure the connection enforces SSL via `?sslmode=require` correctly handling the `DATABASE_URL` environment variable.
- Include logic to verify that the `pgvector` extension is active during the startup phase.

### Schema Updates
Align the existing SQL schema with the project requirements based on user feedback.

#### [MODIFY] `backend/app/db/schema.sql`
- Update `id` fields from `SERIAL` to `UUID` as requested. Ensure the existing relational columns (like `user_id` on the source) use the proper UUID references.
- Add the missing `flashcards` and `quiz_questions` tables to support study tool generation to match `PROJECT_SCOPE.md`.

### RAG Data Access Layer (DAL)
This component encapsulates the SQL queries required to insert sources, chunks, embeddings, and perform the vector similarity search.

#### [NEW] `backend/app/db/crud.py`
- **Ingestion Queries**: Functions to insert a new `source`, bulk insert text `chunk`s, and bulk insert pgvector `embedding`s.
- **PGVector Retrieval System for the AI Tutor**:
  - **Goal:** Implement the pgvector similarity search specific to the AI Tutor's `POST /query` route.
  - **Function:** Create an asynchronous function (e.g., `search_similar_chunks`) taking a `target_embedding` (vectorized user query), a list of `scoped_source_ids` (UUIDs), and a `limit`.
  - **SQL Implementation:** Use the exact query from `PROJECT_SCOPE.md` bridging the `embeddings` and `chunks` tables.
    ```sql
    SELECT c.id, c.content, c.metadata,
           e.embedding <=> $1::vector AS distance
    FROM   embeddings e
    JOIN   chunks c ON c.id = e.chunk_id
    WHERE  c.source_id = ANY($2)
    ORDER  BY distance
    LIMIT  $3;
    ```
  - **Constraints:** Ensure the pgvector `vector_cosine_ops` distance operator `<=>` is explicitly used (since the HNSW index is built for cosine similarity). Ensure the query strictly enforces the `$2` scope filter.
- **Study Tools Queries**: Functions to store and retrieve generated flashcards and quiz questions.

### FastAPI Integration
Wire up the routes to use the data access layer.

#### [MODIFY] `backend/app/main.py`
- Add lifespan events to initialize and close the database connection pool on startup and shutdown.

## Verification Plan

### Automated Tests with TestSprite
- Configure the TestSprite backend test plan (`backend/testsprite_tests/testsprite_backend_test_plan.json`) to automate API and Database testing.
- Load the specific sample data from `machine_learning/data/`:
  - `metadata/*.json` for source initialization.
  - `chunks/*.json` for raw text and document metadata.
  - `embeddings/embeddings.npy` mapped via `chunks_index.jsonl` for vectors.
- Test that the vector similarity search accurately retrieves the closest chunks from the seeded vector data.
- Automate the schema assertions to verify the transaction block inserts `source`, `chunk`, and `embedding` records correctly.
