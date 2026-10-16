"""Computation behind the API: statement value resolution, ratios, scoring, qualitative and graphs.

Ratio maths and score bands are reused unchanged from source/calculation.py and source/score_calc.py
so the API rates exactly like the Streamlit pages.
"""
import base64
import io
import json
import math
import os
import re
from pathlib import Path

import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots

from source import api_client
from source.calculation import FinancialCalculator
from source.score_calc import ScoreCalculator

ROOT = Path(__file__).resolve().parent.parent
QUALITATIVE_PATH = ROOT / "json" / "qualitative_ques.json"
INDICATORS_PATH = ROOT / "json" / "indicators.json"
SAVED_OCR_PATH = ROOT / "saved_responses" / "input_data.json"


class ServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


# ---------- line items per statement ----------

SHEET_ITEMS = {
    "bs": [
        "total assets", "total liabilities", "current assets", "current liabilities", "intangible assets",
        "long term loan-current portion", "inventories", "accounts receivables", "non-current assets",
    ],
    "is": [
        "revenue", "net profit after tax", "operating profit", "earnings before tax", "finance cost", "cost of sales",
    ],
    "cfs": [
        "capital work in progress", "cash and cash equivalents at end of year",
        "cash flows from operating activities", "cash flows from financing activities",
    ],
}

# Default particulars per item (from pages/formula.py)
DEFAULT_MAPPING = {
    "total assets": ["Total assets"],
    "total liabilities": ["Total liabilities"],
    "current assets": ["Current assets"],
    "current liabilities": ["Current liabilities"],
    "intangible assets": ["Intangible assets"],
    "long term loan-current portion": [],
    "inventories": ["Inventories"],
    "accounts receivables": ["Trade receivables", "Other receivables"],
    "capital work in progress": ["Payments for capital work-in-progress"],
    "non-current assets": ["Non-current assets"],
    "revenue": ["Revenue"],
    "net profit after tax": ["Profit/(loss) after tax"],
    "operating profit": ["Operating profit"],
    "earnings before tax": ["Profit before tax"],
    "finance cost": ["Net finance costs"],
    "cost of sales": ["Cost of sales"],
    "cash and cash equivalents at end of year": ["Cash and cash equivalents at reporting date"],
    "cash flows from operating activities": ["Net cash from/(used in) operating activities"],
    "cash flows from financing activities": ["Net cash from/(used in) financing activities"],
}


def parse_number(value):
    """'1,234' -> 1234.0, '(1,234)' -> -1234.0, '-' / '' / '37.1(a)' -> None."""
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        return None if math.isnan(value) else float(value)
    text = str(value).strip().replace(",", "").replace(" ", "")
    negative = text.startswith("(") and text.endswith(")")
    if negative:
        text = text[1:-1]
    try:
        number = float(text)
    except ValueError:
        return None
    if math.isnan(number) or math.isinf(number):
        return None
    return -number if negative else number


def _particulars_column(table):
    for col in table:
        if col.strip().lower() == "particulars":
            return col
    return next(iter(table))


def table_to_markdown(table):
    cols = list(table.keys())
    md = "| " + " | ".join(cols) + " |\n"
    md += "| " + " | ".join(["---"] * len(cols)) + " |\n"
    for row in zip(*[table[c] for c in cols]):
        md += "| " + " | ".join(str(v) if v not in ("", None) else " " for v in row) + " |\n"
    return md


def _llm_mapping(markdown, items):
    from source.config import AgentCall  # imported lazily: pulls in langchain and needs OPENAI_API_KEY

    if not os.getenv("OPENAI_API_KEY"):
        raise ServiceError("OPENAI_API_KEY is not set on the backend", 503)
    content = AgentCall(markdown).generate_response(items)
    if not isinstance(content, str) or content.startswith("Error generating response"):
        raise ServiceError(f"LLM call failed: {content}", 502)
    start, end = content.find("{"), content.rfind("}")
    try:
        mapping = json.loads(content[start:end + 1])
    except ValueError:
        raise ServiceError(f"LLM did not return JSON: {content[:300]}", 502)
    return {item: mapping.get(item) for item in items}


