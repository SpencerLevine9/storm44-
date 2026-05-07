from __future__ import annotations
import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
import numpy as np

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

REPO_ROOT = Path(__file__).resolve().parents[2]
EMB_DIR = REPO_ROOT / "artifacts" / "embeddings"

EMB_NPY = EMB_DIR / "embeddings.npy"
META_JSONL = EMB_DIR / "chunks_index.jsonl"
CHUNKS_DIR = REPO_ROOT / "artifacts" / "chunks"

STOPWORDS = {
    "what", "is", "a", "an", "the", "in", "on", "of", "to", "and", "or",
    "for", "with", "as", "by", "it", "this", "that", "are", "be", "from",
    "does", "do", "how", "why", "when", "where",
}

_CHUNK_FILE_CACHE: Dict[str, List[Dict[str, Any]]] = {}

# Cache the embedding model instance to avoid reloading it on every query
# implemented this for Data usage / processing minimization
_MODEL_CACHE = None

def embed_query_local(query: str) -> np.ndarray:
    global _MODEL_CACHE
    if _MODEL_CACHE is None:
        from sentence_transformers import SentenceTransformer
        _MODEL_CACHE = SentenceTransformer(MODEL_NAME)

    v = _MODEL_CACHE.encode([query], normalize_embeddings=True, convert_to_numpy=True)
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
    source_type = meta.get("source_type")
    chunk_id = meta.get("chunk_id")

    if chunk_id is None:
        return "[Missing chunk_id]"

    chunk_path = None

    if source_type == "youtube":
        chunk_id_str = str(chunk_id)
        if "_chunk_" not in chunk_id_str:
            return "[Invalid YouTube chunk_id format]"
        base = chunk_id_str.split("_chunk_")[0]
        chunk_path = CHUNKS_DIR / f"{base}_chunks.json"
    else:
        source_file = meta.get("source_file")
        if source_file:
            base = Path(source_file).stem
            chunk_path = CHUNKS_DIR / f"{base}_chunks.json"
        else:
            chunk_id_str = str(chunk_id)
            if "_chunk_" in chunk_id_str:
                base = chunk_id_str.split("_chunk_")[0]
                chunk_path = CHUNKS_DIR / f"{base}_chunks.json"

    if chunk_path is None or not chunk_path.exists():
        return "[Chunk text file not found]"

# Implement a simple in-memory cache to avoid re-reading the same chunk file multiple times
# implemented this for Data usage / processing minimization and speedup on repeated queries that hit the same chunks
    cache_key = str(chunk_path)
    if cache_key not in _CHUNK_FILE_CACHE:
        _CHUNK_FILE_CACHE[cache_key] = json.loads(chunk_path.read_text(encoding="utf-8"))
    data = _CHUNK_FILE_CACHE[cache_key]

    for c in data:
        if str(c.get("chunk_id")) == str(chunk_id):
            return (c.get("text") or "").strip()

    return "[Chunk id not found in chunk file]"

def query_keywords(query: str) -> List[str]:
    return [
        w.lower()
        for w in re.findall(r"[a-zA-Z0-9_]+", query)
        if len(w) > 2 and w.lower() not in STOPWORDS
    ]

def extract_target_phrase(query: str) -> str:
    q = query.strip().lower()
    patterns = [
        r"^what is an? (.+?)\??$",
        r"^what are (.+?)\??$",
        r"^define (.+?)\??$",
        r"^explain (.+?)\??$",
    ]
    for pat in patterns:
        m = re.match(pat, q)
        if m:
            return m.group(1).strip()
    return q

def rerank_score(query: str, text: str, meta: Dict[str, Any], base_sim: float) -> float:
    q = query.lower().strip()
    t = text.lower()
    keywords = query_keywords(query)
    target = extract_target_phrase(query)

    score = base_sim * 10.0

    # keyword overlap
    overlap = sum(1 for w in set(keywords) if w in t)
    score += overlap * 1.2

    # exact target phrase
    if target and target in t:
        score += 7.0

    # penalize definition chunks that do NOT contain the exact target phrase
    if (q.startswith("what is") or q.startswith("what are")) and target and target not in t:
        score -= 4.0

    # special penalty so "computer science" does not get confused with sibling fields
    if target == "computer science":
        if "information science" in t:
            score -= 6.0
        if "data science" in t:
            score -= 6.0

    # definitional bonus
    definitional_patterns = [
        " is a ",
        " is an ",
        " refers to ",
        " means ",
        " is defined as ",
        " is used to ",
    ]
    if any(p in t for p in definitional_patterns):
        score += 2.5

    # strong preference for definition-style chunks on "what is" questions
    if q.startswith("what is") or q.startswith("what are"):
        if any(p in t for p in definitional_patterns):
            score += 2.5

    # prefer PDF slightly for clean definitions
    if meta.get("source_type") == "pdf" and (q.startswith("what is") or q.startswith("what are")):
        score += 2.5

    # slight penalty for youtube on strict definition questions
    if meta.get("source_type") == "youtube" and (q.startswith("what is") or q.startswith("what are")):
        score -= 1.5

    # simple file-aware boosts for your small course corpus
    source_file = (meta.get("source_file") or "").lower()

    if "python" in q and "python" in source_file:
        score += 2.0

    if any(term in q for term in ["computer science", "turing", "machine learning"]) and "cs" in source_file:
        score += 2.0

    if "for loop" in q and "python" in q and "python" in source_file:
        score += 2.0

    # penalize noisy transcript / textbook navigation language
    noisy_patterns = [
        r"what is up guys",
        r"in this video",
        r"chapter outline",
        r"chapter summary",
        r"learning objectives",
        r"by the end of this section",
        r"access for free at",
        r"courtesy of",
    ]
    for pat in noisy_patterns:
        if re.search(pat, t):
            score -= 3.0

    # slight penalty for extremely short or extremely long chunks
    text_len = len(text.strip())
    if text_len < 80:
        score -= 1.0
    elif text_len > 1200:
        score -= 1.5

    return score

