"""
Async database connection pool for Storm44.

Connects to Azure PostgreSQL (or any Postgres) via DATABASE_URL using asyncpg.
SSL is required for Azure; the connection string should include ?sslmode=require.

Example DATABASE_URL:
  postgresql://user:password@myserver.postgres.database.azure.com:5432/storm44?sslmode=require
"""
from __future__ import annotations

import os
import ssl
from urllib.parse import urlparse, parse_qs

import asyncpg

_pool: asyncpg.Pool | None = None


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Example: postgresql://user:pass@host.postgres.database.azure.com:5432/storm44?sslmode=require"
        )
    return url


def _build_ssl_context(dsn: str) -> ssl.SSLContext | None:
    """Return an SSL context if sslmode=require is in the DSN, else None."""
    parsed = urlparse(dsn)
    params = parse_qs(parsed.query)
    sslmode = params.get("sslmode", ["disable"])[0]
    if sslmode == "require":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return None


def _strip_sslmode(dsn: str) -> str:
    """asyncpg handles SSL via ssl= kwarg; strip sslmode from the DSN string."""
    from urllib.parse import urlunparse, urlencode
    parsed = urlparse(dsn)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("sslmode", None)
    new_query = urlencode({k: v[0] for k, v in params.items()})
    return str(urlunparse((
        parsed.scheme, parsed.netloc, parsed.path,
        parsed.params, new_query, parsed.fragment,
    )))


async def init_pool() -> None:
    """Create the asyncpg connection pool and verify pgvector is available."""
    global _pool
    dsn = get_database_url()
    ssl_ctx = _build_ssl_context(dsn)
    clean_dsn = _strip_sslmode(dsn)

    _pool = await asyncpg.create_pool(
        dsn=clean_dsn,
        ssl=ssl_ctx,
        min_size=1,
        max_size=int(os.getenv("DB_POOL_MAX", "10")),
    )

    async with _pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT 1 FROM pg_extension WHERE extname = 'vector'"
        )
        if row is None:
            raise RuntimeError(
                "pgvector extension is not installed in this database. "
                "Run: CREATE EXTENSION vector;"
            )


async def close_pool() -> None:
    """Gracefully close the connection pool on app shutdown."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


def get_pool() -> asyncpg.Pool:
    """Return the active pool. Raises if init_pool() has not been called."""
    if _pool is None:
        raise RuntimeError("Database pool is not initialized. Call init_pool() first.")
    return _pool
