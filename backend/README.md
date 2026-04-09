# Storm44 Backend

FastAPI lives here

This Backend will be responsible for:

- Youtube Video Ingestion
- RAG-based question answering
- Study Tool generation (Quizzes and Flashcards)

## Current Status
Backend File Path - Completed

FastAPI server implementation - Running

Schemas - Completed




## Current Structure

```
backend/
    app/
        api/
        core/
        schemas/
        services/
        rag/
        db/
        utils/
        main.py
    tests/
```

## Requirements

# Run backend

source backend/.venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
