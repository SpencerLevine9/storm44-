"""
Store ingested chunks and embeddings into PostgreSQL (pgvector).

Reads artifacts produced by embed.py:
  artifacts/embeddings/embeddings.npy       — float32 array, shape (N, 384)
  artifacts/embeddings/chunks_index.jsonl   — one JSON object per chunk

Requires env vars:
  DATABASE_URL   — postgres connection string (sslmode=require for Azure)
  INGEST_USER_ID — UUID of the user account that owns these sources
"""
from __future__ import annotations

import asyncio
import json
import os
import ssl
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode
from uuid import UUID

import asyncpg
import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
EMBEDDINGS_NPY = REPO_ROOT / "artifacts" / "embeddings" / "embeddings.npy"
CHUNKS_JSONL   = REPO_ROOT / "artifacts" / "embeddings" / "chunks_index.jsonl"
EMBEDDING_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def _get_dsn() -> str:
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set.")
    return url


def _build_ssl_context(dsn: str) -> ssl.SSLContext | None:
    params = parse_qs(urlparse(dsn).query)
    if params.get("sslmode", ["disable"])[0] == "require":
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return None


def _strip_sslmode(dsn: str) -> str:
    parsed = urlparse(dsn)
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("sslmode", None)
    new_query = urlencode({k: v[0] for k, v in params.items()})
    return str(urlunparse((
        parsed.scheme, parsed.netloc, parsed.path,
        parsed.params, new_query, parsed.fragment,
    )))


def _source_key(chunk: dict) -> str:
    """Derive a stable grouping key from a chunk's source metadata."""
    if chunk.get("source_type") == "youtube":
        return f"youtube::{chunk.get('video_id') or chunk.get('url') or chunk.get('title', 'unknown')}"
    return f"pdf::{chunk.get('source_file', 'unknown')}"


def _source_meta(chunks_in_group: list[dict]) -> dict:
    """Build source-level metadata from the first chunk in a group."""
    first = chunks_in_group[0]
    stype = first.get("source_type", "pdf")
    if stype == "youtube":
        return {
            "source_type": "youtube",
            "title": first.get("title", "Untitled Video"),
            "video_id": first.get("video_id"),
            "video_url": first.get("url"),
            "num_segments": len(chunks_in_group),
        }
    return {
        "source_type": "pdf",
        "title": Path(first.get("source_file", "untitled")).stem,
        "source_path": first.get("source_file"),
        "num_pages": max(
            (c.get("end_page") or 0) for c in chunks_in_group
        ) or None,
    }


async def insert_chunks(chunks: list[dict], embeddings: np.ndarray) -> None:
    """
    Group chunks by source, then insert each source + its chunks + embeddings
    in a single transaction per source. A failure in one source rolls back only
    that source, leaving already-committed sources intact.
    """
    user_id_str = os.getenv("INGEST_USER_ID")
    if not user_id_str:
        raise RuntimeError(
            "INGEST_USER_ID env var is required. "
            "Set it to the UUID of the user account that owns these sources."
        )
    user_id = UUID(user_id_str)

    dsn = _get_dsn()
    ssl_ctx = _build_ssl_context(dsn)
    conn = await asyncpg.connect(dsn=_strip_sslmode(dsn), ssl=ssl_ctx)

    try:
        # Group by source, preserving original index for embedding lookup
        groups: dict[str, list[tuple[int, dict]]] = defaultdict(list)
        for idx, chunk in enumerate(chunks):
            groups[_source_key(chunk)].append((idx, chunk))

        for key, indexed_chunks in groups.items():
            meta = _source_meta([c for _, c in indexed_chunks])
            print(f"  Storing source: {meta['title']} ({len(indexed_chunks)} chunks)")

            async with conn.transaction():
                source_id: UUID = await conn.fetchval(
                    """
                    INSERT INTO source (
                        user_id, title, source_type, embedding_model,
                        source_path, num_pages,
                        video_id, video_url, num_segments, status
                    ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,'ready')
                    RETURNING id
                    """,
                    user_id,
                    meta["title"],
                    meta["source_type"],
                    EMBEDDING_MODEL,
                    meta.get("source_path"),
                    meta.get("num_pages"),
                    meta.get("video_id"),
                    meta.get("video_url"),
                    meta.get("num_segments"),
                )

                for local_idx, (orig_idx, chunk) in enumerate(indexed_chunks):
                    chunk_id: UUID = await conn.fetchval(
                        """
                        INSERT INTO chunk (
                            source_id, chunk_index, text, preview,
                            start_page, end_page, start_time, end_time, approx_words
                        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)
                        RETURNING id
                        """,
                        source_id,
                        local_idx,
                        chunk.get("text", ""),
                        chunk.get("preview"),
                        chunk.get("start_page"),
                        chunk.get("end_page"),
                        chunk.get("start_time"),
                        chunk.get("end_time"),
                        chunk.get("approx_words"),
                    )

                    vec = embeddings[orig_idx].tolist()
                    vec_literal = f"[{','.join(str(v) for v in vec)}]"
                    await conn.execute(
                        """
                        INSERT INTO embedding (chunk_id, embedding, embedding_model)
                        VALUES ($1, $2::vector, $3)
                        """,
                        chunk_id,
                        vec_literal,
                        EMBEDDING_MODEL,
                    )

            print(f"  Committed source_id={source_id}")
    finally:
        await conn.close()


def load_artifacts() -> tuple[list[dict], np.ndarray]:
    if not CHUNKS_JSONL.exists():
        raise FileNotFoundError(f"Chunk index not found: {CHUNKS_JSONL}")
    if not EMBEDDINGS_NPY.exists():
        raise FileNotFoundError(f"Embeddings not found: {EMBEDDINGS_NPY}")

    chunks = [json.loads(line) for line in CHUNKS_JSONL.read_text().splitlines() if line.strip()]
    embeddings = np.load(EMBEDDINGS_NPY)

    if len(chunks) != len(embeddings):
        raise ValueError(
            f"Chunk count ({len(chunks)}) does not match embedding count ({len(embeddings)})"
        )
    return chunks, embeddings


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    print("Loading artifacts...")
    chunks, embeddings = load_artifacts()
    print(f"Found {len(chunks)} chunks. Storing to PostgreSQL...")
    asyncio.run(insert_chunks(chunks, embeddings))
    print("Done.")
