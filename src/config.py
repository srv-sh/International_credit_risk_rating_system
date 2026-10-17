tokens = []
detection_class_thresholds = {
    "table": 0.5,
    "table rotated" : 0.5,
    "no object" : 10
}
crop_padding = 12

table_detection_model = 'microsoft/table-transformer-detection'
table_stucture_recognisation_model =  "microsoft/table-structure-recognition-v1.1-all"


list_of_particulars = bs = [
    "asset", "non current asset", "property, plant and equipment", "intangible assets", "right-of-use assets", 
    "deferred tax asset", "investment property", "equity-accounted investees", "biological assets", 
    "capital work-in-progress", "long term investment", "contract cost", "long term loans to subsidiaries", 
    "other investments", "other non current assets", "fixed asset", "current asset", "inventories", 
    "trade and other receivables", "advances, deposits and prepayments", "cash", "investment in marketable securities", 
    "short term investments", "due from related party", "advance income tax", "other receivables", 
    "receivable from joint-ventures and associates", "liabilities", "non current liabilities", "employee benefit obligation", 
    "lease liabilities", "long term bank loans", "deferred tax liabilities", "gratuity payable", "fund", "current liabilities", 
    "trade and other payables", "short term loan", "long term loan-current portion", "lease liability-current portion", 
    "unclaimed dividend", "provisions and accruals", "current tax liabilities", "other current liabilities", 
    "security deposit of distributors", "accrued expenses", "leased assets", "future tax benefit", "real estate investment", 
    "associates and joint ventures", "investment in associates", "agricultural assets", "construction in progress", 
    "non-current investments", "contract expenses", "intercompany loans", "subsidiary loans", "related party loans", 
    "stock", "inventory assets", "accounts receivable", "receivables", "trade receivables", "debtors", 
    "prepaid expenses", "prepaid assets", "liquid assets", "cash and cash equivalents", "marketable investments", 
    "short-term investments", "trading securities", "receivables from related parties", "prepaid income tax", 
    "receivables from equity-accounted investees", "amounts due from joint ventures and associates", 
    "employee benefit liabilities", "employee benefits", "lease obligations", "long-term debt", 
    "bank borrowings (long-term)", "term loans", "long term borrowings", "future tax liabilities", 
    "deferred tax obligations", "gratuity liabilities", "accounts payable", "payables", "short-term debt", 
    "short-term borrowings", "short term credit facilities", "current portion of long-term debt", 
    "current portion of long-term loans", "long term loans - current maturity (secured)", 
    "current portion of lease liabilities", "current lease obligations", "unpaid dividends", 
    "dividends payable", "accrued liabilities", "provisions for liabilities and charges", 
    "provision for expenses", "income tax payable", "tax payable", "current income tax liabilities", 
    "income tax provision", "accrued costs", "accrued obligations",
    "cash flows from operating activities", 
    "net cash from/(used in) operating activities", 
    "cash flows from investing activities", 
    "cash flows from financing activities", 
    "cash and cash equivalents", 
    "cash generated from operating activities", 
    "net cash from/(used in) investing activities", 
    "net cash generated from investing activities", 
    "net cash from/(used in) financing activities", 
    "net cash generated from financing activities", 
    "closing cash and cash equivalents", 
    "cash and bank balances at the end of the year", 
    "revenue", 
    "cost of goods sold", 
    "gross profit", 
    "operating expenses", 
    "administrative expenses", 
    "selling & distribution expenses", 
    "operating profit", 
    "finance income", 
    "finance costs", 
    "net finance costs", 
    "profit after finance costs", 
    "non-operating income / (expenses)", 
    "profit before wppf & tax", 
    "contribution to wppf", 
    "profit before tax", 
    "income tax expense", 
    "current tax (expense) / income", 
    "deferred tax (expense) / income", 
    "net profit after tax", 
    "depreciation and amortization", 
    "foreign exchange (loss)/gain", 
    "sales revenue", 
    "income", 
    "turnover", 
    "gross revenue", 
    "cost of sales", 
    "cost of revenue", 
    "direct costs", 
    "gross income", 
    "gross margin", 
    "gross earnings", 
    "gross operating profit", 
    "operating costs", 
    "operating costs and expenses", 
    "general and administrative expenses", 
    "admin costs", 
    "administrative costs", 
    "general and administrative expenses", 
    "selling expenses", 
    "distribution costs", 
    "sales and distribution costs", 
    "marketing, selling and distribution expenses", 
    "operating income", 
    "operating earnings", 
    "operating margin", 
    "interest income", 
    "investment income", 
    "financial income", 
    "interest expense", 
    "finance expenses", 
    "borrowing costs", 
    "net interest expense", 
    "net borrowing costs", 
    "net financial expenses", 
    "net profit after finance costs", 
    "profit before tax (net of finance costs)", 
    "net income after finance costs", 
    "non-operating gains / (losses)", 
    "other income / (expenses)", 
    "non-operating revenues / (costs)", 
    "profit before tax and wppf (workers' profit participation fund)", 
    "pre-tax profit (excluding wppf)", 
    "operating profit before wppf and tax", 
    "wppf contribution", 
    "workers' profit share", 
    "profit sharing contribution", 
    "contribution to workers’ profit participation / welfare fund", 
    "pre-tax profit", 
    "earnings before tax (ebt)", 
    "profit before income tax", 
    "income tax provision", 
    "tax expense", 
    "current tax expense", 
    "current income tax expense", 
    "current tax provision", 
    "deferred tax provision", 
    "deferred tax expense", 
    "deferred tax benefit", 
    "net profit / (loss)", 
    "net income / (loss)", 
    "earnings after tax", 
    "depreciation and amortization expense", 
    "d&a expense", 
    "depreciation and amortization charges", 
    "currency exchange (loss)/gain", 
    "foreign currency (loss)/gain", 
    "exchange rate (loss)/gain"
]

model_path = "/workspace/hugging_face_model/olmOCR-7B-0225-preview"
processor_path = "/workspace/hugging_face_model/Qwen2-VL-7B-Instruct"
pdf_path = "/workspace/CreditScoring-refined-/pdf"


method = 'normal'


"""Tune this to remove overlapping or duplicate lines.

- Too low: may keep duplicate lines

- Too high: may suppress true lines"""
horiz_iou_thresh = 0.50
vert_iou_thresh = 0.10
"""Controls the minimum distance between clusters of lines.
Good values: 3–15 (depending on resolution and OCR accuracy)"""
horiz_eps = 5
vert_eps = 5

# Helps reduce repeated or noisy columns/rows.
horiz_min_gap =90
vert_min_gap =90
