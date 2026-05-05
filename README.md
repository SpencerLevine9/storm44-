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
