# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Storm44 is an AI study tool that converts YouTube links, PDFs, and handwritten notes into flashcards, quizzes, games, and provides an integrated AI tutor with live feedback. Target users are college students.

## Repository Structure

- **`frontend/`** — Main React 19 + Vite 7 application (the active codebase)
- **`backend/`** — Placeholder (empty `index.js`, not yet implemented)
- **`machine_learning/`** — Python ingestion pipeline (PDF extraction via PyMuPDF, YouTube placeholder, PostgreSQL storage)
- **`AI Study Tool UX/`** — Separate Figma-derived React+TypeScript+Radix UI design prototype (not integrated into main frontend)
- **`ProductSpec.md`** — Full product specification with MVP features and sprint plan

## Development Commands

### Frontend (primary development)
```bash
cd frontend
npm install        # Install dependencies
npm run dev        # Start Vite dev server (port 5173)
npm run build      # Production build
npm run lint       # ESLint
npm run preview    # Preview production build
```

No test runner is configured yet. Tests are currently run via TestSprite MCP (see `frontend/testsprite_tests/`).

## Architecture

### Frontend 3-Panel Layout

The core UI is a resizable 3-panel workspace (`WorkspacePage` → `WorkspaceLayout`):

| Left Panel | Center Panel | Right Panel |
|---|---|---|
| **SourcesPanel** — file list, search, multi-select, scoping | **ChatPanel** — AI chat with streaming responses and citations | **StudyToolsPanel** — tabbed: Flashcards, Quizzes, Mini-games |

Key layout behaviors:
- Panels are resizable with widths persisted to `localStorage`
- Mobile breakpoint at 768px converts panels to bottom drawers
- Fullscreen mode for Study Tools (AR-01)
- Preset 33/67 split for Chat/Study Tools (AR-02)
- `LayoutContext` manages panel collapse, widths, and fullscreen state

### Routing (React Router v7)
- `/` → `WorkspacePage` (main workspace)
- `/settings` → `SettingsPage`

### State Management
Context-based (no Redux/Zustand):
- `LayoutContext` — panel layout state
- `AddSourceContext` — source addition modal state
- `ToastContext` — toast notifications via `useToast` hook

### Component Organization
- `src/components/ui/` — 10 reusable base components (Button, Modal with focus trap, Dropdown, Tabs, Toast, etc.)
- `src/components/layout/` — Header, WorkspaceLayout
- `src/features/` — feature modules: `sources/`, `chat/`, `study-tools/`
- `src/styles/theme.css` — design tokens (iOS-like, primary #007AFF blue)

### Source Addition Flow
Modal overlay with three tabs (`AddSourceModal` → `AddSourceContext`):
- **UploadTab** — file upload (PDF, images)
- **UrlTab** — YouTube/web URL input
- **NoteTab** — manual note creation

### Machine Learning Pipeline
```
machine_learning/ingest_pipeline/
├── extract_text/   # pdfs.py (PyMuPDF), videos.py (placeholder)
├── process/        # chunk.py, embed.py
└── store/          # postgres.py
```
Data resources defined in `machine_learning/data/data_resources.json`.

## Current Integration Status
- Frontend UI is built out but backend is not implemented
- Chat responses are mock-only (no AI streaming connected)
- Source processing and study tool generation are non-functional
- Accessibility basics (keyboard nav, ARIA) are in place
