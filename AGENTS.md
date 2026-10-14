# Repository Guidelines

## Project Structure & Module Organization
This repository is a Python project centered on table extraction and credit-risk document processing. Main entry points live at the root (`app.py`, `api.py`, `main.py`). Core processing code is under `src/`, with utility helpers in `src/utils/`. Experimental and analysis work lives in `notebooks/` and `bank_statement_analysis/`. Generated artifacts and run outputs appear in `runs/` and `src/output/`; avoid treating these as source files.

## Build, Test, and Development Commands
There is no formal build system in the repo, so development is typically run directly with Python.

- `pip install -r requirement.txt` installs the project dependencies.
- `python app.py` starts the main application if you are working on the UI/serving flow.
- `python api.py` runs the API-focused entry point when adjusting endpoints.
- `python main.py` is useful for local pipeline or orchestration checks.

If you add a test suite, prefer `pytest` and keep the command in this file up to date.

## Coding Style & Naming Conventions
Use standard Python style: 4-space indentation, `snake_case` for functions and variables, and `PascalCase` for classes. Keep filenames descriptive and module-focused, matching the current pattern in `src/` such as `GetDataFromTable.py` or `DetectTable.py`. Prefer small, explicit functions over large implicit scripts. There is no repo-wide formatter configured, so keep edits consistent with surrounding code.

## Testing Guidelines
Automated tests are not currently checked into the repository. When adding tests, place them in a dedicated `tests/` directory and name files `test_*.py`. Focus on deterministic checks for parsing, table detection, and data transformation logic. For notebook work, validate results with a small sample input before scaling up.

## Commit & Pull Request Guidelines
Recent commits are short, lower-case, and sometimes informal, often describing a single change. Follow the same spirit, but make messages clearer when possible, for example: `add table parsing fallback` or `fix api endpoint response`.

Pull requests should include a brief summary, the files or pipeline stage affected, and any verification steps you ran. Add screenshots or sample outputs when changes affect extracted tables, generated PDFs, or UI behavior.

## Data & Artifact Notes
Treat datasets in `bank_statement_analysis/` and generated images or PDFs as local working artifacts unless they are intentionally curated examples. Do not commit large run outputs unless they are required for reproducibility.
