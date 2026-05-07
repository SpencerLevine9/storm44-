from fastapi import APIRouter, HTTPException
from app.schemas.ask import AskRequest, AskResponse, Citation

# 1. Adds GET /api/v1/ask/models
# 2. Validates that the requested model is allowed
# 3. Passes req.model into answer_question_structured()
# 4. Returns model_used back to the frontend

# Imports the ML pipeline
from machine_learning.ingest_pipeline.store.answer import (
    answer_question_structured,
    get_allowed_tutor_models,
    get_tutor_models,
)

router = APIRouter()


@router.get("/ask/models")
def get_tutor_model_options():
    primary_model, fallback_model = get_tutor_models()

    return {
        "default_model": primary_model,
        "fallback_model": fallback_model,
        "allowed_models": sorted(get_allowed_tutor_models()),
    }


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:
    try:
        allowed_models = get_allowed_tutor_models()

        if req.model and req.model not in allowed_models:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": f"Model '{req.model}' is not allowed.",
                    "allowed_models": sorted(allowed_models),
                },
            )

        result = answer_question_structured(
            req.query,
            k=req.top_k,
            requested_model=req.model,
        )

        citations = [Citation(**c) for c in result.get("citations", [])]

        return AskResponse(
            answer=result.get("answer", ""),
            citations=citations,
            model_used=result.get("model_used"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))