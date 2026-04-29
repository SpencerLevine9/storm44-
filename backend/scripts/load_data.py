"""
One-shot script: loads pre-computed chunks + embeddings from
backend/data/embeddings/ into the Azure PostgreSQL database (UUID schema).

Run from the repo root:
    python backend/scripts/load_data.py
"""

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import psycopg2
from psycopg2.extras import execute_values

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "backend" / "data" / "embeddings"
ENV_FILE = ROOT / "backend" / ".env"


def load_env(path: Path) -> dict:
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


env = load_env(ENV_FILE)
DATABASE_URL = env["DATABASE_URL"]

# ---------------------------------------------------------------------------
# Load raw files
# ---------------------------------------------------------------------------
print("Loading embeddings.npy …")
embeddings = np.load(DATA / "embeddings.npy")
print(f"  {embeddings.shape[0]} embeddings, dim {embeddings.shape[1]}")

print("Loading chunks_index.jsonl …")
index_entries = []
with open(DATA / "chunks_index.jsonl") as f:
    for line in f:
        index_entries.append(json.loads(line))
assert len(index_entries) == embeddings.shape[0], "index / embedding count mismatch"

print("Loading metadata files …")
metadata = {}
for p in (DATA / "metadata").glob("*.json"):
    metadata[p.stem] = json.loads(p.read_text())

print("Loading chunk text files …")
chunk_texts: dict[tuple, str] = {}
for p in (DATA / "chunks").glob("*.json"):
    for c in json.loads(p.read_text()):
        if c["source_type"] == "pdf":
            key = (c["source_file"], int(c["chunk_id"]))
        else:
            idx = int(c["chunk_id"].split("_")[-1])
            key = (c["video_id"], idx)
        chunk_texts[key] = c["text"]

# ---------------------------------------------------------------------------
# DB ingestion
# ---------------------------------------------------------------------------
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = False
cur = conn.cursor()

# 1. System user ---------------------------------------------------------
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

# 2. Sources -------------------------------------------------------------
print("\nInserting sources …")
source_id_map: dict[str, str] = {}   # stem → UUID string

for stem, meta in metadata.items():
    if meta["source_type"] == "pdf":
        title = stem.replace("_", " ")
        cur.execute("""
            INSERT INTO source (user_id, title, source_type, source_path,
                                output_text_path, num_pages, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'ready')
            RETURNING id
        """, (
            user_id,
            title,
            "pdf",
            meta.get("source_file"),
            meta.get("output_text_file"),
            meta.get("num_pages"),
        ))
    else:
        title = meta.get("title", stem)
        cur.execute("""
            INSERT INTO source (user_id, title, source_type, video_id,
                                video_url, transcript_source,
                                num_segments, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'ready')
            RETURNING id
        """, (
            user_id,
            title,
            "youtube",
            meta.get("video_id"),
            meta.get("url"),
            meta.get("transcript_source"),
            meta.get("num_segments"),
        ))
    source_id_map[stem] = str(cur.fetchone()[0])
    print(f"  {stem} → {source_id_map[stem]}")

# source_key (pdf filename or video_id) → UUID
source_key_map: dict[str, str] = {}
for stem, sid in source_id_map.items():
    meta = metadata[stem]
    if meta["source_type"] == "pdf":
        source_key_map[meta["source_file"].split("/")[-1]] = sid
    else:
        source_key_map[meta["video_id"]] = sid

# 3. Chunks --------------------------------------------------------------
print("\nInserting chunks …")
chunk_id_map: dict[int, str] = {}   # global embedding index → chunk UUID

by_source: dict[str, list] = defaultdict(list)
for i, entry in enumerate(index_entries):
    sk = entry["source_file"] if entry["source_type"] == "pdf" else entry["video_id"]
    by_source[sk].append((i, entry))

for sk, entries in by_source.items():
    sid = source_key_map[sk]
    for global_idx, entry in entries:
        if entry["source_type"] == "pdf":
            local_idx = int(entry["chunk_id"])
            lookup_key = (sk, local_idx)
        else:
            local_idx = int(entry["chunk_id"].split("_")[-1])
            lookup_key = (sk, local_idx)

        text = chunk_texts.get(lookup_key, "")
        preview = (entry.get("preview") or "")[:256] or None
        cur.execute("""
            INSERT INTO chunk (source_id, chunk_index, start_page, end_page,
                               start_time, end_time, approx_words, text, preview)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        chunk_id_map[global_idx] = str(cur.fetchone()[0])

    print(f"  {sk}: {len(entries)} chunks inserted")

# 4. Embeddings ----------------------------------------------------------
print("\nInserting embeddings …")
emb_rows = [
    (chunk_id_map[i], embeddings[i].tolist(), "all-MiniLM-L6-v2")
    for i in range(len(index_entries))
]
execute_values(
    cur,
    "INSERT INTO embedding (chunk_id, embedding, embedding_model) VALUES %s",
    emb_rows,
    template="(%s, %s::vector, %s)",
)
print(f"  {len(emb_rows)} embeddings inserted")

# 5. Rebuild HNSW index --------------------------------------------------
print("\nRebuilding HNSW index …")
cur.execute("REINDEX INDEX idx_embedding_cosine;")

conn.commit()
cur.close()
conn.close()

print("\nDone. All data stored in Azure PostgreSQL.")
print("\nSource UUIDs:")
for stem, sid in source_id_map.items():
    print(f"  {stem}: {sid}")
