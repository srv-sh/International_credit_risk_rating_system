"""Service layer for the compute API (interface only).

The implementation (OCR pipeline, LLM line-item mapping, ratio formulas,
scoring weights and rating bands) is proprietary and not included in this
submission. Signatures are kept so api/main.py shows the full API surface.
"""


class ServiceError(Exception):
    def __init__(self, message, status_code=400):
        super().__init__(message)
        self.status_code = status_code


_HIDDEN = "Not included in the public submission."


def parse_number(value):
    """'1,234' -> 1234.0, '(1,234)' -> -1234.0, '-' / '' / '37.1(a)' -> None."""
    raise NotImplementedError(_HIDDEN)


def table_to_markdown(table):
    raise NotImplementedError(_HIDDEN)


def calculate_statement(sheet, table, mapping=None, year_column=None, use_llm=False):
    raise NotImplementedError(_HIDDEN)


def list_indicators():
    """Flat rows in RATIOS order: weight and points per band for each indicator."""
    raise NotImplementedError(_HIDDEN)


def save_indicators(rows):
    raise NotImplementedError(_HIDDEN)


def list_formulas():
    raise NotImplementedError(_HIDDEN)


def rating_label(percentage):
    raise NotImplementedError(_HIDDEN)


def score(values, qualitative_answers=None):
    """`values`: dict keyed by the spaced item names. Returns a ScoreResponse-shaped dict."""
    raise NotImplementedError(_HIDDEN)


def list_qualitative_questions():
    raise NotImplementedError(_HIDDEN)


def score_qualitative(answers):
    raise NotImplementedError(_HIDDEN)


def run_ocr(uploads, use_saved):
    """`uploads`: [(filename, bytes, content_type)] for balance sheet, cash flow, income statement."""
    raise NotImplementedError(_HIDDEN)


def save_score(result, records):
    raise NotImplementedError(_HIDDEN)


def load_score(score_id):
    raise NotImplementedError(_HIDDEN)


def build_graph(graph_id, result):
    raise NotImplementedError(_HIDDEN)
