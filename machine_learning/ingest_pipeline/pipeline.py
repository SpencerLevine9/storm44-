"""
Storm44 ingestion pipeline.

Runs extraction → chunking → embedding in order.
After extraction and chunking, source/chunk metadata is persisted to Postgres
via postgres_store.  Set SKIP_DB=1 to run without a database.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

# ── Paths ───────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parents[2]  # storm44-/
DATA_RESOURCES = PROJECT_ROOT / "machine_learning" / "data" / "data_resources.json"

ART_TEXT_DIR = PROJECT_ROOT / "machine_learning" / "artifacts" / "text"
ART_META_DIR = PROJECT_ROOT / "machine_learning" / "artifacts" / "metadata"
ART_CHUNKS_DIR = PROJECT_ROOT / "machine_learning" / "artifacts" / "chunks"
ART_SEG_DIR = PROJECT_ROOT / "machine_learning" / "artifacts" / "youtube_segments"

PDF_BASE_DIR = PROJECT_ROOT / "machine_learning"

# ── Imports from sibling packages ──────────────────────────────────

sys.path.insert(0, str(Path(__file__).resolve().parent))

from extract_text.pdfs import extract_pdf_text
from extract_text.videos import (
    extract_video_id,
    fetch_transcript_text,
    safe_filename,
    write_segments_jsonl,
)
from process.chunk import Page, make_chunks_from_pages, split_into_pages, read_text_file
from store.postgres_store import (
    insert_chunks,
    insert_source,
    insert_video_segments,
    update_source,
)

SKIP_DB = os.getenv("SKIP_DB", "0") == "1"
DEFAULT_USER_ID = int(os.getenv("PIPELINE_USER_ID", "1"))


# ── Helpers ─────────────────────────────────────────────────────────

def _load_resources() -> Dict[str, List[Dict[str, str]]]:
    if not DATA_RESOURCES.exists():
        raise FileNotFoundError(f"Missing {DATA_RESOURCES}")
    return json.loads(DATA_RESOURCES.read_text(encoding="utf-8"))


def _ensure_dirs() -> None:
    for d in (ART_TEXT_DIR, ART_META_DIR, ART_CHUNKS_DIR, ART_SEG_DIR):
        d.mkdir(parents=True, exist_ok=True)


# ── PDF pipeline ────────────────────────────────────────────────────

def ingest_pdf(item: Dict[str, str], user_id: int) -> None:
    title = item.get("title", "Untitled PDF")
    rel_path = item.get("file", "")
    pdf_path = PDF_BASE_DIR / rel_path

    if not pdf_path.exists():
        print(f"[SKIP] PDF not found: {pdf_path}")
        return

    print(f"Extracting PDF: {title}")

    # 1. Extract text
    data = extract_pdf_text(pdf_path)
    stem = pdf_path.stem
    txt_path = ART_TEXT_DIR / f"{stem}.txt"
    meta_path = ART_META_DIR / f"{stem}.json"
    txt_path.write_text(data["full_text"], encoding="utf-8")

    num_pages = len(data["pages"])
    meta: Dict[str, Any] = {
        "source_type": "pdf",
        "source_file": str(pdf_path.as_posix()),
        "output_text_file": str(txt_path.as_posix()),
        "num_pages": num_pages,
    }
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    # 2. DB: create source row
    source_id = None
    if not SKIP_DB:
        source_id = insert_source(
            user_id=user_id,
            title=title,
            source_type="pdf",
            source_path=str(pdf_path.as_posix()),
        )
        update_source(
            source_id,
            output_text_path=str(txt_path.as_posix()),
            num_pages=num_pages,
            status="chunking",
        )

    # 3. Chunk
    pages = split_into_pages(data["full_text"])
    source_pdf_name = f"{stem}.pdf"
    chunks = make_chunks_from_pages(pages, source_pdf_name)

    chunk_path = ART_CHUNKS_DIR / f"{stem}_chunks.json"
    chunk_path.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  -> {len(chunks)} chunks written to {chunk_path}")

    # 4. DB: insert chunks
    if not SKIP_DB and source_id is not None:
        insert_chunks(source_id, chunks)
        update_source(source_id, status="ready")

    print(f"  -> done: {title}")


# ── YouTube pipeline ────────────────────────────────────────────────

def ingest_youtube(item: Dict[str, str], user_id: int) -> None:
    title = item.get("title", "youtube_video")
    url = item.get("url", "")
    vid = extract_video_id(url)

    if not vid:
        print(f"[SKIP] Could not parse video id from URL: {url}")
        return

    base = safe_filename(title)
    out_txt = ART_TEXT_DIR / f"{base}.txt"
    out_meta = ART_META_DIR / f"{base}.json"
    out_seg = ART_SEG_DIR / f"{base}.jsonl"

    print(f"Extracting YouTube: {title} ({vid})")

    data = fetch_transcript_text(vid)
    if data is None:
        print(f"[SKIP] No transcript available for {title} ({vid})")
        return

    text = data["text"].strip()
    if not text:
        print(f"[WARN] Empty transcript for {title}")
        return

    segments = data.get("segments", [])
    out_txt.write_text(text, encoding="utf-8")

    meta: Dict[str, Any] = {
        "source_type": "youtube",
        "title": title,
        "url": url,
        "video_id": vid,
        "language": data.get("language"),
        "output_text_file": str(out_txt).replace("\\", "/"),
        "num_segments": len(segments),
        "output_segments_file": str(out_seg).replace("\\", "/"),
        "transcript_source": "youtube_transcript_api",
    }
    out_meta.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    write_segments_jsonl(
        out_seg, segments,
        video_id=vid, title=title, url=url,
        source="youtube_transcript_api",
    )

    # DB: create source row
    source_id = None
    if not SKIP_DB:
        source_id = insert_source(
            user_id=user_id,
            title=title,
            source_type="youtube",
            source_path=url,
        )
        update_source(
            source_id,
            output_text_path=str(out_txt).replace("\\", "/"),
            video_id=vid,
            video_url=url,
            transcript_source="youtube_transcript_api",
            num_segments=len(segments),
            status="chunking",
        )

    # Chunk the transcript
    pages = split_into_pages(text)
    if not pages:
        # No page markers — treat whole text as a single page
        pages = [Page(page_num=1, text=text)]

    chunks = make_chunks_from_pages(pages, f"{base}.txt")
    chunk_path = ART_CHUNKS_DIR / f"{base}_chunks.json"
    chunk_path.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print(f"  -> {len(chunks)} chunks")

    # DB: insert chunks + segments
    if not SKIP_DB and source_id is not None:
        insert_chunks(source_id, chunks)
        insert_video_segments(source_id, segments)
        update_source(source_id, status="ready")

    print(f"  -> done: {title}")


# ── Embedding (still a subprocess — outputs go to files / Azure) ──

def run_embed() -> None:
    print("Running embedding step...")
    subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "machine_learning" / "ingest_pipeline" / "process" / "embed.py")],
        check=True,
    )


# ── Main ────────────────────────────────────────────────────────────

def main() -> None:
    _ensure_dirs()
    resources = _load_resources()
    user_id = DEFAULT_USER_ID

    if SKIP_DB:
        print("SKIP_DB=1 — running without Postgres writes.")

    # PDFs
    for item in resources.get("pdf", []):
        ingest_pdf(item, user_id)

    # YouTube
    for item in resources.get("youtube", []):
        ingest_youtube(item, user_id)

    # Embeddings
    run_embed()

    print("Ingestion pipeline complete.")


if __name__ == "__main__":
    main()
