# International Credit Risk Rating System

Extracts financial statements from uploaded images (OCR + LLM), lets the user review and edit them, then computes ratios and a credit score.

## Stack

| Part | Location | Port |
|---|---|---|
| React + TypeScript (Vite) frontend | `frontend/` | 5173 dev / 8080 docker |
| FastAPI app service | `api/` (uses `source/`) | 8002 |
| DB API (FastAPI + SQLAlchemy) | `db_api/` | 8001 |
| Postgres | docker `db` | 5433 |

The old Streamlit UI (`main.py`, `home.py`, `pages/`) has been removed; the React app replaces it.

## Local development

```bash
pip install -r requirements.txt
npm install && npm --prefix frontend install
npm run db     # starts postgres + db_api in docker
npm run dev    # uvicorn api on :8002 + vite on :5173
```

Configuration is read from `.env` (not tracked). Set `USE_SAVED_RESPONSE=1` to use `saved_responses/` instead of calling the OCR/LLM backend.

## Deployment

```bash
docker compose up -d --build
```

## Tests

```bash
pytest tests
```