def calculate_statement(sheet, table, mapping=None, year_column=None, use_llm=False):
    if not table:
        raise ServiceError("Table is empty")
    lengths = {len(v) for v in table.values()}
    if len(lengths) != 1:
        raise ServiceError("All table columns must have the same number of rows")

    particulars_col = _particulars_column(table)
    value_cols = [c for c in table if c != particulars_col]
    if year_column is None:
        if not value_cols:
            raise ServiceError("Table has no value columns")
        year_column = value_cols[0]
    elif year_column not in value_cols:
        raise ServiceError(f"Unknown year_column '{year_column}'. Available: {value_cols}")

    items = SHEET_ITEMS[sheet]
    markdown = table_to_markdown(table)
    if mapping is None:
        mapping = _llm_mapping(markdown, items) if use_llm else DEFAULT_MAPPING

    particulars = [str(p).strip().lower() for p in table[particulars_col]]
    values, used, missing = {}, {}, []
    for item in items:
        terms = mapping.get(item) or []
        if isinstance(terms, str):
            terms = [terms]
        total, matched = 0.0, []
        for term in terms:
            key = str(term).strip().lower()
            if key in particulars:
                number = parse_number(table[year_column][particulars.index(key)])
                if number is not None:
                    total += number
                    matched.append(str(term))
        values[item] = total
        # Keep every chosen particular so edits stick even when its cell isn't numeric
        used[item] = [str(t) for t in terms]
        if not matched:
            missing.append(item)

    return {
        "sheet": sheet, "particulars_column": particulars_col, "year_column": year_column,
        "values": values, "mapping": used, "missing": missing, "markdown": markdown,
    }


# ---------- ratios & scoring ----------

# (key, name, category, max score, preference, latex, inputs) in ScoreCalculator's label order.
# LaTeX describes what source/calculation.py actually computes.
RATIOS = [
    ("dtn", "Financial Debt to Tangible Net Worth (DTN)", "Leverage", 7, "Low preferable",
     [r"DTN = \frac{\text{total liabilities}}{\text{Tangible Net Worth}}",
      r"\text{Tangible Net Worth} = \text{total assets} - \text{total liabilities} - \text{intangible assets}"],
     ["total liabilities", "total assets", "intangible assets"]),
    ("dta", "Financial Debt to Total Assets (DTA)", "Leverage", 3, "Low preferable",
     [r"DTA = \frac{\text{total liabilities}}{\text{total assets}}"],
     ["total liabilities", "total assets"]),
    ("current_ratio", "Current Ratio (CR)", "Liquidity", 7, "High preferable",
     [r"CR = \frac{\text{current assets}}{\text{current liabilities}}"],
     ["current assets", "current liabilities"]),
    ("cash_ratio", "Cash Ratio (Cash)", "Liquidity", 3, "High preferable",
     [r"\text{Cash Ratio} = \frac{\text{cash and cash equivalents at end of year}}{\text{current liabilities}}"],
     ["cash and cash equivalents at end of year", "current liabilities"]),
    ("npm", "Net Profit Margin (NPM)", "Profitability", 5, "High preferable",
     [r"NPM = \left( \frac{\text{net profit after tax}}{\text{revenue}} \right) \times 100"],
     ["net profit after tax", "revenue"]),
    ("roa", "Return on Assets (ROA)", "Profitability", 3, "High preferable",
     [r"ROA = \left( \frac{\text{net profit after tax}}{\text{total assets}} \right) \times 100"],
     ["net profit after tax", "total assets"]),
    ("opoa", "Operating Profit to Operating Assets (OPOA)", "Profitability", 2, "High preferable",
     [r"OPOA = \left( \frac{\text{operating profit}}{\text{total assets}} \right) \times 100"],
     ["operating profit", "total assets"]),
    ("ic", "Interest Coverage (IC)", "Coverage", 3, "High preferable",
     [r"IC = \frac{\text{earnings before tax}}{\text{finance cost}}"],
     ["earnings before tax", "finance cost"]),
    ("dscr", "Debt Service Coverage Ratio (DSCR)", "Coverage", 5, "High preferable",
     [r"DSCR = \frac{\text{operating profit}}{\text{Total Debt Service}}",
      r"\text{Total Debt Service} = \text{long term loan-current portion} + \text{finance cost}"],
     ["operating profit", "long term loan-current portion", "finance cost"]),
    ("cdr", "Operating Cashflow to Debt Ratio (CDR)", "Coverage", 4, "High preferable",
     [r"CDR = \frac{\text{cash flows from operating activities}}{\text{total liabilities}}"],
     ["cash flows from operating activities", "total liabilities"]),
    ("ccr", "Cashflow Coverage Ratio (CCR)", "Coverage", 3, "High preferable",
     [r"CCR = \frac{\text{non-current assets} + \text{capital work in progress} + \text{total assets}}"
      r"{\text{total liabilities}}"],
     ["non-current assets", "capital work in progress", "total assets", "total liabilities"]),
    ("std", "Stock Turnover Days (STD)", "Operational Efficiency", 4, "Low preferable",
     [r"STD = \frac{\text{inventories}}{\text{cost of sales} / 360}"],
     ["inventories", "cost of sales"]),
    ("tdcd", "Trade Debtor Collection Days (TDCD)", "Operational Efficiency", 3, "Low preferable",
     [r"TDCD = \frac{\text{accounts receivables}}{\text{Average Daily Credit Sales}}",
      r"\text{Average Daily Credit Sales} = \text{revenue} / 360"],
     ["accounts receivables", "revenue"]),
    ("at", "Asset Turnover (AT)", "Operational Efficiency", 3, "High preferable",
     [r"AT = \frac{\text{revenue}}{\text{total assets}}"],
     ["revenue", "total assets"]),
    ("cfs", "Operating Cash Flow to Sales (CFS)", "Earning Quality", 3, "High preferable",
     [r"CFS = \frac{\text{cash flows from operating activities}}{\text{revenue}}"],
     ["cash flows from operating activities", "revenue"]),
    ("car", "Cashflow Based Accrual Ratio (CAR)", "Earning Quality", 2, "Low preferable",
     [r"CAR = \frac{\text{revenue} + \text{cash flows from financing activities}}{\text{total assets}}"],
     ["revenue", "cash flows from financing activities", "total assets"]),
]
CATEGORIES = ["Leverage", "Liquidity", "Profitability", "Coverage", "Operational Efficiency", "Earning Quality"]
BANDS = ["Excellent", "Good", "Marginal", "Unacceptable"]
INDICATORS_ROOT = "Quantitative Indicators (60)"


