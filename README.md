# Storm44

Storm44 is an AI-powered study workspace that helps students turn learning materials into interactive study support. Users can add course sources such as PDFs, YouTube videos, or notes, then use an AI tutor to ask questions grounded in those materials.

The goal of Storm44 is to provide a NotebookLM-style study experience with source-based answers, citations, flashcards, quizzes, and future study tools.

---

## Overview

Storm44 is built around a retrieval-augmented generation pipeline. Study materials are processed into text chunks, converted into embeddings, and retrieved when the user asks a question. The AI tutor then uses the retrieved context to generate a grounded answer instead of answering from general model knowledge alone.

Current focus areas include:

- Source-grounded AI tutor responses
- Local embedding-based retrieval
- PDF and YouTube study material ingestion
- Citation-aware responses
- Tutor model switching
- Flashcard and quiz generation workflows

---

## Features

### Implemented / Working

- AI study tutor interface
- Backend `/api/v1/ask` endpoint for source-grounded questions
- Retrieval from preprocessed study source chunks
- Citations returned with tutor responses
- OpenAI-powered answer generation
- Configurable tutor model selection
- Tutor model dropdown in the frontend
- Backend model validation using an allowed model list
- Fallback model support if the selected/primary model fails
- Health check endpoint

### In Progress

- Fully source-grounded flashcard generation
- Fully source-grounded quiz generation
- Connecting uploaded UI sources directly to the retrieval index
- Source selection/scoping for chat requests
- Database persistence for sources, decks, quizzes, and user workspace data
- pgvector-based production retrieval storage

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript / JSX
- CSS modules/files
- `react-markdown`
- `remark-gfm`
- `lucide-react`

### Backend

- Python
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- asyncpg
- pgvector

### AI / Machine Learning

- OpenAI API for answer generation
- Local embedding retrieval
- SentenceTransformers model:
  - `sentence-transformers/all-MiniLM-L6-v2`
- NumPy vector similarity search
- Chunk-based retrieval from processed PDFs and YouTube transcripts

### Data / Storage

Current local artifact-based retrieval uses:

- `machine_learning/artifacts/chunks`
- `machine_learning/artifacts/embeddings`
- `machine_learning/artifacts/metadata`
- `machine_learning/artifacts/text`
- `machine_learning/artifacts/youtube_segments`

Database support is being developed under the backend database modules and pgvector-related dependencies.

---

## System Architecture

```text
User Source Material
        |
        v
PDF / YouTube / Notes Input
        |
        v
Text Extraction + Processing
        |
        v
Chunking
        |
        v
Embedding Generation
        |
        v
Local Vector Index / Future pgvector Storage
        |
        v
Retriever Finds Relevant Chunks
        |
        v
OpenAI Answer Generation
        |
        v
Grounded AI Tutor Response + Citations

```

# AI Tutor Flow

When a user asks the tutor a question:

The frontend sends the question to the FastAPI backend.
The backend calls the retrieval pipeline.
The retriever searches embedded chunks from the study materials.
The top relevant chunks are used as context.
OpenAI generates an answer using only that study context.
The backend returns:
answer text
citations
the model used
The frontend displays the response in the chat panel.

# Tutor Model Switching

Storm44 supports configurable tutor model switching.

The backend exposes:

`GET /api/v1/ask/models`

This returns the default model, fallback model, and allowed tutor models.

The chat endpoint accepts an optional model field:
```
{
  "query": "What is computer science?",
  "top_k": 5,
  "model": "gpt-4.1-mini"
}
```

The backend validates the requested model before using it. If an invalid model is requested, the backend rejects the request. If the selected model fails, the backend can fall back to the configured fallback model.

The frontend includes a Tutor Model dropdown that lets users select between allowed models.

# API Endpoints

## Health Check
```
GET /health

Returns:

{
  "status": "ok"
}
```

# Ask Tutor
```
POST /api/v1/ask

Example request:

{
  "query": "What is computer science?",
  "source_ids": [],
  "top_k": 5,
  "model": "gpt-5-mini"
}
```

Example response:
```
{
  "answer": "Computer science is the study of computing...",
  "citations": [
    {
      "source_id": "Intro_CS_ch1.pdf",
      "chunk_id": "18",
      "snippet": "What Is Computer Science?",
      "start_seconds": null,
      "url": null
    }
  ],
  "model_used": "gpt-5-mini"
}
```

# Tutor Model Options
`GET /api/v1/ask/models`

Example response:
```
{
  "default_model": "gpt-5-mini",
  "fallback_model": "gpt-4.1-mini",
  "allowed_models": ["gpt-4.1-mini", "gpt-5-mini"]
}
```

Project Structure
```
storm44/
|
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── ask.py
│   │   │       │   └── health.py
│   │   │       └── router.py
│   │   ├── db/
│   │   ├── schemas/
│   │   │   ├── ask.py
│   │   │   ├── flashcards.py
│   │   │   └── quizzes.py
│   │   └── main.py
│   └── requirements.txt
|
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── contexts/
│   │   ├── features/
│   │   │   ├── chat/
│   │   │   ├── sources/
│   │   │   └── study-tools/
│   │   ├── pages/
│   │   ├── styles/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
|
├── machine_learning/
│   ├── artifacts/
│   │   ├── chunks/
│   │   ├── embeddings/
│   │   ├── metadata/
│   │   ├── text/
│   │   └── youtube_segments/
│   ├── data/
│   └── ingest_pipeline/
│       ├── extract_text/
│       ├── process/
│       └── store/
│           ├── answer.py
│           ├── retrieve.py
│           └── postgres.py
|
└── README.md
```

