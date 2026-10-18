# International Credit Risk Rating System

Turns scanned financial statements into a credit rating. The user uploads a
balance sheet, an income statement and a cash flow statement. OCR and an LLM
extract them into tables. The user reviews and edits the tables, and the system
computes financial ratios and a score with charts and a summary.

Project write-up: [PROJECT_SLIDES.md](PROJECT_SLIDES.md)

## About this repository

This is a **submission version**. The core of the system is proprietary and
is left out:

- the OCR and table extraction pipeline (table detection, structure
  recognition, cell OCR)
- the LLM prompts and line-item mapping
- the ratio formulas, indicator weights, scoring bands and rating logic
- the storage service and the training data

What is included:

| Part | Location | Contents |
|---|---|---|
| Frontend | `frontend/` | Full React + TypeScript (Vite) app: the guided wizard, editable tables, charts and summary |
| API surface | `api/main.py`, `api/schemas.py` | Every FastAPI endpoint and its request and response models |
| Service interface | `api/services.py` | Function signatures only; each raises `NotImplementedError` |

The backend here does not run on its own. A live demo or a walkthrough of the
full system is available on request.

## Stack

- React 19, TypeScript, Vite, Zustand
- FastAPI and Pydantic (compute API), FastAPI and SQLAlchemy with Postgres (storage)
- PaddleOCR and YOLO table detection, Gemini or OpenAI for cleanup and mapping
- Docker Compose for the full deployment

## Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI loads on <http://localhost:5173>. It needs the full backend to fetch
data, so without it the screens show their empty and error states.
