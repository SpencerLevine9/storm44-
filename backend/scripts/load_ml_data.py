"""
Load machine_learning/data/ into the Azure PostgreSQL database.

Sources, chunks, and embeddings are inserted idempotently (ON CONFLICT DO NOTHING).
A 'system' user_account row is upserted as the owner.

Run from the repo root:
    python backend/scripts/load_ml_data.py
"""

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2
from psycopg2.extras import execute_values

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "machine_learning" / "data"
META_DIR = DATA / "metadata"
CHUNKS_DIR = DATA / "chunks"
EMB_DIR = DATA / "embeddings"
EMB_NPY = EMB_DIR / "embeddings.npy"
EMB_INDEX = EMB_DIR / "chunks_index.jsonl"
ENV_FILE = ROOT / "backend" / ".env"

EMBED_MODEL = "all-MiniLM-L6-v2"


def load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


def parse_chunk_index(raw_id) -> int:
    if isinstance(raw_id, int):
        return raw_id
    m = re.search(r"_(\d+)$", str(raw_id))
    return int(m.group(1)) if m else int(raw_id)


def main() -> None:
    load_env(ENV_FILE)
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        sys.exit("ERROR: DATABASE_URL is not set.")

    # ── Load files ──────────────────────────────────────────────────
    print("Loading embeddings.npy …")
    embeddings = np.load(EMB_NPY)
    print(f"  {embeddings.shape[0]} vectors, dim {embeddings.shape[1]}")

    print("Loading chunks_index.jsonl …")
    index_entries = []
    with EMB_INDEX.open() as f:
        for line in f:
            line = line.strip()
            if line:
                index_entries.append(json.loads(line))
    assert len(index_entries) == embeddings.shape[0], "index/embedding count mismatch"

    print("Loading metadata …")
    metadata: dict[str, dict] = {}
    for p in sorted(META_DIR.glob("*.json")):
        metadata[p.stem] = json.loads(p.read_text())

    print("Loading chunk text files …")
    chunk_texts: dict[tuple, str] = {}
    for p in sorted(CHUNKS_DIR.glob("*_chunks.json")):
        for c in json.loads(p.read_text()):
            if c.get("source_type") == "pdf":
                key = (Path(c["source_file"]).name, int(c["chunk_id"]))
            else:
                idx = parse_chunk_index(c["chunk_id"])
                key = (c["video_id"], idx)
            chunk_texts[key] = c.get("text", "")

    # ── DB ──────────────────────────────────────────────────────────
    conn = psycopg2.connect(database_url)
    conn.autocommit = False
    cur = conn.cursor()

    # 1. System user
    print("\nUpserting system user …")
    cur.execute("""
        INSERT INTO user_account (username, password_hash)
        VALUES ('system', 'not-a-real-hash')
        ON CONFLICT (username) DO NOTHING
        RETURNING id
    """)
    row = cur.fetchone()
    if row:
        user_id = row[0]
    else:
        cur.execute("SELECT id FROM user_account WHERE username = 'system'")
        user_id = cur.fetchone()[0]
    print(f"  user_id = {user_id}")

    # 2. Sources
    print("\nInserting sources …")
    source_key_map: dict[str, str] = {}  # filename-or-video_id → UUID

    for stem, meta in metadata.items():
        stype = meta.get("source_type", "unknown")
        if stype == "pdf":
            title = stem.replace("_", " ")
            cur.execute("""
                INSERT INTO source (user_id, title, source_type, source_path,
                                    output_text_path, num_pages, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'ready')
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (
                user_id, title, "pdf",
                meta.get("source_file"),
                meta.get("output_text_file"),
                meta.get("num_pages"),
            ))
            fname_key = Path(meta.get("source_file", stem)).name
        else:
            title = meta.get("title", stem)
            cur.execute("""
                INSERT INTO source (user_id, title, source_type, video_id,
                                    video_url, transcript_source, num_segments, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'ready')
                ON CONFLICT DO NOTHING
                RETURNING id
            """, (
                user_id, title, "youtube",
                meta.get("video_id"),
                meta.get("url"),
                meta.get("transcript_source"),
                meta.get("num_segments"),
            ))
            fname_key = meta.get("video_id", stem)

        row = cur.fetchone()
        if row is None:
            # Already exists — look it up
            if stype == "pdf":
                cur.execute("SELECT id FROM source WHERE source_path = %s AND user_id = %s",
                            (meta.get("source_file"), user_id))
            else:
                cur.execute("SELECT id FROM source WHERE video_id = %s AND user_id = %s",
                            (meta.get("video_id"), user_id))
            row = cur.fetchone()

        if row is None:
            print(f"  WARN: could not resolve source for {stem}, skipping")
            continue

        source_key_map[fname_key] = str(row[0])
        print(f"  {stem} → {row[0]}")

    # 3. Chunks
    print("\nInserting chunks …")
    chunk_pk_map: dict[int, str] = {}  # global embedding index → chunk UUID

    by_source: dict[str, list] = defaultdict(list)
    for i, entry in enumerate(index_entries):
        sk = Path(entry["source_file"]).name if entry.get("source_type") == "pdf" else entry.get("video_id", "")
        by_source[sk].append((i, entry))

    for sk, entries in by_source.items():
        sid = source_key_map.get(sk)
        if sid is None:
            print(f"  WARN: no source_id for key '{sk}', skipping {len(entries)} chunks")
            continue

        for global_idx, entry in entries:
            local_idx = parse_chunk_index(entry["chunk_id"])
            lookup_key = (sk, local_idx)
            text = chunk_texts.get(lookup_key, "")
            preview = (entry.get("preview") or text)[:256] or None

            cur.execute("""
                INSERT INTO chunk (source_id, chunk_index, start_page, end_page,
                                   start_time, end_time, approx_words, text, preview)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_id, chunk_index) DO NOTHING
                RETURNING id
            """, (
                sid,
                local_idx,
                entry.get("start_page"),
                entry.get("end_page"),
                entry.get("start_time"),
                entry.get("end_time"),
                entry.get("approx_words"),
                text,
                preview,
            ))
            row = cur.fetchone()
            if row is None:
                cur.execute("SELECT id FROM chunk WHERE source_id = %s AND chunk_index = %s",
                            (sid, local_idx))
                row = cur.fetchone()
            if row:
                chunk_pk_map[global_idx] = str(row[0])

        print(f"  {sk}: {len(entries)} chunks")

    # 4. Embeddings
    print("\nInserting embeddings …")
    emb_rows = [
        (chunk_pk_map[i], embeddings[i].tolist(), EMBED_MODEL)
        for i in range(len(index_entries))
        if i in chunk_pk_map
    ]
    execute_values(
        cur,
        "INSERT INTO embedding (chunk_id, embedding, embedding_model) VALUES %s ON CONFLICT (chunk_id) DO NOTHING",
        emb_rows,
        template="(%s, %s::vector, %s)",
    )
    print(f"  {len(emb_rows)} embeddings inserted")

    # 5. Rebuild HNSW index
    print("\nRebuilding HNSW index …")
    cur.execute("REINDEX INDEX idx_embedding_cosine;")

    conn.commit()
    cur.close()
    conn.close()
    print("\nDone. All data loaded into Azure PostgreSQL.")


if __name__ == "__main__":
    main()
