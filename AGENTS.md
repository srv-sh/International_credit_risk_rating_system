# Repository Guidelines

## Project Structure & Module Organization
`frontend/` contains the React + TypeScript UI built with Vite. `api/` is the main FastAPI service and reuses shared business logic from `source/`. `db_api/` is the storage service. Tests live in `tests/`, mostly as Python `pytest` cases. Keep generated artifacts such as `saved_responses/`, `json/`, and `data/` out of the core logic unless you are working on input fixtures or sample outputs.

## Build, Test, and Development Commands
Use the root scripts for the common workflows:

```bash
npm run dev      # start FastAPI on :8002 and the frontend on :5173
npm run db       # start Postgres and db_api with Docker Compose
npm run build    # build the frontend
pytest tests     # run backend tests
```

For frontend-only work, use `npm --prefix frontend run dev`, `build`, or `lint`.

## Coding Style & Naming Conventions
Python code follows standard PEP 8 conventions: 4-space indentation, `snake_case` for functions and modules, and `PascalCase` for classes and Pydantic schemas. TypeScript/React code uses 2-space indentation, `PascalCase` for components, and `camelCase` for variables, hooks, and helpers. Prefer small, focused modules over large files. Run `npm --prefix frontend run lint` before committing UI changes.

## Testing Guidelines
Use `pytest` for Python behavior and keep test names descriptive, such as `test_api.py`. Add tests alongside the code path they cover when practical, and prefer deterministic fixtures over live service calls. If a change affects OCR, saved responses, or scoring logic, include a regression test or a clearly documented manual verification step.

## Commit & Pull Request Guidelines
Recent commits use short, imperative messages, often sentence case, for example: `Rework the frontend into a step wizard`. Keep commit titles concise and action-oriented. Pull requests should explain what changed, why it changed, and how it was verified. Include screenshots or screen recordings for UI updates, and link any related issue or handoff note when available.

## Configuration & Runtime Notes
Copy `.env.example` to `.env` before local or Docker runs. Set `USE_SAVED_RESPONSE=1` to avoid live OCR/LLM calls during development. When pointing the API at a host-based OCR service, use `host.docker.internal`, not `localhost`, from inside containers.
