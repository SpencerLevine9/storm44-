"""
Database connection and schema setup for Storm44.

Connects to Azure PostgreSQL (or any Postgres) via DATABASE_URL.
SSL is required for Azure; the connection string should include ?sslmode=require.

Example DATABASE_URL:
  postgresql://user:password@myserver.postgres.database.azure.com:5432/storm44?sslmode=require
"""
from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator

import psycopg2
import psycopg2.pool
from psycopg2.extensions import connection as PgConnection

_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

_pool: psycopg2.pool.ThreadedConnectionPool | None = None


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Example: postgresql://user:pass@host.postgres.database.azure.com:5432/storm44?sslmode=require"
        )
    return url


def _get_pool() -> psycopg2.pool.ThreadedConnectionPool:
    global _pool
    if _pool is None or _pool.closed:
        _pool = psycopg2.pool.ThreadedConnectionPool(
            minconn=1,
            maxconn=int(os.getenv("DB_POOL_MAX", "10")),
            dsn=get_database_url(),
        )
    return _pool


def get_connection() -> PgConnection:
    """Get a connection from the pool."""
    return _get_pool().getconn()


def put_connection(conn: PgConnection) -> None:
    """Return a connection to the pool."""
    pool = _get_pool()
    pool.putconn(conn)


@contextmanager
def get_db() -> Generator[PgConnection, None, None]:
    """Context manager that yields a connection and returns it to the pool."""
    conn = get_connection()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        put_connection(conn)


def init_db(conn: PgConnection | None = None) -> None:
    """Run schema.sql to create all tables. Idempotent (IF NOT EXISTS)."""
    sql = _SCHEMA_PATH.read_text()
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        if own_conn:
            put_connection(conn)


def close_pool() -> None:
    """Shut down the connection pool (call on app shutdown)."""
    global _pool
    if _pool is not None and not _pool.closed:
        _pool.closeall()
        _pool = None
