# Handover

## Status (2026-10-16)

The React migration is complete. Streamlit has been retired:

- Removed `main.py`, `home.py`, `pages/`, `styles.css` and `test2.py`.
- Removed `streamlit`, `streamlit-option-menu`, `streamlit-extras` and the other `streamlit-*` add-ons from `requirements.txt`.

Each old Streamlit page now has a React page in `frontend/src/pages/` (Home, Ocr, BalanceSheet, IncomeSheet, CashflowSheet, Formulas, Parameters, Graphs, Summary). These pages call the FastAPI service in `api/`. See `README.md` for how to run it.

## Known leftovers

These files still `import streamlit` but nothing in `api/` uses them. Delete them or port them:

- `ocr_data.py`
- `source/main_function.py`
- `source/qualitative_calc.py` (also imports `home.QualitativeQuestions`, which is now deleted)

Some comments still mention the old files: `source/api_client.py` (`home.py`), `api/services.py` (`pages/formula.py`) and `frontend/src/components/NavBar.tsx` (`main.py`).