def top_k(query: str, k: int = 5, candidate_pool: int = 20) -> List[Dict[str, Any]]:
    emb, meta = load_index()
    qv = embed_query_local(query)

    sims = emb @ qv
    candidate_idx = np.argsort(-sims)[:candidate_pool]

    scored = []
    for i in candidate_idx:
        m = meta[int(i)]
        text = find_chunk_text(m)
        score = rerank_score(query, text, m, float(sims[int(i)]))
        scored.append((score, float(sims[int(i)]), int(i), m, text))

    scored.sort(key=lambda x: (-x[0], -x[1]))

    results = []
    for rank, (_, sim, i, m, text) in enumerate(scored[:k], start=1):
        source_type = m.get("source_type")
        results.append(
            {
                "rank": rank,
                "score": sim,
                "rerank_score": float(_),
                "source_type": source_type,
                "chunk_id": m.get("chunk_id"),
                "text": text,
                "source_file": m.get("source_file"),
                "start_page": m.get("start_page"),
                "end_page": m.get("end_page"),
                "title": m.get("title"),
                "url": m.get("url"),
                "video_id": m.get("video_id"),
                "start_time": m.get("start_time"),
                "end_time": m.get("end_time"),
            }
        )
    return results

# Part of backend process 
def _normalize_source_key(value: Any) -> str:
    value = str(value or "").strip().lower()
    value = value.replace("\\", "/")

    # Keep only filename if a path was passed
    if "/" in value:
        value = value.split("/")[-1]

    return value


def _source_match_candidates(meta: Dict[str, Any]) -> set[str]:
    candidates = set()

    for key in ["source_file", "title", "url", "video_id", "chunk_id"]:
        value = meta.get(key)
        if value:
            normalized = _normalize_source_key(value)
            candidates.add(normalized)

            # Also include filename stem, e.g. Intro_CS_ch1.pdf -> intro_cs_ch1
            try:
                stem = Path(normalized).stem.lower()
                if stem:
                    candidates.add(stem)
            except Exception:
                pass

    return candidates


def get_chunks_for_sources(
    source_ids: List[str],
    max_chunks_per_source: int = 8,
) -> List[Dict[str, Any]]:
    """
    Load chunks that belong to specific uploaded/selected sources.

    The frontend may send a PDF filename, YouTube URL, title, video id, or source label.
    This function tries to match those values against retrieval metadata.
    """
    if not source_ids:
        return []

    _, meta = load_index()

    requested = set()

    for source_id in source_ids:
        normalized = _normalize_source_key(source_id)
        if normalized:
            requested.add(normalized)

            try:
                stem = Path(normalized).stem.lower()
                if stem:
                    requested.add(stem)
            except Exception:
                pass

    if not requested:
        return []

    matched_by_source: Dict[str, List[Dict[str, Any]]] = {}

    for m in meta:
        candidates = _source_match_candidates(m)

        if not candidates.intersection(requested):
            continue

        source_key = (
            m.get("source_file")
            or m.get("video_id")
            or m.get("title")
            or m.get("url")
            or "unknown"
        )

        if source_key not in matched_by_source:
            matched_by_source[source_key] = []

        if len(matched_by_source[source_key]) >= max_chunks_per_source:
            continue

        text = find_chunk_text(m)

        if not text or text.startswith("["):
            continue

        matched_by_source[source_key].append({
            "rank": len(matched_by_source[source_key]) + 1,
            "score": 1.0,
            "rerank_score": 99.0,
            "source_type": m.get("source_type"),
            "chunk_id": m.get("chunk_id"),
            "text": text,
            "source_file": m.get("source_file"),
            "start_page": m.get("start_page"),
            "end_page": m.get("end_page"),
            "title": m.get("title"),
            "url": m.get("url"),
            "video_id": m.get("video_id"),
            "start_time": m.get("start_time"),
            "end_time": m.get("end_time"),
        })

    results: List[Dict[str, Any]] = []

    for chunks in matched_by_source.values():
        results.extend(chunks)

    return results