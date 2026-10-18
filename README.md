# International Credit Risk Rating System

OCR-based credit scoring app with three parts: `ocr` for PDF/image extraction, `api` for scoring and analysis, and `frontend` for the React UI.

## Project Layout
- `frontend/` React + TypeScript app
- `api/` FastAPI compute API
- `db_api/` storage API and PostgreSQL helpers
- `src/`, `fastapi_app.py`, `requirements-docker.txt` OCR extraction service
- `tests/` backend tests

## Run With Docker
```bash
copy .env.example .env
docker compose up -d --build
```

Open:
- App: `http://localhost:8080`
- API docs: `http://localhost:8002/docs`
- DB API docs: `http://localhost:8001/docs`
- OCR docs: `http://localhost:8000/docs`

Useful commands:
```bash
docker compose ps
docker compose logs -f api
docker compose down
docker compose down -v
```

## Local Development
```bash
pip install -r requirements.txt
pip install -r requirements-docker.txt
npm install
npm --prefix frontend install
npm run db
npm run dev
```

`npm run dev` starts the compute API on `:8002` and the frontend on `:5173`. The OCR service can run separately with:

```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
```

## Testing
```bash
pytest tests
npm --prefix frontend run lint
npm --prefix frontend run build
```

## Production Notes
- Use Docker Compose for deployment: `docker compose up -d --build`
- Set `USE_SAVED_RESPONSE=1` to run without live OCR/LLM calls.
- Set `USE_SAVED_RESPONSE=0` and provide `OPENAI_API_KEY` when using live extraction.
- Inside containers, the API talks to OCR at `http://ocr:8000`.

## License
Copyright (c) 2026 Sourav Saha, Team ONNESHX. All rights reserved.
 
This is proprietary software. The source code is visible for review and evaluation only. Copying, modifying, distributing, or using it in any product or service requires prior written permission. See the [LICENSE](LICENSE) file for details.
