# Keeps main.py tiny and groups v1 endpoints together


from fastapi import APIRouter
from app.api.v1.endpoints import health, ask, flashcards, quizzes, sources

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(ask.router, tags=["Ask"])
api_router.include_router(flashcards.router, tags=["Flashcards"])
api_router.include_router(quizzes.router, tags=["Quizzes"])
api_router.include_router(sources.router, prefix="/sources", tags=["Sources"])

# This exposes the api_router that main.py will mount at /api/v1.