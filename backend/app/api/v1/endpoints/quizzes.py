from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_db_connection
from app.db.crud import retrieve_similar_chunks
from app.schemas.quizzes import QuizQuestion, QuizRequest, QuizResponse
from machine_learning.ingest_pipeline.store.answer import (
    build_context,
    generate_quiz_from_context,
)
from machine_learning.ingest_pipeline.store.retrieve import embed_query_local

router = APIRouter()


@router.post("/quizzes", response_model=QuizResponse)
async def generate_quiz(
    req: QuizRequest,
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> QuizResponse:
    try:
        qv = embed_query_local(req.topic)
        source_uuids = [UUID(s) for s in req.source_ids]
        results = await retrieve_similar_chunks(conn, qv.tolist(), source_uuids, k=5)

        if not results:
            return QuizResponse(questions=[])

        for r in results:
            r["title"] = r.get("source_title")
            r["source_file"] = r.get("source_path") or r.get("source_title")
            r["url"] = r.get("video_url")

        context = build_context(results)
        raw_questions = generate_quiz_from_context(req.topic, context, req.count)
        questions = [QuizQuestion(**q) for q in raw_questions]
        return QuizResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))