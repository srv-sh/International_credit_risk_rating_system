"""Single place that talks to the Docker backend (credit-risk-api).

The backend exposes only:
    GET  /health
    POST /extract  (multipart: file1, file2, file3) -> {"ok", "provider", "files": [{"filename", "result"}]}

`extract_statements` reshapes that response into the structure the Streamlit
pages already use: {"bs": {...}, "cfs": {...}, "is": {...}}.

Records are saved through the storage API in db_api/ (PostgreSQL), started with
`docker compose up -d`; `store` returns the {"status", "response": {"id"}} shape the pages expect.
"""
import base64
import io
import os
import pickle

import numpy as np
import requests
from dotenv import load_dotenv
from PIL import Image

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
LLM_PROVIDER = os.getenv("LLM_PROVIDER")  # optional: "gemini" or "openai"
REQUEST_TIMEOUT = int(os.getenv("BACKEND_TIMEOUT", "900"))
DB_API_URL = os.getenv("DB_API_URL", "http://localhost:8001").rstrip("/")

# Order of files sent to /extract, matching home.py's get_images() return order
SHEET_KEYS = ["bs", "cfs", "is"]


class BackendError(Exception):
    pass


def health():
    try:
        r = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return r.ok
    except requests.exceptions.RequestException:
        return False


def _file_bytes(file):
    if hasattr(file, "getvalue"):
        return file.getvalue()
    if hasattr(file, "read"):
        file.seek(0)
        return file.read()
    with open(file, "rb") as f:
        return f.read()


def _image_to_pickled_b64(image_bytes):
    """Encode an image the way the pages' json2im() decodes it (base64 of a pickled numpy array)."""
    arr = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
    return base64.b64encode(pickle.dumps(arr)).decode("utf-8")


def _markdown_to_columns(markdown):
    """Parse a markdown table into {column: [values]}."""
    rows = []
    for line in markdown.strip().splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if all(set(c) <= set(":- ") for c in cells):
            continue  # separator row
        rows.append(cells)
    if not rows:
        return {}
    header, body = rows[0], rows[1:]
    header = [h or f"col_{i}" for i, h in enumerate(header)]
    return {h: [r[i] if i < len(r) else "" for r in body] for i, h in enumerate(header)}


def _table_to_columns(table):
    """Accept whatever form the backend serialised the table in."""
    if isinstance(table, str):
        return _markdown_to_columns(table)
    if isinstance(table, list) and table and isinstance(table[0], dict):
        cols = list(table[0].keys())
        return {c: [row.get(c, "") for row in table] for c in cols}
    if isinstance(table, dict):
        # {col: [..]} or {col: {row_idx: val}}
        return {c: (list(v.values()) if isinstance(v, dict) else list(v)) for c, v in table.items()}
    return {}


def _columns_to_markdown(columns):
    cols = list(columns.keys())
    md = "| " + " | ".join(cols) + " |\n"
    md += "| " + " | ".join(["---"] * len(cols)) + " |\n"
    for row in zip(*[columns[c] for c in cols]):
        md += "| " + " | ".join(str(v) for v in row) + " |\n"
    return md


def _adapt_result(result, image_bytes):
    correct = result.get("correct_markdown")
    llm_error = isinstance(correct, str) and correct.startswith("Error from llm")
    table = result.get("incorrect_markdown", "") if llm_error or not correct else correct
    columns = _table_to_columns(table)

    return {
        "processed_response": columns,
        "paddleOCR": {"text": result.get("text", []), "bbox": result.get("bbox", [])},
        "image_base64": _image_to_pickled_b64(image_bytes),
        "raw_response": {"natural_text": _columns_to_markdown(columns) if columns else ""},
        "llm_error": correct if llm_error else None,
    }


def extract_statements(files, provider=LLM_PROVIDER):
    """Send the 3 statement images to /extract and return {"bs", "cfs", "is"} data.

    `files` order: balance sheet, cash flow, profit & loss (as returned by home.get_images()).
    """
    if not files or len(files) != 3 or not all(files):
        raise BackendError("Exactly three images are required (balance sheet, cash flow, profit & loss).")

    images = [_file_bytes(f) for f in files]
    multipart = {
        f"file{i + 1}": (getattr(f, "name", f"file{i + 1}.png"), data, getattr(f, "type", None) or "image/png")
        for i, (f, data) in enumerate(zip(files, images))
    }
    params = {"provider": provider} if provider else None

    try:
        r = requests.post(f"{BACKEND_URL}/extract", files=multipart, params=params, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        raise BackendError(f"Could not reach backend at {BACKEND_URL}: {e}") from e

    try:
        body = r.json()
    except ValueError:
        raise BackendError(f"Backend returned {r.status_code}: {r.text[:500]}")
    if not r.ok or not body.get("ok"):
        raise BackendError(f"Backend error ({r.status_code}): {body.get('error') or body.get('detail') or body}")

    results = body.get("files", [])
    if len(results) != 3:
        raise BackendError(f"Expected 3 results from backend, got {len(results)}")

    return {key: _adapt_result(item["result"], img) for key, item, img in zip(SHEET_KEYS, results, images)}


def store(kind, payload):
    """Save a record via the storage API (db_api). `kind` is e.g. "store_ocr_data" or "llm_data".

    Returns {'status': 'success', 'response': {'id': ...}} or {'status': 'error', 'error': ...}.
    """
    endpoint = kind if kind.startswith("store_") else f"store_{kind}"
    try:
        r = requests.post(f"{DB_API_URL}/{endpoint}", json=payload, timeout=30)
        r.raise_for_status()
        return {"status": "success", "response": r.json()}
    except requests.exceptions.RequestException as e:
        detail = getattr(e.response, "text", "") if getattr(e, "response", None) is not None else ""
        return {"status": "error", "error": f"Storage API ({DB_API_URL}) failed: {e} {detail[:300]}"}
