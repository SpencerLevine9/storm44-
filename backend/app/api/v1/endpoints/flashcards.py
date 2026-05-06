from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_db_connection
from app.db.crud import retrieve_similar_chunks
from app.schemas.flashcards import Flashcard, FlashcardRequest, FlashcardResponse
from machine_learning.ingest_pipeline.store.answer import (
    build_context,
    generate_flashcards_from_context,
)
from machine_learning.ingest_pipeline.store.retrieve import embed_query_local

router = APIRouter()


@router.post("/flashcards", response_model=FlashcardResponse)
async def generate_flashcards(
    req: FlashcardRequest,
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> FlashcardResponse:
    try:
        qv = embed_query_local(req.topic)
        source_uuids = [UUID(s) for s in req.source_ids]
        results = await retrieve_similar_chunks(conn, qv.tolist(), source_uuids, k=5)

        if not results:
            return FlashcardResponse(cards=[])

        for r in results:
            r["title"] = r.get("source_title")
            r["source_file"] = r.get("source_path") or r.get("source_title")
            r["url"] = r.get("video_url")

        context = build_context(results)
        raw_cards = generate_flashcards_from_context(req.topic, context, req.count)
        cards = [Flashcard(**c) for c in raw_cards]
        return FlashcardResponse(cards=cards)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))