# ---------- editable weights (json/indicators.json) ----------
# ScoreCalculator decides the band (thresholds); the file decides each indicator's
# weight ("Scale") and the points awarded per band.

def list_indicators():
    """Flat rows in RATIOS order: weight and points per band for each indicator."""
    data = json.loads(INDICATORS_PATH.read_text(encoding="utf-8"))[INDICATORS_ROOT]
    by_name = {name: (group, entry) for group, g in data.items() for name, entry in g["Indicators"].items()}
    rows = []
    for key, name, cat, default_max, *_ in RATIOS:
        group, entry = by_name.get(name, (cat, {"Scale": default_max, "Scoring": {}}))
        rows.append({
            "key": key, "name": name, "category": cat, "group": group, "scale": float(entry["Scale"]),
            "scoring": {band: float(entry["Scoring"].get(band, 0)) for band in BANDS},
        })
    return rows


def save_indicators(rows):
    known = {name: (key, cat) for key, name, cat, *_ in RATIOS}
    if {r["name"] for r in rows} != set(known) or len(rows) != len(known):
        raise ServiceError(f"Expected exactly the {len(known)} quantitative indicators")
    for r in rows:
        if r["scale"] < 0:
            raise ServiceError(f"{r['name']}: weight must be >= 0")
        for band in BANDS:
            points = r["scoring"].get(band)
            if points is None or not 0 <= points <= r["scale"]:
                raise ServiceError(f"{r['name']}: {band} points must be between 0 and the weight ({r['scale']:g})")
    data = {}
    for r in rows:
        group = r.get("group") or known[r["name"]][1]
        data.setdefault(group, {"Indicators": {}})["Indicators"][r["name"]] = {
            "Scale": r["scale"], "Scoring": {band: r["scoring"][band] for band in BANDS},
        }
    INDICATORS_PATH.write_text(json.dumps({INDICATORS_ROOT: data}, indent=4), encoding="utf-8")
    return list_indicators()


def list_formulas():
    weights = {i["key"]: i["scale"] for i in list_indicators()}
    return [
        {"key": key, "name": name, "category": cat, "latex": latex, "inputs": inputs,
         "preference": pref, "max_score": weights[key]}
        for key, name, cat, _, pref, latex, inputs in RATIOS
    ]


def rating_label(percentage):
    if percentage >= 80:
        return "Excellent"
    if percentage >= 70:
        return "Good"
    if percentage >= 60:
        return "Marginal"
    return "Unacceptable"


def _finite(value):
    return value if value is not None and math.isfinite(value) else None


