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


def find_chunk_text(source_file: str, chunk_id: int) -> str:
    # Each chunk file is a JSON list. We'll search for the matching chunk_id.
    # source_file examples: Intro_CS_ch1.pdf
    # your chunk json filename examples: Intro_CS_ch1_chunks.json
    base = Path(source_file).stem  # Intro_CS_ch1
    chunk_path = CHUNKS_DIR / f"{base}_chunks.json"

    if not chunk_path.exists():
        return "[Chunk text file not found]"

    data = json.loads(chunk_path.read_text(encoding="utf-8"))
    for c in data:
        if c.get("chunk_id") == chunk_id:
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
        results.append(
            {
                "rank": rank,
                "score": float(sims[int(i)]),
                "source_file": m.get("source_file"),
                "chunk_id": m.get("chunk_id"),
                "start_page": m.get("start_page"),
                "end_page": m.get("end_page"),
                "text": find_chunk_text(m.get("source_file"), int(m.get("chunk_id"))),
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
        print(f"[{r['rank']}] score={r['score']:.4f}  {r['source_file']}  chunk={r['chunk_id']}  pages={r['start_page']}-{r['end_page']}")
        print(r["text"][:800].replace("\n", " ") + ("..." if len(r["text"]) > 800 else ""))
        print("-" * 80)


if __name__ == "__main__":
    main()
