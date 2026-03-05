# this file is for the top k chunks

from __future__ import annotations
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

REPO_ROOT = Path(__file__).resolve().parents[2]  # machine_learning/ingest_pipeline/store -> machine_learning
EMB_DIR = REPO_ROOT / "artifacts" / "embeddings"

EMB_NPY = EMB_DIR / "embeddings.npy"
META_JSONL = EMB_DIR / "chunks_index.jsonl"

# Where your chunk text lives (so we can show the actual chunk content)
CHUNKS_DIR = REPO_ROOT / "artifacts" / "chunks"


def embed_query_local(query: str) -> np.ndarray:
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    v = model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
    return v.astype(np.float32)[0]


def load_index() -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    if not EMB_NPY.exists():
        raise FileNotFoundError(f"Missing {EMB_NPY}. Run embed.py first.")
    if not META_JSONL.exists():
        raise FileNotFoundError(f"Missing {META_JSONL}. Run embed.py first.")

    emb = np.load(EMB_NPY)
    meta: List[Dict[str, Any]] = []
    with META_JSONL.open("r", encoding="utf-8") as f:
        for line in f:
            meta.append(json.loads(line))

    if len(meta) != emb.shape[0]:
        raise ValueError(f"Metadata count ({len(meta)}) != embedding rows ({emb.shape[0]}).")

    return emb, meta

def format_time(seconds: Any) -> str:
    if seconds is None:
        return "unknown"
    total_seconds = int(float(seconds))
    minutes = total_seconds // 60
    secs = total_seconds % 60
    return f"{minutes}:{secs:02d}"

def find_chunk_text(meta: Dict[str, Any]) -> str:
    """
    Find the full chunk text by reading the correct chunk file and matching chunk_id.
    Works for both PDF and YouTube chunks.
    """
    source_type = meta.get("source_type")
    chunk_id = meta.get("chunk_id")

    if chunk_id is None:
        return "[Missing chunk_id]"

    chunk_path = None

    if source_type == "youtube":
        # Example chunk_id: Video_1_chunk_003 -> file Video_1_chunks.json
        chunk_id_str = str(chunk_id)
        if "_chunk_" not in chunk_id_str:
            return "[Invalid YouTube chunk_id format]"
        base = chunk_id_str.split("_chunk_")[0]
        chunk_path = CHUNKS_DIR / f"{base}_chunks.json"

    else:
        # PDF path
        # source_file example: Intro_CS_ch1.pdf -> Intro_CS_ch1_chunks.json
        source_file = meta.get("source_file")
        if source_file:
            base = Path(source_file).stem
            chunk_path = CHUNKS_DIR / f"{base}_chunks.json"
        else:
            # fallback: try deriving from chunk_id if source_file is missing
            chunk_id_str = str(chunk_id)
            if "_chunk_" in chunk_id_str:
                base = chunk_id_str.split("_chunk_")[0]
                chunk_path = CHUNKS_DIR / f"{base}_chunks.json"

    if chunk_path is None or not chunk_path.exists():
        return "[Chunk text file not found]"

    data = json.loads(chunk_path.read_text(encoding="utf-8"))
    for c in data:
        if str(c.get("chunk_id")) == str(chunk_id):
            return (c.get("text") or "").strip()

    return "[Chunk id not found in chunk file]"

def top_k(query: str, k: int = 5) -> List[Dict[str, Any]]:
    emb, meta = load_index()
    qv = embed_query_local(query)

    # Because both emb and qv are normalized, cosine sim = dot product
    sims = emb @ qv  # shape: (N,)
    idx = np.argsort(-sims)[:k]

    results = []
    for rank, i in enumerate(idx, start=1):
        m = meta[int(i)]
        source_type = m.get("source_type")

        results.append(
            {
                "rank": rank,
                "score": float(sims[int(i)]),

                # common
                "source_type": source_type,
                "chunk_id": m.get("chunk_id"),
                "text": find_chunk_text(m),

                # PDF fields
                "source_file": m.get("source_file"),
                "start_page": m.get("start_page"),
                "end_page": m.get("end_page"),

                # YouTube fields
                "title": m.get("title"),
                "url": m.get("url"),
                "video_id": m.get("video_id"),
                "start_time": m.get("start_time"),
                "end_time": m.get("end_time"),
            }
        )
    return results

def main():
    query = input("Question: ").strip()
    if not query:
        print("No query entered.")
        return

    results = top_k(query, k=5)

    print("\nTop matches:\n")
    for r in results:
        if r["source_type"] == "youtube":
            start_str = format_time(r.get("start_time"))
            end_str = format_time(r.get("end_time"))
            print(
                f"[{r['rank']}] score={r['score']:.4f}  "
                f"{r.get('title')}  chunk={r['chunk_id']}  "
                f"time={start_str}-{end_str}"
            )
            print(f"URL: {r.get('url')}")
        else:
            print(
                f"[{r['rank']}] score={r['score']:.4f}  "
                f"{r.get('source_file')}  chunk={r['chunk_id']}  "
                f"pages={r.get('start_page')}-{r.get('end_page')}"
            )

        print(r["text"][:800].replace("\n", " ") + ("..." if len(r["text"]) > 800 else ""))
        print("-" * 80)

if __name__ == "__main__":
    main()