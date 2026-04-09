from fastapi import APIRouter, HTTPException
from app.schemas.ask import AskRequest, AskResponse, Citation

# Imports the ML pipeline
from machine_learning.ingest_pipeline.store.answer import answer_question_structured

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:

    try:
        result = answer_question_structured(req.query, k=req.top_k)
        
        citations = [Citation(**c) for c in result.get("citations", [])]

        
        return AskResponse(
            answer=result.get("answer", ""),
            citations=citations,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))