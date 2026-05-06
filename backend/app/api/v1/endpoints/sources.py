import asyncio
import tempfile
from pathlib import Path
from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile

from app.api.deps import get_db_connection
from app.db import crud
from app.db.database import get_pool
from machine_learning.ingest_pipeline.extract_text.pdfs import extract_pdf_text
from machine_learning.ingest_pipeline.extract_text.videos import (
    extract_video_id,
    fetch_transcript_text,
)
from machine_learning.ingest_pipeline.process.chunk import (
    Page,
    make_chunks_from_pages,
    split_into_pages,
)
from machine_learning.ingest_pipeline.process.embed import embed_texts_local

USER_ID = UUID("00000000-0000-0000-0000-000000000001")
EMBEDDING_MODEL = "MiniLM-L6-v2"

router = APIRouter()


def _run_in_executor(fn, *args):
    """Run a blocking function in the default thread pool."""
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, fn, *args)


def _embed(texts: list[str]):
    return embed_texts_local(texts)


# ---------------------------------------------------------------------------
# POST /upload/pdf
# ---------------------------------------------------------------------------

@router.post("/upload/pdf")
async def upload_pdf(
    file: UploadFile,
    title: str = Form(...),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    tmp_path = None
    try:
        suffix = Path(file.filename or "upload").suffix or ".pdf"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = Path(tmp.name)

        extracted = await _run_in_executor(extract_pdf_text, tmp_path)
        pages = split_into_pages(extracted["full_text"])

        if not pages:
            # Fallback: treat full text as a single page
            pages = [Page(page_num=1, text=extracted["full_text"])]

        raw_chunks = make_chunks_from_pages(pages, title)

        if not raw_chunks:
            raise HTTPException(status_code=422, detail="PDF produced no usable text chunks.")

        texts = [c["text"] for c in raw_chunks]
        vectors = await _run_in_executor(_embed, texts)

        chunks = [
            {
                "chunk_index": i,
                "text": c["text"],
                "preview": c["text"][:256],
                "start_page": c.get("start_page"),
                "end_page": c.get("end_page"),
                "approx_words": c.get("approx_words"),
            }
            for i, c in enumerate(raw_chunks)
        ]
        embeddings = [v.tolist() for v in vectors]

        pool = get_pool()
        source_id = await crud.ingest_source(
            pool,
            user_id=USER_ID,
            title=title,
            source_type="pdf",
            chunks=chunks,
            embeddings=embeddings,
            embedding_model=EMBEDDING_MODEL,
            metadata={
                "source_path": title,
                "num_pages": len(pages),
            },
        )

        return {"source_id": str(source_id)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if tmp_path and tmp_path.exists():
            tmp_path.unlink()


# ---------------------------------------------------------------------------
# POST /upload/youtube
# ---------------------------------------------------------------------------

@router.post("/upload/youtube")
async def upload_youtube(
    payload: dict,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    url: str = payload.get("url", "").strip()
    title: str = payload.get("title", "").strip()

    if not url:
        raise HTTPException(status_code=400, detail="url is required.")

    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid or unsupported YouTube URL.")

    transcript_data = await _run_in_executor(fetch_transcript_text, video_id)
    if transcript_data is None:
        raise HTTPException(
            status_code=400,
            detail="Could not fetch transcript. The video may have no captions.",
        )

    raw_text = transcript_data["text"]
    segments = transcript_data.get("segments", [])

    if not title:
        title = url

    # Chunk the flat transcript text as a single synthetic page
    pages = [Page(page_num=1, text=raw_text)]
    raw_chunks = make_chunks_from_pages(pages, url)

    if not raw_chunks:
        raise HTTPException(status_code=422, detail="Transcript produced no usable chunks.")

    texts = [c["text"] for c in raw_chunks]
    vectors = await _run_in_executor(_embed, texts)

    # Map each chunk to its start/end time using character offsets in the transcript.
    # Build a cumulative character offset list for each segment line in raw_text.
    seg_offsets: list[tuple[int, float, float]] = []  # (char_start, start_time, end_time)
    cursor = 0
    for seg in segments:
        seg_text = seg.get("text", "").strip()
        if not seg_text:
            continue
        start_t = float(seg.get("start", 0.0))
        duration = float(seg.get("duration", 0.0)) if seg.get("duration") is not None else 0.0
        seg_offsets.append((cursor, start_t, start_t + duration))
        cursor += len(seg_text) + 1  # +1 for the newline joining segments

    def _find_time_for_offset(char_pos: int) -> tuple[float | None, float | None]:
        if not seg_offsets:
            return None, None
        best_start, best_end = seg_offsets[0][1], seg_offsets[0][2]
        for (off, st, et) in seg_offsets:
            if off <= char_pos:
                best_start, best_end = st, et
            else:
                break
        return best_start, best_end

    # Accumulate chunk char offsets by scanning raw_text for each chunk's text
    chunks = []
    search_start = 0
    for i, c in enumerate(raw_chunks):
        chunk_text = c["text"]
        pos = raw_text.find(chunk_text[:40], search_start)
        if pos == -1:
            pos = search_start
        start_time, end_time = _find_time_for_offset(pos)
        search_start = pos + 1
        chunks.append({
            "chunk_index": i,
            "text": chunk_text,
            "preview": chunk_text[:256],
            "approx_words": c.get("approx_words"),
            "start_time": start_time,
            "end_time": end_time,
        })

    embeddings = [v.tolist() for v in vectors]

    pool = get_pool()
    source_id = await crud.ingest_source(
        pool,
        user_id=USER_ID,
        title=title,
        source_type="youtube",
        chunks=chunks,
        embeddings=embeddings,
        embedding_model=EMBEDDING_MODEL,
        metadata={
            "video_id": video_id,
            "video_url": url,
            "transcript_source": "youtube_transcript_api",
            "num_segments": len(segments),
        },
    )

    if segments:
        await crud.insert_video_segments(conn, source_id, segments)

    return {"source_id": str(source_id)}


# ---------------------------------------------------------------------------
# GET /youtube-title
# ---------------------------------------------------------------------------

@router.get("/youtube-title")
async def youtube_title(url: str):
    video_id = extract_video_id(url)
    if not video_id:
        raise HTTPException(status_code=400, detail="Invalid or unsupported YouTube URL.")

    # youtube-transcript-api 1.x uses instance API; title not exposed — fall back to video_id
    def _fetch_title(vid: str) -> str | None:
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            api = YouTubeTranscriptApi()
            tl = api.list(vid)
            return getattr(tl, "video_title", None)
        except Exception:
            return None

    title = await _run_in_executor(_fetch_title, video_id)

    if not title:
        # Fall back to video_id so the frontend always gets something
        title = video_id

    return {"title": title}


# ---------------------------------------------------------------------------
# DELETE /delete/{source_id}
# ---------------------------------------------------------------------------

@router.delete("/delete/{source_id}")
async def delete_source(
    source_id: str,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    try:
        uid = UUID(source_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid source_id format.")

    await crud.delete_source(conn, uid)
    return {"deleted": True}
