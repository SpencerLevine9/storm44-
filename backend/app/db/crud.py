"""
Data Access Layer for Storm44.

All database operations go through this module. Functions accept an asyncpg
Pool (or Connection) obtained from database.get_pool().
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

import asyncpg


# ---------------------------------------------------------------------------
# Ingestion
# ---------------------------------------------------------------------------

async def ingest_source(
    pool: asyncpg.Pool,
    *,
    user_id: UUID,
    title: str,
    source_type: str,
    chunks: list[dict[str, Any]],
    embeddings: list[list[float]],
    embedding_model: str = "MiniLM-L6-v2",
    metadata: dict[str, Any] | None = None,
) -> UUID:
    """
    Insert a source, its chunks, and embeddings in a single transaction.
    Rolls back completely on any failure — no orphaned rows.

    chunks: list of dicts with keys matching the chunk table columns
            (chunk_index, text, start_page, end_page, start_time, end_time,
             approx_words, preview — all optional except chunk_index and text)
    embeddings: parallel list of 384-dim float vectors, one per chunk
    Returns the new source UUID.
    """
    if len(chunks) != len(embeddings):
        raise ValueError(
            f"chunks and embeddings must have the same length "
            f"({len(chunks)} vs {len(embeddings)})"
        )

    meta = metadata or {}

    async with pool.acquire() as conn:
        async with conn.transaction():
            source_id: UUID = await conn.fetchval(
                """
                INSERT INTO source (
                    user_id, title, source_type, embedding_model,
                    source_path, output_text_path,
                    num_pages, video_id, video_url,
                    transcript_source, num_segments, status
                ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,'ready')
                RETURNING id
                """,
                user_id,
                title,
                source_type,
                embedding_model,
                meta.get("source_path"),
                meta.get("output_text_path"),
                meta.get("num_pages"),
                meta.get("video_id"),
                meta.get("video_url"),
                meta.get("transcript_source"),
                meta.get("num_segments"),
            )

            chunk_ids: list[UUID] = []
            for chunk in chunks:
                chunk_id: UUID = await conn.fetchval(
                    """
                    INSERT INTO chunk (
                        source_id, chunk_index, text, preview,
                        start_page, end_page, start_time, end_time, approx_words
                    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                    RETURNING id
                    """,
                    source_id,
                    chunk["chunk_index"],
                    chunk["text"],
                    chunk.get("preview"),
                    chunk.get("start_page"),
                    chunk.get("end_page"),
                    chunk.get("start_time"),
                    chunk.get("end_time"),
                    chunk.get("approx_words"),
                )
                chunk_ids.append(chunk_id)

            await conn.executemany(
                """
                INSERT INTO embedding (chunk_id, embedding, embedding_model)
                VALUES ($1, $2, $3)
                """,
                [
                    (cid, f"[{','.join(str(v) for v in vec)}]", embedding_model)
                    for cid, vec in zip(chunk_ids, embeddings)
                ],
            )

    return source_id


# ---------------------------------------------------------------------------
# RAG Retrieval
# ---------------------------------------------------------------------------

async def retrieve_similar_chunks(
    conn: asyncpg.Connection,
    query_embedding: list[float],
    source_ids: list[UUID],
    k: int = 5,
) -> list[dict[str, Any]]:
    """
    Return the top-k chunks most similar to query_embedding, restricted to
    the given source_ids. Uses pgvector cosine distance (<=>).
    """
    # Use fixed-point notation to avoid scientific notation in vector literal,
    # which pgvector does not accept.
    vec_literal = "[" + ",".join(f"{v:.8f}" for v in query_embedding) + "]"

    # MATERIALIZED CTE forces PostgreSQL to fully evaluate the filter before
    # computing distances. Without MATERIALIZED, the planner may fold the
    # ORDER BY + LIMIT into the HNSW index scan, which returns global top-k
    # candidates before applying the WHERE filter — causing empty results.
    rows = await conn.fetch(
        """
        WITH filtered AS MATERIALIZED (
            SELECT
                c.id          AS chunk_id,
                c.source_id,
                c.chunk_index,
                c.text,
                c.start_page,
                c.end_page,
                c.start_time,
                c.end_time,
                s.title       AS source_title,
                s.source_type,
                s.video_url,
                s.video_id,
                s.source_path,
                e.embedding
            FROM embedding e
            JOIN chunk  c ON c.id = e.chunk_id
            JOIN source s ON s.id = c.source_id
            WHERE c.source_id = ANY($2::uuid[])
        )
        SELECT
            chunk_id, source_id, chunk_index, text,
            start_page, end_page, start_time, end_time,
            source_title, source_type, video_url, video_id, source_path,
            embedding <=> $1::vector AS distance
        FROM filtered
        ORDER BY distance
        LIMIT $3
        """,
        vec_literal,
        source_ids,
        k,
    )
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Flashcard CRUD
# ---------------------------------------------------------------------------

async def save_flashcards(
    pool: asyncpg.Pool,
    source_id: UUID,
    cards: list[dict[str, Any]],
) -> None:
    """
    Bulk-insert flashcards for a source.
    Each card: {front, back, citation_chunk_id (optional UUID)}
    """
    await pool.executemany(
        """
        INSERT INTO flashcard (source_id, citation_chunk_id, front, back)
        VALUES ($1, $2, $3, $4)
        """,
        [
            (
                source_id,
                card.get("citation_chunk_id"),
                card["front"],
                card["back"],
            )
            for card in cards
        ],
    )


async def get_flashcards(
    pool: asyncpg.Pool,
    source_id: UUID,
) -> list[dict[str, Any]]:
    rows = await pool.fetch(
        "SELECT id, source_id, citation_chunk_id, front, back, created_at "
        "FROM flashcard WHERE source_id = $1 ORDER BY created_at",
        source_id,
    )
    return [dict(r) for r in rows]


async def delete_flashcards(pool: asyncpg.Pool, source_id: UUID) -> None:
    await pool.execute("DELETE FROM flashcard WHERE source_id = $1", source_id)


# ---------------------------------------------------------------------------
# Quiz Question CRUD
# ---------------------------------------------------------------------------

async def save_quiz_questions(
    pool: asyncpg.Pool,
    source_id: UUID,
    questions: list[dict[str, Any]],
) -> None:
    """
    Bulk-insert quiz questions for a source.
    Each question: {question, options (list), correct_answer, citation_chunk_id (optional UUID)}
    """
    import json

    await pool.executemany(
        """
        INSERT INTO quiz_question (source_id, citation_chunk_id, question, options, correct_answer)
        VALUES ($1, $2, $3, $4, $5)
        """,
        [
            (
                source_id,
                q.get("citation_chunk_id"),
                q["question"],
                json.dumps(q["options"]),
                q["correct_answer"],
            )
            for q in questions
        ],
    )


async def get_quiz_questions(
    pool: asyncpg.Pool,
    source_id: UUID,
) -> list[dict[str, Any]]:
    rows = await pool.fetch(
        "SELECT id, source_id, citation_chunk_id, question, options, correct_answer, created_at "
        "FROM quiz_question WHERE source_id = $1 ORDER BY created_at",
        source_id,
    )
    return [dict(r) for r in rows]


async def delete_quiz_questions(pool: asyncpg.Pool, source_id: UUID) -> None:
    await pool.execute("DELETE FROM quiz_question WHERE source_id = $1", source_id)
