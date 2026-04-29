from fastapi import APIRouter, HTTPException
from app.schemas.flashcards import FlashcardRequest, FlashcardResponse, Flashcard
from machine_learning.ingest_pipeline.store.answer import generate_flashcards_structured

router = APIRouter()


@router.post("/flashcards", response_model=FlashcardResponse)
def generate_flashcards(req: FlashcardRequest) -> FlashcardResponse:
    try:
        result = generate_flashcards_structured(req.topic, count=req.count)
        cards = [Flashcard(**card) for card in result.get("cards", [])]
        return FlashcardResponse(cards=cards)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))