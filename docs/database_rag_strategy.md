# Database Connectivity & RAG Storage Strategy

This document outlines the strategic plan for implementing database connectivity and the data storage layer required for Retrieval-Augmented Generation (RAG) features in the Storm44 application.

## 1. Goal
Establish database connectivity for the FastAPI backend to the Azure Database for PostgreSQL (Flexible Server) using `pgvector`, and implement the necessary logic to store and retrieve data for core application features and AI study tools.

## 2. Schema Alignment Strategy
Based on the project scope, the database schema (`backend/app/db/schema.sql`) must be updated to ensure consistency and support all required features.

**Key Changes:**
- **UUID Primary Keys:** Migrate all `id` fields from `SERIAL` integers to `UUID`. This aligns with the requirement outlined in `PROJECT_SCOPE.md` for better scalability and security.
- **Relational Integrity:** Ensure all foreign key references (e.g., `user_id`, `source_id`, `chunk_id`) are updated to `UUID` to match the new primary keys.
- **New Tables:** Introduce the missing `flashcards` and `quiz_questions` tables to persist the generated study tools, linking them back to the source materials and specific citations (via `citation_chunk_id`).

## 3. Implementation Plan

### A. Database Connection Layer
Create the core connection boilerplate to interface with the Azure PostgreSQL instance asynchronously.

- **Target File:** `backend/app/db/database.py` (or similar)
- **Requirements:**
  - Utilize an asynchronous driver like `asyncpg` or `SQLAlchemy` (async core) for high performance.
  - Implement a connection pool to manage concurrent database access efficiently.
  - Ensure SSL is strictly enforced (`?sslmode=require`) by correctly parsing the `DATABASE_URL` environment variable.
  - Add logic during the application startup to verify the database connection and ensure the `pgvector` extension is active.

### B. RAG Data Access Layer (DAL)
Develop the SQL queries and Python functions necessary for data ingestion and vector retrieval.

- **Target File:** `backend/app/db/crud.py` (or similar)
- **Core Operations:**
  - **Ingestion:** Functions to handle the creation of a new `source` record, followed by bulk inserts of extracted text `chunk`s and their corresponding `embedding`s (using `pgvector`).
  - **RAG Retrieval:** Implement the query using pgvector's cosine similarity operator (`<=>`). It must filter vectors by a provided list of `source_id`s to restrict the AI Tutor's context scope.
  - **Study Tools CRUD:** Functions to save, read, and delete generated flashcards and quiz questions belonging to a specific source.

### C. FastAPI Application Integration
Wire the database connection layer into the FastAPI application lifecycle.

- **Target File:** `backend/app/main.py`
- **Requirements:**
  - Add FastAPI `lifespan` events (or `@app.on_event("startup")` / `@app.on_event("shutdown")` depending on FastAPI version) to initialize the database connection pool when the server starts and gracefully close it when the server stops.

## 4. Verification & Testing

Our strategy relies exclusively on automated testing frameworks to validate the backend APIs and database operations before deployment.

### Automated Testing Strategy (TestSprite)
We will use TestSprite to execute end-to-end integration tests focusing on RAG operations and Database Connectivity. The test plan is configured in `backend/testsprite_tests/testsprite_backend_test_plan.json` and consists of the following key scenarios:

1. **Database Health Verification:** Validate that the application connects to the Azure Database for PostgreSQL instance and the `pgvector` extension is active.
2. **Ingestion Pipeline Automation:** Utilize the local sample data provided in `machine_learning/data/` (parsing `metadata/*.json`, `chunks/*.json`, and mapping vectors from `embeddings/embeddings.npy` using `chunks_index.jsonl`) to automatically seed the database via the `/ingest` endpoint. This will verify transaction safety and data integrity.
3. **Automated Vector Search Validation:** Simulate user queries against the `/query` endpoint using test vectors from the `.npy` files. The automated assertions will verify that the database correctly performs cosine similarity operations and returns the most relevant contextual chunks.
4. **Study Tools Validation:** Automate requests to the `/flashcards/generate` and `/quizzes/generate` endpoints using the identifiers of the automatically ingested test data to ensure the generation state is successfully persisted to the database.
