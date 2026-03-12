"""
Post-pipeline loader: reads artifact files from disk and bulk-inserts into
PostgreSQL (source, chunk, video_segment, embedding tables).

Run *after* pipeline.py has finished producing artifacts.

Usage:
    python -m machine_learning.ingest_pipeline.store.postgres [--user-id 1]
"""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

REPO_ROOT = Path(__file__).resolve().parents[2]  # machine_learning/
ARTIFACTS = REPO_ROOT / "artifacts"
META_DIR = ARTIFACTS / "metadata"
CHUNKS_DIR = ARTIFACTS / "chunks"
SEGMENTS_DIR = ARTIFACTS / "youtube_segments"
EMB_DIR = ARTIFACTS / "embeddings"
EMB_NPY = EMB_DIR / "embeddings.npy"
EMB_INDEX = EMB_DIR / "chunks_index.jsonl"

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def _get_conn():
    if psycopg2 is None:
        raise RuntimeError("psycopg2 is required – pip install psycopg2-binary")
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. "
            "Example: postgresql://user:pass@host.postgres.database.azure.com:5432/storm44?sslmode=require"
        )
    return psycopg2.connect(url)


# ── 1. Sources ──────────────────────────────────────────────────────

def _load_metadata() -> List[Dict[str, Any]]:
    if not META_DIR.is_dir():
        return []
    metas = []
    for fp in sorted(META_DIR.glob("*.json")):
        metas.append(json.loads(fp.read_text(encoding="utf-8")))
    return metas


def _derive_title(meta: Dict[str, Any], path: Path) -> str:
    """Best-effort title: use metadata title, fall back to filename stem."""
    if meta.get("title"):
        return meta["title"]
    if meta.get("source_file"):
        return Path(meta["source_file"]).stem
    return path.stem


def _insert_sources(
    cur, metas: List[Dict[str, Any]], user_id: int
) -> Dict[str, int]:
    """Insert source rows and return a mapping of source_key -> source.id.

    source_key is:
      - source_file (posix path string) for PDFs
      - video_id for YouTube
    """
    key_to_id: Dict[str, int] = {}

    for meta in metas:
        stype = meta.get("source_type", "unknown")
        title = meta.get("title") or Path(meta.get("source_file", "unknown")).stem

        cur.execute(
            """
            INSERT INTO source
                (user_id, title, source_type, source_path, output_text_path,
                 num_pages, video_id, video_url, transcript_source, num_segments,
                 status)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'ready')
            ON CONFLICT DO NOTHING
            RETURNING id
            """,
            (
                user_id,
                title,
                stype,
                meta.get("source_file") or meta.get("url"),
                meta.get("output_text_file"),
                meta.get("num_pages"),
                meta.get("video_id"),
                meta.get("url"),
                meta.get("transcript_source"),
                meta.get("num_segments"),
            ),
        )
        row = cur.fetchone()
        if row is None:
            # Already exists – look it up
            if stype == "youtube" and meta.get("video_id"):
                cur.execute(
                    "SELECT id FROM source WHERE video_id = %s AND user_id = %s",
                    (meta["video_id"], user_id),
                )
            else:
                cur.execute(
                    "SELECT id FROM source WHERE source_path = %s AND user_id = %s",
                    (meta.get("source_file"), user_id),
                )
            row = cur.fetchone()

        if row is None:
            continue

        source_id = row[0]
        if stype == "youtube" and meta.get("video_id"):
            key_to_id[meta["video_id"]] = source_id
        if meta.get("source_file"):
            key_to_id[meta["source_file"]] = source_id
            key_to_id[Path(meta["source_file"]).name] = source_id

    return key_to_id


# ── 2. Chunks ───────────────────────────────────────────────────────

_CHUNK_ID_SUFFIX_RE = re.compile(r"_chunk_(\d+)$")


def _parse_chunk_index(raw_id) -> int:
    """chunk_id may be an int (PDF) or a string like 'Video_1_chunk_003' (YT)."""
    if isinstance(raw_id, int):
        return raw_id
    m = _CHUNK_ID_SUFFIX_RE.search(str(raw_id))
    if m:
        return int(m.group(1))
    return int(raw_id)


def _load_all_chunks() -> List[Dict[str, Any]]:
    if not CHUNKS_DIR.is_dir():
        return []
    all_chunks: List[Dict[str, Any]] = []
    for fp in sorted(CHUNKS_DIR.glob("*_chunks.json")):
        data = json.loads(fp.read_text(encoding="utf-8"))
        if isinstance(data, list):
            all_chunks.extend(data)
    return all_chunks


def _resolve_source_id(
    chunk: Dict[str, Any], key_to_id: Dict[str, int]
) -> Optional[int]:
    """Try to match a chunk to an already-inserted source row."""
    # PDF chunks have source_file; YouTube chunks have video_id
    for key_field in ("source_file", "video_id"):
        val = chunk.get(key_field)
        if val and val in key_to_id:
            return key_to_id[val]
        if val:
            # Try just the filename
            fname = Path(val).name
            if fname in key_to_id:
                return key_to_id[fname]
    return None


