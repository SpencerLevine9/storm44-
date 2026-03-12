"""
Postgres helpers for the ingestion pipeline.

Provides functions to insert / update source and chunk rows
so pipeline steps can persist metadata as they run.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import psycopg2
import psycopg2.extras


def get_connection():
    """Return a new psycopg2 connection using DATABASE_URL or PG* env vars."""
    dsn = os.getenv("DATABASE_URL")
    if dsn:
        return psycopg2.connect(dsn)
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=int(os.getenv("PGPORT", "5432")),
        dbname=os.getenv("PGDATABASE", "storm44"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


# ── Source helpers ──────────────────────────────────────────────────

def insert_source(
    user_id: int,
    title: str,
    source_type: str,
    source_path: Optional[str] = None,
) -> int:
    """Insert a new source row (status='processing') and return its id."""
    sql = """
        INSERT INTO source (user_id, title, source_type, source_path)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id, title, source_type, source_path))
            source_id: int = cur.fetchone()[0]
        conn.commit()
        return source_id
    finally:
        conn.close()


def update_source(source_id: int, **fields: Any) -> None:
    """
    Update arbitrary columns on a source row.

    Example:
        update_source(1, status='ready', num_pages=42, output_text_path='...')
    """
    allowed = {
        "output_text_path", "num_pages", "video_id", "video_url",
        "transcript_source", "num_segments", "status", "error_message",
    }
    to_set = {k: v for k, v in fields.items() if k in allowed}
    if not to_set:
        return

    set_clause = ", ".join(f"{col} = %s" for col in to_set)
    values = list(to_set.values()) + [source_id]

    sql = f"UPDATE source SET {set_clause} WHERE id = %s"
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, values)
        conn.commit()
    finally:
        conn.close()


# ── Chunk helpers ───────────────────────────────────────────────────

def insert_chunks(source_id: int, chunks: List[Dict[str, Any]]) -> int:
    """
    Bulk-insert chunk rows for a given source.

    Each dict in *chunks* is expected to have the keys produced by chunk.py:
        chunk_id, start_page, end_page, approx_words, text

    Returns the number of rows inserted.
    """
    if not chunks:
        return 0

    sql = """
        INSERT INTO chunk
            (source_id, chunk_index, start_page, end_page, approx_words, text, preview)
        VALUES %s
        ON CONFLICT (source_id, chunk_index) DO NOTHING
    """
    rows = []
    for c in chunks:
        text = c.get("text", "")
        rows.append((
            source_id,
            c.get("chunk_id", c.get("chunk_index", 0)),
            c.get("start_page"),
            c.get("end_page"),
            c.get("approx_words"),
            text,
            text[:200] if text else None,
        ))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, sql, rows)
        conn.commit()
        return len(rows)
    finally:
        conn.close()


# ── Video segment helpers ──────────────────────────────────────────

def insert_video_segments(
    source_id: int,
    segments: List[Dict[str, Any]],
) -> int:
    """
    Bulk-insert video_segment rows for a given source.

    Each dict should have: text, start (seconds), duration.
    Returns the number of rows inserted.
    """
    if not segments:
        return 0

    sql = """
        INSERT INTO video_segment (source_id, text, start_time, duration, seg_index)
        VALUES %s
        ON CONFLICT (source_id, seg_index) DO NOTHING
    """
    rows = []
    for i, seg in enumerate(segments):
        rows.append((
            source_id,
            seg.get("text", ""),
            seg.get("start", 0.0),
            seg.get("duration"),
            i,
        ))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(cur, sql, rows)
        conn.commit()
        return len(rows)
    finally:
        conn.close()
