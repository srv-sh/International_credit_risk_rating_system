# Handover

## Status (2026-10-16)

The React migration is complete. Streamlit has been retired:

- Removed `main.py`, `home.py`, `pages/`, `styles.css` and `test2.py`.
- Removed `streamlit`, `streamlit-option-menu`, `streamlit-extras` and the other `streamlit-*` add-ons from `requirements.txt`.

Each old Streamlit page now has a React page in `frontend/src/pages/` (Home, Ocr, BalanceSheet, IncomeSheet, CashflowSheet, Formulas, Parameters, Graphs, Summary). These pages call the FastAPI service in `api/`. See `README.md` for how to run it.

## UI rework (branch `ui-rework`)

The flow is now a wizard. `frontend/src/flow.ts` is the single source of truth for
the order of steps and for which step is reachable:

    Applicant -> Balance sheet -> Income statement -> Cash flow
              -> Weights -> Indicators -> Analysis -> Summary

Things worth knowing before you touch it:

- **The rating is quantitative only, out of 60.** The qualitative questionnaire
  (40 points) is no longer in the flow. No backend change was needed for this:
  `POST /score` without a `qualitative` body already returns a result out of 60.
- **The score is calculated on the Indicators step**, on Continue. It used to be
  calculated by the qualitative page, which is why that page had to go somewhere.
- **OCR and Parameters are off the flow but still work.** They are not in the nav
  and not in `STEPS`, but `/ocr` and `/parameters` still resolve and the endpoints
  behind them are untouched. Parameters shows a warning that scoring from there
  produces a rating out of 100 that will not match the rest of the app.
- **There is one navigation surface and one pair of Back/Continue buttons.**
  `StepNav` is the rail, `FlowFooter` is the footer. Pages do not add their own
  Next links. The rail is hidden on the first step because every later step reads
  data that only the first step can produce.
- `frontend/src/components/blocks/` holds four components ported from
  [bencho.dev](https://bencho.dev) (MIT): the upload dropzone, the radial gauge,
  the stacked bars and the toast stack. They use framer-motion and respect
  `prefers-reduced-motion`.

Nothing in `api/`, `source/`, `db_api/` or `json/` was changed by this work apart
from one version bump, so the calculations are the same as before. Verified: the
full chain returns 19.5/60 both before and after, with every per-ratio score
identical.

## Known leftovers

These files still `import streamlit` but nothing in `api/` uses them. Delete them or port them:

- `ocr_data.py`
- `source/main_function.py`
- `source/qualitative_calc.py` (also imports `home.QualitativeQuestions`, which is now deleted)

Some comments still mention the old files: `source/api_client.py` (`home.py`) and `api/services.py` (`pages/formula.py`).

## Open accuracy issues

These are real and were found while testing the rework. None of them is fixed,
because all three need backend changes and this branch deliberately leaves the
backend alone.

1. **The particulars column is chosen by position.** `api/services.py:93` takes
   the first column unless one is literally named `particulars`. If the
   extraction puts an index column first, every line name fails to match, every
   item is read as zero, and a rating is still produced from the zeros. The React
   app currently avoids this only by accident: JavaScript orders integer-like
   object keys first, which happens to push the stray `level_0` column out of the
   way. Call the same API from Python with the raw column order and the whole
   balance sheet reads as zero.
2. **The year column defaults to the first non-particulars column.** On the saved
   cash flow that column is the note reference, which holds no money, so all four
   cash flow items read as zero. The step now warns about this and you can pick
   the right column by hand, but the default is still wrong.
3. **Number parsing misses two common OCR shapes.** Brackets are handled
   correctly (`(1,234)` becomes `-1234`), but `-1,234` written with an en dash and
   trailing-minus accounting style (`1,234-`) both return `None`, which silently
   becomes zero. A one-sided bracket from a truncated scan does the same.

The common thread is that a value that cannot be read becomes zero and the rating
carries on. Making unreadable values visible, rather than silently zero, is the
single highest-value fix.
