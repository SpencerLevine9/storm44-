# Cloud Database Connection & Data Migration Plan

This plan details the steps to transition your application from using the local Dockerized PostgreSQL database to your running cloud PostgreSQL server (Azure Database for PostgreSQL). It also covers migrating your existing local data (including embeddings).

## Pre-Flight Checklist

> [!IMPORTANT]
> Confirm the following before proceeding:
> 1. **Confirm cloud target:** The connection template in `backend/.env.example` already shows `storm44cloud.postgres.database.azure.com`. Verify you have the final credentials (host, user, password) ready.
> 2. **pgvector on Azure:** Does your Azure PostgreSQL instance have the `pgvector` extension installed? Run `SELECT extversion FROM pg_extension WHERE extname = 'vector';` on the cloud instance. If missing, run `CREATE EXTENSION vector;` (requires superuser or the `azure_pg_admin` role on Azure Flexible Server).
> 3. **pgvector version match:** Run the same version query locally against the Docker container. The cloud version must match or be newer to avoid binary vector incompatibility on the HNSW index.

---

## Proposed Changes

### 1. Pre-Migration: Fix Missing Python Dependency

`backend/requirements.txt` is missing the `pgvector` Python package, which is required by the verification test script. Add it before proceeding:

```bash
# In backend/requirements.txt, add:
pgvector>=0.3.0
```

Then reinstall:
```bash
cd backend && pip install -r requirements.txt
```

---

### 2. Environment Configuration Update

Update `backend/.env` to point to your Azure instance. Use `.env.example` as the template.

#### [MODIFY] [backend/.env](../../../backend/.env)

```dotenv
# Keep the local URL commented out as a rollback fallback
# DATABASE_URL=postgresql://postgres:password@127.0.0.1:5432/storm44

# Azure cloud connection
DATABASE_URL=postgresql://storm44admin:<your_password>@storm44cloud.postgres.database.azure.com:5432/postgres?sslmode=require
```

> **Important:** `machine_learning/ingest_pipeline/store/postgres.py` also reads the database connection for embedding ingestion. Any future ingestion runs must use this same updated `DATABASE_URL`.

---

### 3. Data Migration Workflow

This migrates the local schema and all data (including pgvector embeddings) to Azure.

> [!NOTE]
> The codebase has two schema files. We are migrating data from the **production schema** at `backend/app/db/schema.sql` (UUID-based, pgvector-enabled). The legacy schema at `backend/app/database/schema.sql` (SERIAL-based) is not in use and should be ignored.

#### Step 1 — Dump the Local Database

Run this against the local Docker container. The `--no-owner` and `--no-acl` flags are required to avoid role mismatches between the local `postgres` superuser and the Azure-managed user.

```bash
pg_dump \
  -h 127.0.0.1 -p 5432 -U postgres \
  --no-owner --no-acl \
  -Fc \
  storm44 > storm44_local.dump
```

#### Step 2 — Restore to Azure

```bash
pg_restore \
  --no-owner --no-acl \
  -h storm44cloud.postgres.database.azure.com \
  -U storm44admin \
  -d postgres \
  --verbose \
  storm44_local.dump
```

#### Step 3 — Rebuild the HNSW Index

After the restore, explicitly rebuild the vector search index to ensure it is valid on the new server:

```sql
REINDEX INDEX idx_embedding_cosine;
```

---

## Verification Plan

### Automated / Manual Testing

1. **Pre-restore:** Confirm pgvector version matches between local Docker and Azure (see Pre-Flight Checklist).
2. **Post-restore:** Run `REINDEX INDEX idx_embedding_cosine;` on the Azure instance.
3. **Connection test:** Restart the local backend (`uvicorn`) and observe startup logs for `Pool initialized` and pgvector extension verified messages.
4. **RAG accuracy:** Run `backend/testsprite_tests/scripts/test_db_insertion.py` against the cloud to verify connectivity, then execute the TC001/TC003 TestSprite test cases to confirm pgvector search returns expected chunks and citations.
5. **Rollback window:** Leave the local Docker `db` service running for at least 24 hours as a fallback before decommissioning. If any verification step fails, revert `DATABASE_URL` in `.env` to the local connection string.
6. **Docker cleanup (optional):** Once all tests pass, comment out the `db` service in `docker-compose.yml` to free local machine resources.

### Rollback Procedure

If cloud verification fails at any step:
1. Swap `DATABASE_URL` back to the commented-out local value in `backend/.env`.
2. Restart the backend — it will reconnect to the local Docker instance immediately.
3. Do **not** remove the Docker `db` service or its `pgdata` volume until fully verified.

---

## Post-Migration Follow-Up

> [!WARNING]
> **SSL Certificate Verification:** `backend/app/db/database.py` currently sets `ctx.verify_mode = ssl.CERT_NONE`, which disables certificate validation. This is acceptable for local development but exposes cloud connections to MITM attacks. Before going to production, update this to use `ssl.CERT_REQUIRED` with the Azure CA bundle (downloadable from the Azure portal).
