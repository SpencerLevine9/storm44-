from fastapi import APIRouter, HTTPException
from app.schemas.quizzes import QuizRequest, QuizResponse, QuizQuestion
from machine_learning.ingest_pipeline.store.answer import generate_quiz_structured

router = APIRouter()


@router.post("/quizzes", response_model=QuizResponse)
def generate_quiz(req: QuizRequest) -> QuizResponse:
    try:
        result = generate_quiz_structured(req.topic, count=req.count)
        questions = [QuizQuestion(**q) for q in result.get("questions", [])]
        return QuizResponse(questions=questions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))