def _pct(part, whole):
    return round(100 * part / whole, 2) if whole else 0.0


def score(values, qualitative_answers=None):
    """`values`: dict keyed by the spaced item names. Returns a ScoreResponse-shaped dict."""
    calc = FinancialCalculator(values)
    raw = {key: getattr(calc, f"{key}_calc")() for key, *_ in RATIOS}
    _, labels = ScoreCalculator([{"item": k, "value": v} for k, v in raw.items()]).calculate_scores()
    labels = [label for label in labels if label.strip()]  # drop category separators
    weights = {i["key"]: i for i in list_indicators()}

    ratios = [
        {"key": key, "name": name, "category": cat, "value": _finite(raw[key]),
         "score": weights[key]["scoring"][label], "max_score": weights[key]["scale"], "label": label, "preference": pref}
        for (key, name, cat, _, pref, *_), label in zip(RATIOS, labels)
    ]
    categories = [
        {"name": cat,
         "score": sum(r["score"] for r in ratios if r["category"] == cat),
         "max_score": sum(r["max_score"] for r in ratios if r["category"] == cat)}
        for cat in CATEGORIES
    ]
    quant_total = sum(r["score"] for r in ratios)
    quant_max = sum(r["max_score"] for r in ratios)
    quant_pct = _pct(quant_total, quant_max)

    qual = score_qualitative(qualitative_answers) if qualitative_answers is not None else None
    overall_total = quant_total + (qual["total"] if qual else 0)
    overall_max = quant_max + (qual["max_score"] if qual else 0)
    overall_pct = _pct(overall_total, overall_max)

    return {
        "ratios": ratios, "categories": categories,
        "quantitative_total": quant_total, "quantitative_max": quant_max,
        "quantitative_percentage": quant_pct, "quantitative_label": rating_label(quant_pct),
        "qualitative": qual,
        "overall_total": overall_total, "overall_max": overall_max,
        "overall_percentage": overall_pct, "overall_label": rating_label(overall_pct),
    }


# ---------- qualitative ----------

# (category, question) for each entry of json/qualitative_ques.json, in order
QUALITATIVE_QUESTIONS = [
    ("Performance Behavior", "How many times was the borrower adversely classified in the last 3 years?"),
    ("Performance Behavior", "How many times were the borrower's loans rescheduled/restructured in the last 3 years?"),
    ("Performance Behavior", "Did the borrower pay its suppliers/creditors regularly in the last year?"),
    ("Business and Industry Risk", "Sales growth"),
    ("Business and Industry Risk", "Age of business"),
    ("Business and Industry Risk", "Industry prospects"),
    ("Business and Industry Risk", "Long-term external credit rating of the borrower"),
    ("Management Risk", "Experience of the management"),
    ("Management Risk", "Existence of succession plan"),
    ("Management Risk", "Auditing firm"),
    ("Management Risk", "Change in external auditors in the last 4 years"),
    ("Security Risk", "Primary security"),
    ("Security Risk", "Collateral"),
    ("Security Risk", "Eligible collateral coverage"),
    ("Security Risk", "Type of guarantee"),
    ("Relationship Risk", "Account conduct"),
    ("Compliance Risk", "Compliance with environmental rules, regulations and covenants"),
    ("Compliance Risk", "Corporate governance: independence of management"),
]
QUALITATIVE_CATEGORIES = ["Performance Behavior", "Business and Industry Risk", "Management Risk",
                          "Security Risk", "Relationship Risk", "Compliance Risk"]


def _qualitative_options():
    with open(QUALITATIVE_PATH, encoding="utf-8") as f:
        options = json.load(f)["Q"]
    if len(options) != len(QUALITATIVE_QUESTIONS):
        raise ServiceError(f"{QUALITATIVE_PATH.name} has {len(options)} questions, expected "
                           f"{len(QUALITATIVE_QUESTIONS)}", 500)
    return options


def list_qualitative_questions():
    return [
        {"index": i, "category": cat, "question": question, "max_score": max(opts.values()),
         "options": [{"label": label, "score": s} for label, s in opts.items()]}
        for i, ((cat, question), opts) in enumerate(zip(QUALITATIVE_QUESTIONS, _qualitative_options()))
    ]


def _normalise(text):
    return re.sub(r"\s+", " ", str(text)).strip().lower()


