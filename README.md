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

The app is a wizard: applicant details and images, then the three statements, then
weights, indicators, analysis and summary. The rating is quantitative only, out of
60. See `HANDOVER.md` before changing the flow.

## Running it with docker

This is the quickest way to get everything up, and the only one that needs no
Python or Node installed locally.

```bash
cp .env.example .env     # then edit it if you have an OCR backend and an API key
docker compose up -d --build
```

That starts four containers and the app is on <http://localhost:8080>.

| What | Where |
|---|---|
| App | <http://localhost:8080> |
| Compute API docs | <http://localhost:8002/docs> |
| Storage API docs | <http://localhost:8001/docs> |
| Postgres | localhost:5433 |

Useful commands:

```bash
docker compose ps              # what is running
docker compose logs -f api     # follow one service
docker compose up -d --build frontend   # rebuild after a frontend change
docker compose down            # stop everything (data is kept)
docker compose down -v         # stop and delete the database too
```

With `USE_SAVED_RESPONSE=1` the app never calls the OCR backend or the LLM, so it
runs end to end with no API key. Tick "Use the saved extraction" on the first step.

### Pointing at the OCR service

Uploading real images needs the OCR service, which is a separate deployment and
is not in this repo. It serves `POST /extract`. Set `USE_SAVED_RESPONSE=0` once
you have it.

Watch the host name. The api runs inside a container, so `localhost` there means
the container itself, not your machine. A backend running on your own machine is
reached at `host.docker.internal`, which is what `.env.example` uses:

```
USE_SAVED_RESPONSE=0
BACKEND_URL=http://host.docker.internal:8000
OPENAI_API_KEY=sk-...
```

If the OCR service runs as its own container, add it to `docker-compose.yml` and
use its service name instead, for example `http://ocr:8000`. Either way, restart
the api so it picks the change up:

```bash
docker compose up -d api
```

When the service is down, the first step says so and keeps your files, and you
can still tick "Use the saved extraction" to carry on.

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