# Environment Variables

## Create a backend environment file:

`backend/.env`

Example:

`OPENAI_API_KEY=your_openai_api_key_here`

FRONTEND_ORIGIN=http://localhost:5173

`TUTOR_PRIMARY_MODEL=gpt-5-mini`
`TUTOR_FALLBACK_MODEL=gpt-4.1-mini`
`TUTOR_ALLOWED_MODELS=gpt-5-mini,gpt-4.1-mini`

`EMBED_MODEL=sentence-transformers/all-MiniLM-L6-v2`

# Create a frontend environment file:

`frontend/.env`

Example:

`VITE_BACKEND_API_URL=http://127.0.0.1:8000`

Never commit real API keys to GitHub.

# Backend Setup

From the project root:
```
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Return to the project root and run the backend with:
```
$env:TUTOR_PRIMARY_MODEL="gpt-5-mini"
$env:TUTOR_FALLBACK_MODEL="gpt-4.1-mini"
$env:TUTOR_ALLOWED_MODELS="gpt-5-mini,gpt-4.1-mini"
$env:PYTHONPATH = "$PWD;$PWD\backend"

python -m uvicorn app.main:app --reload --port 8000
```

## Backend will run at:

`http://127.0.0.1:8000`

## Frontend Setup

From the project root:
```
cd frontend
npm install
npm run dev
```

## Frontend will run at:

`http://localhost:5173`
Running the Full Application

# Open two terminals.

## Terminal 1: Backend
```
$env:TUTOR_PRIMARY_MODEL="gpt-5-mini"
$env:TUTOR_FALLBACK_MODEL="gpt-4.1-mini"
$env:TUTOR_ALLOWED_MODELS="gpt-5-mini,gpt-4.1-mini"
$env:PYTHONPATH = "$PWD;$PWD\backend"

python -m uvicorn app.main:app --reload --port 8000
```

## Terminal 2: Frontend
```
cd frontend
npm run dev
```

# Then open:
`http://localhost:5173`
Testing the Backend

# Test Health
```
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/health" `
  -Method GET
```

# Test Tutor Models
```
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/ask/models" `
  -Method GET
```

# Test Tutor Ask Endpoint
```
$response = Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/ask" `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"query":"what is computer science?","top_k":3,"model":"gpt-4.1-mini"}'

$response | ConvertTo-Json -Depth 10
```

## Expected response should include:
```
{
  "answer": "...",
  "citations": [...],
  "model_used": "gpt-4.1-mini"
}
Demo Flow
```

# A typical demo flow:

Start the backend.
Start the frontend.
Open the Storm44 workspace.
Select a tutor model from the Tutor Model dropdown.

# Ask a source-related question such as:

What is computer science?
Verify that the tutor returns:
a grounded answer
citations
the model used
Switch to a different tutor model.
Ask the same question again.
Confirm that the UI displays the newly selected model.
Current Limitations

# Storm44 is actively under development. Current limitations include:

The visible uploaded source list and the retrieval artifact index are not fully synchronized yet.
Flashcard and quiz schemas exist, but full source-grounded generation is still being integrated.
The current retrieval pipeline uses local artifacts and is not fully migrated to pgvector.
The frontend still has some placeholder logic for selected source IDs.
Some study tools are UI-complete but still need deeper backend integration.
Real API keys should be moved into environment variables and never stored in source code.
Future Work

# Planned improvements:

Automatically generate flashcards and quizzes from uploaded source material.
Add source selection so users can scope tutor answers to specific PDFs or videos.
Store sources, chats, flashcards, and quizzes in the database.
Move retrieval storage from local artifacts to PostgreSQL + pgvector.
Add better upload-to-ingestion integration.
Improve citation display in the frontend.
Add persistent notebooks and user workspaces.
Add support for handwritten note/image ingestion.
Improve automated tests for tutor, upload, flashcard, and quiz flows.
Team Contributions
Spencer Levine: AI/ML pipeline, retrieval, grounded tutor responses, citations, tutor model switching
Jason: Backend API development and integration
Ethan: Frontend UI and interaction flow
Marcus: Database and pgvector-related development
Git Hygiene

# Before committing, avoid including:
```
.env
backend/.env
frontend/.env
node_modules/
backend/.venv/
__pycache__/
.DS_Store
dist/
build/
```

# Recommended .gitignore additions:
```
.env
backend/.env
frontend/.env
node_modules/
backend/.venv/
__pycache__/
.DS_Store
dist/
build/
Project Status
```

Storm44 currently has a working AI tutor flow with retrieval-grounded answers, citations, and selectable tutor models. The next major milestone is completing source-grounded flashcard and quiz generation so uploaded PDFs and YouTube materials automatically become study tools.
