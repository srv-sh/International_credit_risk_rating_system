"""Compute API for the React frontend: OCR, statement calculation, scoring, formulas and graphs.

Storage stays in db_api/ (port 8001). Run from the project root:

    uvicorn api.main:app --reload --port 8002

Docs: http://localhost:8002/docs
"""
import os
from typing import Any, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, File, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

from api import services  # noqa: E402  (after load_dotenv so source/ modules see .env)
from api.schemas import (  # noqa: E402
    Formula, Indicator, OcrResponse, QualitativeQuestion, QualitativeRequest, QualitativeResult,
    ScoreRequest, ScoreResponse, StatementRequest, StatementResult,
)

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

app = FastAPI(title="Credit Risk Compute API", version="1.0.0")
app.add_middleware(
    CORSMiddleware, allow_origins=[o.strip() for o in CORS_ORIGINS if o.strip()],
    allow_methods=["*"], allow_headers=["*"],
)


@app.exception_handler(services.ServiceError)
def service_error(_: Request, exc: services.ServiceError):
    return JSONResponse(status_code=exc.status_code, content={"detail": str(exc)})


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ocr", response_model=OcrResponse, tags=["ocr"])
async def ocr(
    balance_sheet: Optional[UploadFile] = File(None),
    cash_flow: Optional[UploadFile] = File(None),
    income_statement: Optional[UploadFile] = File(None),
    use_saved: Optional[bool] = Query(
        None, description="Return saved_responses/input_data.json instead of calling the OCR backend. "
                          "Defaults to USE_SAVED_RESPONSE from .env."),
):
    """Extract the three statements from images via the OCR backend (BACKEND_URL)."""
    if use_saved is None:
        use_saved = os.getenv("USE_SAVED_RESPONSE", "1") == "1"
    files = [balance_sheet, cash_flow, income_statement]
    if not use_saved and not all(files):
        raise services.ServiceError("Upload balance_sheet, cash_flow and income_statement", 422)
    uploads = [(f.filename, await f.read(), f.content_type) for f in files] if all(files) else []
    return services.run_ocr(uploads, use_saved)


@app.post("/balance-sheet/calculate", response_model=StatementResult, tags=["statements"])
def balance_sheet(body: StatementRequest):
    return services.calculate_statement("bs", **body.model_dump())


@app.post("/income/calculate", response_model=StatementResult, tags=["statements"])
def income(body: StatementRequest):
    return services.calculate_statement("is", **body.model_dump())


@app.post("/cashflow/calculate", response_model=StatementResult, tags=["statements"])
def cashflow(body: StatementRequest):
    return services.calculate_statement("cfs", **body.model_dump())


@app.get("/statements/items", tags=["statements"])
def statement_items() -> dict[str, Any]:
    """Line items each statement provides, and the default particulars mapping."""
    return {"items": services.SHEET_ITEMS, "default_mapping": services.DEFAULT_MAPPING}


@app.get("/qualitative/questions", response_model=list[QualitativeQuestion], tags=["qualitative"])
def qualitative_questions():
    return services.list_qualitative_questions()


@app.post("/qualitative/score", response_model=QualitativeResult, tags=["qualitative"])
def qualitative_score(body: QualitativeRequest):
    return services.score_qualitative(body.answers)


@app.post("/score", response_model=ScoreResponse, tags=["score"])
def final_score(body: ScoreRequest):
    """Ratios, per-ratio scores, category totals and the final rating (quantitative /60, plus qualitative /40)."""
    answers = body.qualitative.answers if body.qualitative else None
    result = services.score(body.values.model_dump(by_alias=True), answers)
    if body.save:
        result["score_id"] = services.save_score(result, body.records.model_dump())
    return result


@app.get("/formulas", response_model=list[Formula], tags=["formulas"])
def formulas():
    return services.list_formulas()


@app.get("/indicators", response_model=list[Indicator], tags=["indicators"])
def indicators():
    return services.list_indicators()


@app.put("/indicators", response_model=list[Indicator], tags=["indicators"])
def update_indicators(body: list[Indicator]):
    """Replace the weights and band points in json/indicators.json; used by every later /score."""
    return services.save_indicators([i.model_dump() for i in body])


@app.get("/graphs", tags=["graphs"])
def graph_ids() -> list[str]:
    return services.GRAPH_IDS


@app.get("/graphs/{graph_id}", tags=["graphs"])
def graph(graph_id: str, score_id: int = Query(..., description="id returned by POST /score with save=true")):
    """Plotly figure JSON (render with react-plotly.js) for a saved score."""
    return services.build_graph(graph_id, services.load_score(score_id))


@app.post("/graphs/{graph_id}", tags=["graphs"])
def graph_from_result(graph_id: str, body: ScoreResponse):
    """Same as GET, but built from a ScoreResponse you already have (no storage needed)."""
    return services.build_graph(graph_id, body.model_dump())
