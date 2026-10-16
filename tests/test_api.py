import pytest
from fastapi.testclient import TestClient

from api import services
from api.main import app

client = TestClient(app)

TABLE = {
    "Particulars": ["Assets", "Total assets", "Total liabilities", "Current assets", "Current liabilities",
                    "Intangible assets", "Inventories", "Trade receivables", "Other receivables", "Non-current assets"],
    "30 June 2023": ["", "90,908,122,246", "80360849262", "51237665010", "70200705508", "1409150269",
                     "21791856287", "16648869492", "(1,103,490,611)", "39670457236"],
    "30 June 2022": ["", "75721816847", "63517124675", "39758263596", "54140334291", "1367550235",
                     "20323249620", "12772253271", "832500769", "35963553250"],
}
ANSWERS = [q["options"][0]["label"] for q in services.list_qualitative_questions()]


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_parse_number():
    assert services.parse_number("1,234") == 1234
    assert services.parse_number("(1,234.5)") == -1234.5
    assert services.parse_number("-5") == -5
    assert services.parse_number("-") is None
    assert services.parse_number("37.1(a)") is None


def test_balance_sheet_default_mapping():
    r = client.post("/balance-sheet/calculate", json={"table": TABLE})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["year_column"] == "30 June 2023"
    assert body["values"]["total assets"] == 90908122246
    assert body["values"]["accounts receivables"] == 16648869492 - 1103490611
    assert body["missing"] == ["long term loan-current portion"]
    assert body["markdown"].startswith("| Particulars | 30 June 2023 |")


def test_statement_custom_mapping_and_year():
    r = client.post("/balance-sheet/calculate", json={
        "table": TABLE, "year_column": "30 June 2022", "mapping": {"total assets": ["total assets"]}})
    assert r.json()["values"]["total assets"] == 75721816847
    assert r.json()["values"]["inventories"] == 0


def test_statement_errors():
    assert client.post("/income/calculate", json={"table": TABLE, "year_column": "1999"}).status_code == 400
    assert client.post("/cashflow/calculate", json={"table": {"a": [1], "b": []}}).status_code == 400


def test_qualitative():
    questions = client.get("/qualitative/questions").json()
    assert len(questions) == 18 and sum(q["max_score"] for q in questions) == 40
    r = client.post("/qualitative/score", json={"answers": ANSWERS})
    assert r.json()["total"] == 40 and r.json()["percentage"] == 100
    bad = client.post("/qualitative/score", json={"answers": ["nope"] * 18})
    assert bad.status_code == 422 and "nope" in bad.json()["detail"]


def test_score_matches_score_calculator():
    values = {"total assets": 100, "total liabilities": 40, "current assets": 60, "current liabilities": 20,
              "revenue": 200, "net profit after tax": 30, "operating profit": 50, "earnings before tax": 40,
              "finance cost": 10, "cost of sales": 100, "inventories": 5, "accounts receivables": 10,
              "cash and cash equivalents at end of year": 25, "cash flows from operating activities": 70}
    r = client.post("/score", json={"values": values})
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["ratios"]) == 16 and body["quantitative_max"] == 60
    assert body["quantitative_total"] == sum(c["score"] for c in body["categories"])
    assert body["overall_total"] == body["quantitative_total"] and body["qualitative"] is None
    dtn = next(x for x in body["ratios"] if x["key"] == "dtn")
    assert dtn["value"] == pytest.approx(40 / 60) and dtn["label"] == "Marginal" and dtn["score"] == 4


def test_score_zero_denominators_and_qualitative():
    r = client.post("/score", json={"values": {}, "qualitative": {"answers": ANSWERS}})
    body = r.json()
    assert r.status_code == 200, r.text
    assert next(x for x in body["ratios"] if x["key"] == "current_ratio")["value"] is None  # infinite
    assert body["overall_max"] == 100
    assert body["overall_total"] == body["quantitative_total"] + 40


def test_formulas():
    formulas = client.get("/formulas").json()
    assert len(formulas) == 16 and sum(f["max_score"] for f in formulas) == 60
    assert all(f["latex"] for f in formulas)


@pytest.mark.parametrize("graph_id", ["summary", "categories", "ratios", "qualitative"])
def test_graphs_from_result(graph_id):
    result = client.post("/score", json={"values": {"total assets": 10, "revenue": 5},
                                         "qualitative": {"answers": ANSWERS}}).json()
    fig = client.post(f"/graphs/{graph_id}", json=result)
    assert fig.status_code == 200, fig.text
    assert fig.json()["data"]


def test_unknown_graph():
    result = client.post("/score", json={"values": {}}).json()
    assert client.post("/graphs/pie", json=result).status_code == 404
    assert client.post("/graphs/qualitative", json=result).status_code == 404


def test_ocr_saved_response():
    if not services.SAVED_OCR_PATH.exists():
        pytest.skip("no saved OCR response")
    r = client.post("/ocr", params={"use_saved": True})
    assert r.status_code == 200, r.text
    assert set(r.json()) == {"bs", "is", "cfs", "source"} and r.json()["bs"]["table"]


def test_ocr_requires_three_files():
    assert client.post("/ocr", params={"use_saved": False}).status_code == 422


def test_cors_preflight():
    r = client.options("/score", headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "POST"})
    assert r.headers["access-control-allow-origin"] == "http://localhost:5173"
