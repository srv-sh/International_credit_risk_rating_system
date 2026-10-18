"""Request/response models for the compute API."""
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

Label = Literal["Excellent", "Good", "Marginal", "Unacceptable"]

# A statement table as the pages hold it: {column name: [cell, ...]}, first column = particulars
Table = dict[str, list[Any]]


# ---------- OCR ----------

class OcrSheet(BaseModel):
    table: Table = Field(description="Extracted statement as {column: [values]}")
    ocr_text: list[str] = Field(default_factory=list, description="Raw OCR tokens, for click-to-insert")
    ocr_bbox: list[Any] = Field(default_factory=list, description="Flat polygon per OCR token")
    image: Optional[str] = Field(None, description="Uploaded image as a data URL")
    llm_error: Optional[str] = None


class OcrResponse(BaseModel):
    bs: OcrSheet
    is_: OcrSheet = Field(alias="is")
    cfs: OcrSheet
    source: Literal["backend", "saved"]

    model_config = ConfigDict(populate_by_name=True, serialize_by_alias=True)


# ---------- statement calculation ----------

class StatementRequest(BaseModel):
    table: Table
    mapping: Optional[dict[str, Optional[list[str]]]] = Field(
        None,
        description="Item -> particulars to sum. Omit to use the default mapping (or the LLM when use_llm=true).",
    )
    year_column: Optional[str] = Field(None, description="Column to read values from. Defaults to the first value column.")
    use_llm: bool = Field(False, description="Ask the LLM to map items to particulars (only used when mapping is omitted)")

    model_config = ConfigDict(json_schema_extra={"example": {
        "table": {
            "Particulars": ["Revenue", "Cost of sales", "Operating profit", "Net finance costs",
                            "Profit before tax", "Profit/(loss) after tax"],
            "30 June 2023": ["115,355,397,105", "(89,483,069,654)", "6138853725", "-5053581867",
                             "1652687261", "-493958862"],
        },
    }})


class StatementResult(BaseModel):
    sheet: Literal["bs", "is", "cfs"]
    particulars_column: str
    year_column: str
    values: dict[str, float] = Field(description="Resolved line-item values")
    mapping: dict[str, list[str]] = Field(description="Particulars used for each item")
    missing: list[str] = Field(description="Items with no matching particular (valued at 0)")
    markdown: str


# ---------- qualitative ----------

class QualitativeOption(BaseModel):
    label: str
    score: float


class QualitativeQuestion(BaseModel):
    index: int
    category: str
    question: str
    max_score: float
    options: list[QualitativeOption]


class QualitativeRequest(BaseModel):
    answers: list[str] = Field(description="One selected option label per question, in question order")

    model_config = ConfigDict(json_schema_extra={"example": {"answers": [
        "0 time", "0 time", "Yes", ">10%", ">10 years", "Stable", "2&3",
        "More than 10 years in the related line of business", "Yes, with good capability of successor",
        "Recognized Auditors", "No", "Fully Pledged Facilities",
        "Registered Mortgage On Municipal Corporation/Prime Area Property", "80% to 100%",
        "Strong Corporate Guarantee", "More than 3 years Accounts having faultless record", "Yes",
        "Good Corporate Governance",
    ]}})


class QualitativeAnswer(BaseModel):
    index: int
    category: str
    question: str
    answer: str
    score: float
    max_score: float


class CategoryScore(BaseModel):
    name: str
    score: float
    max_score: float


class QualitativeResult(BaseModel):
    answers: list[QualitativeAnswer]
    categories: list[CategoryScore]
    total: float
    max_score: float
    percentage: float


# ---------- final score ----------

class FinancialValues(BaseModel):
    """The 19 line items the ratios are computed from. Accepts either the snake_case names or
    the spaced names the pages use (e.g. "total assets")."""
    total_assets: float = Field(0, alias="total assets")
    total_liabilities: float = Field(0, alias="total liabilities")
    current_assets: float = Field(0, alias="current assets")
    current_liabilities: float = Field(0, alias="current liabilities")
    intangible_assets: float = Field(0, alias="intangible assets")
    long_term_loan_current_portion: float = Field(0, alias="long term loan-current portion")
    inventories: float = Field(0, alias="inventories")
    accounts_receivables: float = Field(0, alias="accounts receivables")
    capital_work_in_progress: float = Field(0, alias="capital work in progress")
    noncurrent_assets: float = Field(0, alias="non-current assets")
    revenue: float = Field(0, alias="revenue")
    net_profit_after_tax: float = Field(0, alias="net profit after tax")
    operating_profit: float = Field(0, alias="operating profit")
    earnings_before_tax: float = Field(0, alias="earnings before tax")
    finance_cost: float = Field(0, alias="finance cost")
    cost_of_sales: float = Field(0, alias="cost of sales")
    cash_and_cash_equivalents_at_end_of_year: float = Field(0, alias="cash and cash equivalents at end of year")
    cash_flows_from_operating_activities: float = Field(0, alias="cash flows from operating activities")
    cash_flows_from_financing_activities: float = Field(0, alias="cash flows from financing activities")

    model_config = ConfigDict(populate_by_name=True)


class RecordIds(BaseModel):
    bs_id: Optional[int] = None
    is_id: Optional[int] = None
    cfs_id: Optional[int] = None
    llm_id: Optional[int] = None


class ScoreRequest(BaseModel):
    values: FinancialValues
    qualitative: Optional[QualitativeRequest] = None
    save: bool = Field(False, description="Store the result through db_api; returns score_id")
    records: RecordIds = Field(default_factory=RecordIds, description="Statement/LLM record ids to link when saving")

    model_config = ConfigDict(json_schema_extra={"example": {"values": {
        "total assets": 90908122246, "total liabilities": 80360849262, "current assets": 51237665010,
        "current liabilities": 70200705508, "intangible assets": 1409150269, "inventories": 21791856287,
        "accounts receivables": 17752360103, "non-current assets": 39670457236, "revenue": 115355397105,
        "net profit after tax": -493958862, "operating profit": 6138853725, "earnings before tax": 1652687261,
        "finance cost": 5053581867, "cost of sales": 89483069654,
        "cash and cash equivalents at end of year": 6912144024,
        "cash flows from operating activities": 2380088122, "cash flows from financing activities": 8833028441,
    }}})


class RatioResult(BaseModel):
    key: str
    name: str
    category: str
    value: Optional[float] = Field(description="null when the denominator is zero (infinite)")
    score: float
    max_score: float
    label: Label
    preference: str


class ScoreResponse(BaseModel):
    ratios: list[RatioResult]
    categories: list[CategoryScore]
    quantitative_total: float
    quantitative_max: float
    quantitative_percentage: float
    quantitative_label: Label
    qualitative: Optional[QualitativeResult] = None
    overall_total: float
    overall_max: float
    overall_percentage: float
    overall_label: Label
    score_id: Optional[int] = None


# ---------- formulas ----------

class Formula(BaseModel):
    key: str
    name: str
    category: str
    latex: list[str] = Field(description="Main formula first, then any helper definitions")
    inputs: list[str]
    preference: str
    max_score: float


# ---------- indicator weights ----------

class Indicator(BaseModel):
    key: str
    name: str
    category: str
    group: str = Field(description="Section heading in json/indicators.json, e.g. 'A. Leverage'")
    scale: float = Field(description="Weight: the most points this indicator can contribute")
    scoring: dict[str, float] = Field(description="Points per band: Excellent, Good, Marginal, Unacceptable")