def score_qualitative(answers):
    options = _qualitative_options()
    if len(answers) != len(options):
        raise ServiceError(f"Expected {len(options)} answers, got {len(answers)}", 422)

    scored = []
    for i, ((cat, question), opts, answer) in enumerate(zip(QUALITATIVE_QUESTIONS, options, answers)):
        lookup = {_normalise(label): (label, s) for label, s in opts.items()}
        match = lookup.get(_normalise(answer))
        if match is None:
            raise ServiceError(f"Question {i} ('{question}'): '{answer}' is not one of {list(opts)}", 422)
        scored.append({"index": i, "category": cat, "question": question, "answer": match[0],
                       "score": match[1], "max_score": max(opts.values())})

    categories = [
        {"name": cat,
         "score": sum(a["score"] for a in scored if a["category"] == cat),
         "max_score": sum(a["max_score"] for a in scored if a["category"] == cat)}
        for cat in QUALITATIVE_CATEGORIES
    ]
    total = sum(a["score"] for a in scored)
    max_score = sum(a["max_score"] for a in scored)
    return {"answers": scored, "categories": categories, "total": total,
            "max_score": max_score, "percentage": _pct(total, max_score)}


# ---------- OCR ----------

def _ocr_sheet(data, image_bytes=None, content_type=None):
    image = None
    if image_bytes is not None:
        image = f"data:{content_type or 'image/png'};base64,{base64.b64encode(image_bytes).decode()}"
    ocr = data.get("paddleOCR") or {}
    return {
        "table": data.get("processed_response") or {},
        "ocr_text": [str(t) for t in ocr.get("text") or []],
        "ocr_bbox": ocr.get("bbox") or [],
        "image": image,
        "llm_error": data.get("llm_error"),
    }


def run_ocr(uploads, use_saved):
    """`uploads`: [(filename, bytes, content_type)] for balance sheet, cash flow, income statement."""
    if use_saved:
        if not SAVED_OCR_PATH.exists():
            raise ServiceError(f"No saved OCR response at {SAVED_OCR_PATH}", 404)
        with open(SAVED_OCR_PATH, encoding="utf-8") as f:
            saved = json.load(f)
        # The saved image is a pickled array; never unpickle it here, send the upload instead if given.
        images = {key: (u[1], u[2]) for key, u in zip(api_client.SHEET_KEYS, uploads)} if uploads else {}
        out = {key: _ocr_sheet(saved[key], *images.get(key, (None, None))) for key in api_client.SHEET_KEYS}
        return {**out, "source": "saved"}

    files = []
    for name, data, content_type in uploads:
        f = io.BytesIO(data)
        f.name, f.type = name, content_type
        files.append(f)
    try:
        result = api_client.extract_statements(files)
    except api_client.BackendError as e:
        raise ServiceError(str(e), 502)
    out = {key: _ocr_sheet(result[key], data, ctype)
           for key, (_, data, ctype) in zip(api_client.SHEET_KEYS, uploads)}
    return {**out, "source": "backend"}


# ---------- storage ----------

def save_score(result, records):
    payload = {
        **{f"{r['key']}_score": r["score"] for r in result["ratios"]},
        "total_score": result["overall_total"],
        **records,
        "result": result,
    }
    stored = api_client.store("scoring_data", payload)
    if stored["status"] != "success":
        raise ServiceError(stored["error"], 502)
    return stored["response"]["id"]


def load_score(score_id):
    try:
        r = requests.get(f"{api_client.DB_API_URL}/scoring_data/{score_id}", timeout=30)
    except requests.exceptions.RequestException as e:
        raise ServiceError(f"Storage API ({api_client.DB_API_URL}) unreachable: {e}", 502)
    if r.status_code == 404:
        raise ServiceError(f"Score {score_id} not found", 404)
    if not r.ok:
        raise ServiceError(f"Storage API error {r.status_code}: {r.text[:300]}", 502)
    result = (r.json().get("scores") or {}).get("result")
    if not result:
        raise ServiceError(f"Score {score_id} was not saved by this API, so it has no graph data", 404)
    return {**result, "score_id": score_id}


# ---------- graphs ----------

LABEL_COLORS = {"Excellent": "#50d967", "Good": "#2ca0e8", "Marginal": "#e8a62c", "Unacceptable": "#db2e2e"}
GRAPH_IDS = ["summary", "categories", "ratios", "qualitative"]


def _fmt(value):
    return "∞" if value is None else f"{value:,.2f}"


