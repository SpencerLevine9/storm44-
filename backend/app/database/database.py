"""
Database connection and schema setup for Storm44.
Uses PostgreSQL; set DATABASE_URL in environment (e.g. postgresql://user:pass@localhost:5432/storm44).
"""

from __future__ import annotations

import os
from pathlib import Path

# Optional: install psycopg2-binary for PostgreSQL
try:
    import psycopg2
    from psycopg2.extensions import connection as PgConnection
except ImportError:
    psycopg2 = None
    PgConnection = None

_SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_database_url() -> str:
    return os.getenv(
        "DATABASE_URL",
        "postgresql://localhost:5432/storm44",
    )


def get_connection():
    """Return a new PostgreSQL connection. Requires psycopg2 and a running Postgres with DATABASE_URL."""
    if psycopg2 is None:
        raise RuntimeError("Install psycopg2-binary to use the database (pip install psycopg2-binary).")
    return psycopg2.connect(get_database_url())


def init_db(conn=None) -> None:
    """Create user_account table (and any other tables in schema.sql). Idempotent."""
    sql = _SCHEMA_PATH.read_text()
    own_conn = conn is None
    if own_conn:
        conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        if own_conn and conn is not None and conn.closed == 0:
            conn.close()


def ensure_user_table() -> None:
    """Convenience: open connection, run schema, close. Use at app startup if desired."""
    conn = get_connection()
    try:
        init_db(conn=conn)
    finally:
        conn.close()
