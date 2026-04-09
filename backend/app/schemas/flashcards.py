from typing import List
from pydantic import BaseModel, Field

class FlashcardRequest(BaseModel):
    topic: str = Field(..., min_length=1, description="Topic or question to generate flashcards from")
    source_ids: List[str] = Field(default_factory=list, description="Selected sources to use")
    count: int = Field(10, ge=5, le=20, description="Number of flashcards to generate")


class Flashcard(BaseModel):
    front: str = Field(..., description="Front side of the flashcard")
    back: str = Field(..., description="Back side of the flashcard")


class FlashcardResponse(BaseModel):
    cards: List[Flashcard] = Field(default_factory=list, description="Generated flashcards")