def _summary_figure(result):
    """The Streamlit graph page: score donut, category bars and the analysis table."""
    pct = result["quantitative_percentage"]
    rows = []  # (criteria, scale, actual, score, pct, label, remark, is_header)
    for cat in result["categories"]:
        rows.append((cat["name"], cat["max_score"], "", cat["score"], f"{_pct(cat['score'], cat['max_score'])}%",
                     "", "", True))
        for i, r in enumerate(x for x in result["ratios"] if x["category"] == cat["name"]):
            rows.append((f"{i + 1}. {r['name']}", r["max_score"], _fmt(r["value"]), r["score"],
                         f"{_pct(r['score'], r['max_score'])}%", r["label"], r["preference"], False))
    rows.append(("Total", result["quantitative_max"], "", result["quantitative_total"], f"{pct}%",
                 result["quantitative_label"], "", True))

    columns = list(zip(*rows))
    base = ["#D5C0F2" if header else "#FBF2FC" for header in columns[7]]
    label_fill = [LABEL_COLORS.get(label, base[i]) for i, label in enumerate(columns[5])]

    fig = make_subplots(rows=2, cols=2, specs=[[{"type": "domain"}, {"type": "xy"}],
                                               [{"type": "table", "colspan": 2}, None]],
                        row_heights=[0.35, 0.65], subplot_titles=("Score Percentage", "Category Scores"))
    fig.add_trace(go.Pie(labels=["Score", "Remaining"], values=[pct, 100 - pct], hole=0.7, sort=False,
                         marker=dict(colors=["#F1421C", "#540A9A"]), textinfo="none"), row=1, col=1)
    fig.add_trace(go.Bar(x=[c["name"] for c in result["categories"]], y=[c["max_score"] for c in result["categories"]],
                         name="Scale", marker_color="#D5C0F2"), row=1, col=2)
    fig.add_trace(go.Bar(x=[c["name"] for c in result["categories"]], y=[c["score"] for c in result["categories"]],
                         name="Obtained", marker_color="#0BB0A3"), row=1, col=2)
    fig.add_trace(go.Table(
        header=dict(values=["Criteria", "Scale", "Actual Parameter", "Obtained Score", "Percentage", "Status", "Remarks"],
                    fill_color="#E580BB", align="left"),
        cells=dict(values=list(columns[:7]), fill_color=[base, base, base, base, base, label_fill, base], align="left"),
    ), row=2, col=1)
    # Centre the label on the pie's own subplot domain
    pie_x, pie_y = fig.data[0].domain.x, fig.data[0].domain.y
    fig.update_layout(barmode="overlay", height=1000, annotations=list(fig.layout.annotations) + [
        dict(text=f"{pct:.1f}%", x=sum(pie_x) / 2, y=sum(pie_y) / 2, xref="paper", yref="paper",
             xanchor="center", yanchor="middle", showarrow=False, font_size=36),
    ])
    return fig


def _categories_figure(cats, title):
    fig = go.Figure([
        go.Bar(x=[c["name"] for c in cats], y=[c["max_score"] for c in cats], name="Scale", marker_color="#D5C0F2"),
        go.Bar(x=[c["name"] for c in cats], y=[c["score"] for c in cats], name="Obtained", marker_color="#0BB0A3"),
    ])
    fig.update_layout(title=title, barmode="overlay")
    return fig


def build_graph(graph_id, result):
    if graph_id == "summary":
        fig = _summary_figure(result)
    elif graph_id == "categories":
        fig = _categories_figure(result["categories"], "Quantitative score by category")
    elif graph_id == "ratios":
        ratios = result["ratios"]
        fig = go.Figure(go.Bar(
            x=[r["key"].upper() for r in ratios], y=[_pct(r["score"], r["max_score"]) for r in ratios],
            marker_color=[LABEL_COLORS[r["label"]] for r in ratios],
            customdata=[[r["name"], _fmt(r["value"]), r["label"]] for r in ratios],
            hovertemplate="%{customdata[0]}<br>Value: %{customdata[1]}<br>%{customdata[2]}: %{y}%<extra></extra>",
        ))
        fig.update_layout(title="Score per ratio (% of scale)", yaxis_range=[0, 100])
    elif graph_id == "qualitative":
        if not result.get("qualitative"):
            raise ServiceError("This score has no qualitative answers", 404)
        fig = _categories_figure(result["qualitative"]["categories"], "Qualitative score by category")
    else:
        raise ServiceError(f"Unknown graph '{graph_id}'. Available: {GRAPH_IDS}", 404)
    return json.loads(fig.to_json())
