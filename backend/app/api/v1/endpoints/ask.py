from uuid import UUID

import asyncpg
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_db_connection
from app.db.crud import retrieve_similar_chunks
from app.schemas.ask import AskRequest, AskResponse, Citation
from machine_learning.ingest_pipeline.store.answer import (
    build_context,
    generate_grounded_answer,
)
from machine_learning.ingest_pipeline.store.retrieve import embed_query_local

router = APIRouter()


@router.post("/ask", response_model=AskResponse, response_model_exclude_none=True)
async def ask(
    req: AskRequest,
    conn: asyncpg.Connection = Depends(get_db_connection),
) -> AskResponse:
    if not req.source_ids:
        return AskResponse(
            answer="Please select at least one source to ask a question.",
            citations=[],
        )

    try:
        # Embed query
        qv = embed_query_local(req.query)
        query_embedding = qv.tolist()

        # Parse source UUIDs
        source_uuids = [UUID(s) for s in req.source_ids]

        # Retrieve top-k chunks via pgvector
        results = await retrieve_similar_chunks(conn, query_embedding, source_uuids, req.top_k)

        if not results:
            return AskResponse(
                answer="I could not find any relevant content in the selected sources.",
                citations=[],
            )

        # Normalize keys: DB returns source_title/video_url/source_path,
        # but build_context() expects title/url/source_file
        for r in results:
            r["title"] = r.get("source_title")
            r["source_file"] = r.get("source_path") or r.get("source_title")
            r["url"] = r.get("video_url")

        context = build_context(results)
        answer = generate_grounded_answer(req.query, context)

        citations = [
            Citation(
                source_id=str(r["source_id"]),
                chunk_id=str(r["chunk_id"]),
                snippet=(r.get("text") or "")[:180],
                start_seconds=r.get("start_time") or None,
                url=r.get("video_url") or None,
            )
            for r in results
        ]

        return AskResponse(answer=answer, citations=citations)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
