from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import numpy as np

# ----------------------------
# Config
# ----------------------------
MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
USE_OPENAI = os.getenv("USE_OPENAI", "0") == "1"  # leave as 0 for now

# Paths
REPO_ROOT = Path(__file__).resolve().parents[2]  # machine_learning/ingest_pipeline/process -> machine_learning
CHUNKS_DIR = REPO_ROOT / "artifacts" / "chunks"
OUT_DIR = REPO_ROOT / "artifacts" / "embeddings"
OUT_DIR.mkdir(parents=True, exist_ok=True)

OUT_META_JSONL = OUT_DIR / "chunks_index.jsonl"
OUT_EMB_NPY = OUT_DIR / "embeddings.npy"


def load_chunks() -> List[Dict[str, Any]]:
    chunk_files = sorted(CHUNKS_DIR.glob("*_chunks.json"))
    if not chunk_files:
        raise FileNotFoundError(f"No chunk files found in {CHUNKS_DIR}")

    all_chunks: List[Dict[str, Any]] = []
    for fp in chunk_files:
        data = json.loads(fp.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{fp.name} is not a JSON list")
        all_chunks.extend(data)

    return all_chunks


def embed_texts_local(texts: List[str]) -> np.ndarray:
    # Lazy import so the file loads even if user chooses OpenAI later
    from sentence_transformers import SentenceTransformer

    model = SentenceTransformer(MODEL_NAME)
    vectors = model.encode(
        texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,  # cosine similarity becomes dot product
    )
    return vectors.astype(np.float32)


def embed_texts_openai(texts: List[str]) -> np.ndarray:
    """
    Optional: if you later want OpenAI embeddings.
    Set:
      USE_OPENAI=1
      OPENAI_API_KEY=...
    """
    from openai import OpenAI

    client = OpenAI()
    # Pick a model you want later, e.g. "text-embedding-3-small"
    emb_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

    vectors: List[List[float]] = []
    # batch to avoid huge requests
    batch_size = 128
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        resp = client.embeddings.create(model=emb_model, input=batch)
        vectors.extend([d.embedding for d in resp.data])

    arr = np.array(vectors, dtype=np.float32)
    # normalize to use cosine similarity
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1
    return arr / norms


def main():
    chunks = load_chunks()
    print(f"Found {len(chunks)} chunks across {len(list(CHUNKS_DIR.glob('*_chunks.json')))} files.")

    texts = []
    metas = []

    for c in chunks:
        text = (c.get("text") or "").strip()
        lower = text.lower()

        if not text:
            continue

        if len(text.split()) < 25:
            continue

        bad_patterns = [    # added more patterns for citation quality 
            "access multimedia content",
            "link to learning",
            "review questions",
            "multiple choice",
            "true or false",
            "fill in the blank",
            "chapter review",
            "chapter summary",
            "exploring further",
            "concepts in practice",
            "exercise",
            "key terms",
            "try it",
            "which comment is",
            "where should a blank line",
            "to temporarily prevent a line",
            "what type of error",
            "which would be a good name",
            "final score",
        ]

        if any(pat in lower for pat in bad_patterns):
            continue
        
        # keep metadata for citations later
        metas.append(
            {
                # Common PDF and YouTube
                "chunk_id": c.get("chunk_id"),
                "source_type": c.get("source_type"),   # "pdf" or "youtube"
                "preview": text[:200],

                # PDF specific (safe if missing)
                "source_file": c.get("source_file"),
                "start_page": c.get("start_page"),
                "end_page": c.get("end_page"),
                "approx_words": c.get("approx_words"),

                # YouTube specific (safe if missing)
                "title": c.get("title"),
                "url": c.get("url"),
                "video_id": c.get("video_id"),
                "start_time": c.get("start_time"),
                "end_time": c.get("end_time"),
                "segment_start_idx": c.get("segment_start_idx"),
                "segment_end_idx": c.get("segment_end_idx"),
            }
        )
        texts.append(text)

    print(f"Embedding {len(texts)} non-empty chunks...")

    if USE_OPENAI:
        vectors = embed_texts_openai(texts)
    else:
        vectors = embed_texts_local(texts)

    # Save embeddings
    np.save(OUT_EMB_NPY, vectors)

    # Save metadata as JSONL (one chunk per line)
    with OUT_META_JSONL.open("w", encoding="utf-8") as f:
        for m in metas:
            f.write(json.dumps(m, ensure_ascii=False) + "\n")

    print(f"Saved embeddings -> {OUT_EMB_NPY}")
    print(f"Saved metadata  -> {OUT_META_JSONL}")
    print("Done.")


if __name__ == "__main__":
    main()