def _insert_chunks(
    cur,
    chunks: List[Dict[str, Any]],
    key_to_id: Dict[str, int],
) -> Dict[Tuple[int, int], int]:
    """Insert chunk rows. Returns mapping of (source_id, chunk_index) -> chunk.id."""
    si_to_id: Dict[Tuple[int, int], int] = {}

    for c in chunks:
        source_id = _resolve_source_id(c, key_to_id)
        if source_id is None:
            continue

        chunk_index = _parse_chunk_index(c.get("chunk_id", 0))
        text = (c.get("text") or "").strip()
        if not text:
            continue

        cur.execute(
            """
            INSERT INTO chunk
                (source_id, chunk_index, start_page, end_page, start_time,
                 end_time, approx_words, text, preview)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (source_id, chunk_index) DO NOTHING
            RETURNING id
            """,
            (
                source_id,
                chunk_index,
                c.get("start_page"),
                c.get("end_page"),
                c.get("start_time"),
                c.get("end_time"),
                c.get("approx_words"),
                text,
                text[:256],
            ),
        )
        row = cur.fetchone()
        if row is None:
            cur.execute(
                "SELECT id FROM chunk WHERE source_id = %s AND chunk_index = %s",
                (source_id, chunk_index),
            )
            row = cur.fetchone()
        if row:
            si_to_id[(source_id, chunk_index)] = row[0]

    return si_to_id


# ── 3. Video segments ──────────────────────────────────────────────

def _insert_video_segments(
    cur, key_to_id: Dict[str, int]
) -> None:
    if not SEGMENTS_DIR.is_dir():
        return

    for fp in sorted(SEGMENTS_DIR.glob("*.jsonl")):
        segments: List[Dict[str, Any]] = []
        with fp.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    segments.append(json.loads(line))

        if not segments:
            continue

        # Resolve source_id from video_id in the first segment
        video_id = segments[0].get("video_id")
        source_id = key_to_id.get(video_id) if video_id else None
        if source_id is None:
            continue

        for idx, seg in enumerate(segments):
            text = (seg.get("text") or "").strip()
            if not text:
                continue
            cur.execute(
                """
                INSERT INTO video_segment
                    (source_id, text, start_time, duration, seg_index)
                VALUES (%s,%s,%s,%s,%s)
                ON CONFLICT (source_id, seg_index) DO NOTHING
                """,
                (
                    source_id,
                    text,
                    seg.get("start", 0.0),
                    seg.get("duration"),
                    idx,
                ),
            )


# ── 4. Embeddings ──────────────────────────────────────────────────

def _insert_embeddings(
    cur,
    key_to_id: Dict[str, int],
    chunk_pk_map: Dict[Tuple[int, int], int],
) -> int:
    if not EMB_NPY.exists() or not EMB_INDEX.exists():
        return 0

    vectors = np.load(EMB_NPY)
    metas: List[Dict[str, Any]] = []
    with EMB_INDEX.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                metas.append(json.loads(line))

    if len(metas) != vectors.shape[0]:
        print(
            f"[WARN] embedding count mismatch: index={len(metas)}, npy={vectors.shape[0]}. "
            "Inserting min(both)."
        )

    inserted = 0
    n = min(len(metas), vectors.shape[0])
    for i in range(n):
        m = metas[i]
        source_id = _resolve_source_id(m, key_to_id)
        if source_id is None:
            continue

        chunk_index = _parse_chunk_index(m.get("chunk_id", 0))
        chunk_id = chunk_pk_map.get((source_id, chunk_index))
        if chunk_id is None:
            continue

        vec = vectors[i].tolist()

        cur.execute(
            """
            INSERT INTO embedding (chunk_id, embedding, embedding_model)
            VALUES (%s, %s, %s)
            ON CONFLICT (chunk_id) DO NOTHING
            """,
            (chunk_id, str(vec), MODEL_NAME),
        )
        inserted += 1

    return inserted


# ── Main ────────────────────────────────────────────────────────────

def load_artifacts(user_id: int = 1) -> None:
    conn = _get_conn()
    try:
        with conn.cursor() as cur:
            # 1. Sources
            metas = _load_metadata()
            key_to_id = _insert_sources(cur, metas, user_id)
            print(f"Sources: {len(key_to_id)} keys mapped")

            # 2. Chunks
            chunks = _load_all_chunks()
            chunk_pk_map = _insert_chunks(cur, chunks, key_to_id)
            print(f"Chunks: {len(chunk_pk_map)} inserted/resolved")

            # 3. Video segments
            _insert_video_segments(cur, key_to_id)
            print("Video segments: done")

            # 4. Embeddings
            emb_count = _insert_embeddings(cur, key_to_id, chunk_pk_map)
            print(f"Embeddings: {emb_count} inserted")

        conn.commit()
        print("All artifacts loaded into Postgres.")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Load pipeline artifacts into Postgres")
    parser.add_argument(
        "--user-id",
        type=int,
        default=int(os.getenv("PIPELINE_USER_ID", "1")),
        help="user_account.id to associate sources with (default: env PIPELINE_USER_ID or 1)",
    )
    args = parser.parse_args()
    load_artifacts(user_id=args.user_id)


if __name__ == "__main__":
    main()
