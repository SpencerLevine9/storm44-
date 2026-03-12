from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Source ──────────────────────────────────────────────────────────

class SourceCreate(BaseModel):
    """Payload sent by the frontend / API when a user adds a new source."""
    user_id: int
    title: str = Field(max_length=512)
    source_type: str = Field(max_length=32)  # 'pdf' | 'youtube' | 'note'
    source_path: Optional[str] = None


class SourceUpdate(BaseModel):
    """Fields that the pipeline updates after extraction finishes."""
    output_text_path: Optional[str] = None
    num_pages: Optional[int] = None
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    transcript_source: Optional[str] = None
    num_segments: Optional[int] = None
    status: Optional[str] = None
    error_message: Optional[str] = None


class SourceInDB(BaseModel):
    """Full source row as stored in Postgres."""
    id: int
    user_id: int
    title: str
    source_type: str
    source_path: Optional[str] = None
    output_text_path: Optional[str] = None
    num_pages: Optional[int] = None
    video_id: Optional[str] = None
    video_url: Optional[str] = None
    transcript_source: Optional[str] = None
    num_segments: Optional[int] = None
    status: str = "processing"
    error_message: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Chunk ───────────────────────────────────────────────────────────

class ChunkCreate(BaseModel):
    """One chunk produced by chunk.py, ready for DB insertion."""
    source_id: int
    chunk_index: int
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    approx_words: Optional[int] = None
    text: str
    preview: Optional[str] = None


class ChunkInDB(BaseModel):
    """Full chunk row as stored in Postgres."""
    id: int
    source_id: int
    chunk_index: int
    start_page: Optional[int] = None
    end_page: Optional[int] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    approx_words: Optional[int] = None
    text: str
    preview: Optional[str] = None

    model_config = {"from_attributes": True}


# ── Video segment ──────────────────────────────────────────────────

class VideoSegmentCreate(BaseModel):
    source_id: int
    text: str
    start_time: float
    duration: Optional[float] = None
    seg_index: int
