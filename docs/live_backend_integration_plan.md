# Live Backend Database Integration Plan

## Objective
Establish a direct, dynamic connection between the FastAPI backend and the Azure Database for PostgreSQL instance. The goal is to completely decouple the Retrieval-Augmented Generation (RAG) endpoints (like `/api/v1/ask`) from reading static JSON or Numpy files in the `machine_learning/data/` directory, and instead serve all data dynamically from the database.

---

## 1. Database Connection & Dependency Injection
To cleanly manage asynchronous database connections per API request without blocking or exhausting the pool, we will use FastAPI's dependency injection system.

*   **Targets:** `backend/app/db/database.py` and potentially a new `backend/app/api/deps.py`
*   **Actions:**
    *   Ensure the `init_pool()` function creates a robust `asyncpg` connection pool with SSL enforcement on startup.
    *   Create a `get_db_connection()` generator (or standard async dependency) that `yield`s a connection from the pool and automatically returns it (`Close`) upon request completion.

---

## 2. Dynamic RAG Data Access Layer
The Data Access Layer must be strictly scoped to accepting native Postgres connections and returning validated Python representations of database rows.

*   **Target:** `backend/app/db/crud.py`
*   **Actions:**
    *   Write `async def retrieve_relevant_chunks(conn: asyncpg.Connection, query_embedding: list[float], top_k: int) -> list[dict]:`
    *   The function will execute the `pgvector` cosine similarity query (`<=>`) utilizing the provided connection, joining the `embeddings` and `chunks` tables.
    *   It will return a pre-formatted dictionary list of results containing `chunk_id`, `source_id`, `snippet` (or `text`), and `metadata` (to extract `start_seconds` and `url` if necessary).

---

## 3. Route Integration (`/api/v1/ask`)
The RAG pipeline must be executed synchronously within the request lifecycle, ensuring that all data sourcing happens strictly against the active DB tables.

*   **Target:** `backend/app/api/v1/...` (wherever the `ask` route is defined)
*   **Actions:**
    1.  **Input:** The route accepts a JSON payload of the user query and `top_k`.
    2.  **Embedding:** The backend invokes the embedding model (e.g., `sentence-transformers` or an external API) on the user's raw query to generate a query vector.
    3.  **Retrieval:** The route injects the DB connection dependency and calls `retrieve_relevant_chunks`, passing the embedded vector.
    4.  **Generation:** The retrieved chunks are assembled into an LLM context prompt. The LLM processes the query against this context.
    5.  **Output:** The route parses the LLM's response and constructs the final JSON payload containing the `answer` and an array of `citations` formatted to match the requirements of Test Case `TC002`.

---

## 4. Validating the Integration
This implementation will satisfy the updated TestSprite configuration directly:

*   **`TC001` (Health Check):** The `GET /api/v1/health` endpoint will be updated to make a lightweight `SELECT 1` query to verify the `asyncpg` pool is functional before returning `status: ok`.
*   **`TC002` (RAG Ask Endpoint):** The `POST /api/v1/ask` request will be executed to verify the entire pipeline (Embedding -> PostgreSQL HNSW Index Retrieval -> LLM Generation) works cohesively, relying exclusively on data previously seeded into the database via Postgres, confirming all static filesystem reads are removed.
