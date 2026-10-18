# International Credit Risk Rating System

An OCR- and LLM-assisted system that turns images of a company's **balance sheet, income statement and cash flow statement** into a transparent, rule-based **quantitative credit rating out of 60**, with every extracted figure, mapping, ratio, threshold and weight visible to and editable by the analyst.

The project is built by **Team ONNESHX** for the AI Builder Cup.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Problem Statement and Motivation](#2-problem-statement-and-motivation)
3. [Solution Summary and Key Differentiators](#3-solution-summary-and-key-differentiators)
4. [Key Features](#4-key-features)
5. [Screenshots and Demonstration](#5-screenshots-and-demonstration)
6. [System Architecture](#6-system-architecture)
7. [Architecture Diagrams](#7-architecture-diagrams)
8. [Technology Stack and Rationale](#8-technology-stack-and-rationale)
9. [Repository Structure](#9-repository-structure)
10. [Detailed Feature Documentation](#10-detailed-feature-documentation)
11. [Core Modules and Responsibilities](#11-core-modules-and-responsibilities)
12. [End-to-End Workflow and Data Flow](#12-end-to-end-workflow-and-data-flow)
13. [AI/ML Methodology](#13-aiml-methodology)
14. [Scoring Methodology](#14-scoring-methodology)
15. [API Reference](#15-api-reference)
16. [Data Models and Storage](#16-data-models-and-storage)
17. [Installation and Prerequisites](#17-installation-and-prerequisites)
18. [Environment Variables](#18-environment-variables)
19. [Local Development](#19-local-development)
20. [Usage Walkthrough](#20-usage-walkthrough)
21. [Testing and Quality Assurance](#21-testing-and-quality-assurance)
22. [AI/ML Evaluation](#22-aiml-evaluation)
23. [Deployment](#23-deployment)
24. [Security, Privacy and Data Handling](#24-security-privacy-and-data-handling)
25. [Known Limitations and Edge Cases](#25-known-limitations-and-edge-cases)
26. [Performance and Scalability](#26-performance-and-scalability)
27. [Roadmap](#27-roadmap)
28. [Team and Acknowledgments](#28-team-and-acknowledgments)
29. [License and Contact](#29-license-and-contact)

---

## 1. Overview

Credit analysts at lending institutions receive financial statements as scanned pages or screenshots. Before any judgement can be made, the figures must be transcribed, matched to standard line items, turned into ratios, compared against policy thresholds and weighted into a score.

This system automates that chain while keeping the analyst in control:

| Stage | Performed by | Nature |
|---|---|---|
| Text detection and recognition | PaddleOCR | ML model |
| Table reconstruction from text boxes | Geometric NMS on OCR boxes | Deterministic algorithm |
| Table clean-up (headers, duplicates, misspellings) | OpenAI or Google Gemini | LLM, temperature 0 |
| Review and correction of extracted tables | Analyst, in an editable grid | Human-in-the-loop |
| Line-item mapping | Default synonym dictionary, manual re-mapping; optional LLM mapping via API | Deterministic by default |
| 16 financial ratios, banding, weighting | `source/calculation.py`, `source/score_calc.py`, `api/services.py` | Deterministic business rules |
| Visualisation, summary and CSV export | Plotly figures from the API, React UI | Deterministic |

**The rating itself is never produced by an AI model.** AI is used only to read the documents; every number that contributes to the score is computed by fixed formulas and can be traced back to a specific cell in the reviewed table.

## 2. Problem Statement and Motivation

- **Manual transcription is slow and error-prone.** Statements contain dozens of lines and multiple year columns, and figures use accounting notation such as `(1,234,567)` for negatives.
- **Line names are not standardised.** One company reports "Net cash from/(used in) operating activities", another "Cash generated from operating activities". Ratios require a fixed vocabulary.
- **Scoring rules are policy, not opinion.** Credit-rating frameworks (the questionnaire in this repository references Bangladesh Bank BRPD circulars) define bands and weights that must be applied consistently and auditably.
- **Black-box scoring is unacceptable in lending.** An analyst must be able to explain every point awarded or withheld.

## 3. Solution Summary and Key Differentiators

1. **Guided eight-step wizard** (`frontend/src/flow.ts`) from applicant details to final summary, with step locking so that no page renders without the data it depends on.
2. **AI confined to extraction.** OCR and LLM clean-up produce a table; the analyst corrects it; deterministic code does the rest.
3. **Visible failure modes.** Items that could not be found are listed as `missing` and counted as zero, and the UI raises a specific warning when nearly all items are missing, distinguishing a wrong *particulars* column from a wrong *year* column (`frontend/src/pages/StatementPage.tsx`).
4. **Editable policy.** Indicator weights and points per band are stored in `json/indicators.json` and can be changed through the UI (`PUT /indicators`) with server-side validation.
5. **Offline-capable demo mode.** `USE_SAVED_RESPONSE=1` replays a recorded extraction (`saved_responses/input_data.json`), so the full rating chain runs without GPU, OCR models or API keys.
6. **Service separation.** OCR, compute and storage are separate FastAPI services, so the heavy OCR stack (PaddleOCR, TensorFlow) never has to be installed to run scoring.

## 4. Key Features

| Feature | Status | Where |
|---|---|---|
| Applicant details form with validation | Implemented | `frontend/src/pages/Home.tsx` |
| Upload of three statement images (drag-and-drop) | Implemented | `Home.tsx`, `components/blocks/UploadDropzone.tsx` |
| OCR + LLM table extraction service | Implemented | `fastapi_app.py`, `src/` |
| Saved-extraction replay mode | Implemented | `api/services.py::run_ocr` |
| Editable statement grids with accounting-number normalisation | Implemented | `pages/StatementPage.tsx`, `components/EditableTable.tsx`, `lib/numbers.ts` |
| Year-column selection and per-item re-mapping | Implemented | `StatementPage.tsx`, `Formulas.tsx` |
| Default particulars mapping | Implemented | `api/services.py::DEFAULT_MAPPING` |
| LLM-based particulars mapping (`use_llm=true`) | API only, not wired into the UI | `api/services.py::_llm_mapping`, `source/config.py::AgentCall` |
| 16 ratios across 6 categories, live preview | Implemented | `source/calculation.py`, `pages/Formulas.tsx` |
| Editable indicator weights and band points | Implemented | `pages/Indicators.tsx`, `PUT /indicators` |
| LaTeX formula display | Implemented | `GET /formulas`, `components/Latex.tsx` (KaTeX) |
| Plotly analysis charts (summary, categories, ratios) | Implemented | `api/services.py::build_graph`, `pages/Graphs.tsx` |
| Summary page with CSV export and "start over" | Implemented | `pages/Summary.tsx` |
| Persistence of statements and scores in PostgreSQL | Implemented, best-effort | `db_api/app.py` |
| Session persistence across browser refresh | Implemented | `store/useAppStore.ts` (zustand + localStorage) |
| Qualitative questionnaire (18 questions, 40 points) | Backend implemented; UI page off the main flow at `/parameters` | `GET/POST /qualitative/*`, `pages/Parameters.tsx` |
| Raw OCR viewer | Off the main flow at `/ocr` | `pages/Ocr.tsx` |
| Authentication / multi-tenant access control | **Not implemented** | — |
| PDF input | **Not implemented** in the live path (images only) | — |

## 5. Screenshots and Demonstration

No screenshots or recordings are committed to the repository. To see the application, follow [Local Development](#19-local-development) with `USE_SAVED_RESPONSE=1`; the whole flow runs in a few seconds without any external service. `PROJECT_SLIDES.md` contains the team's presentation outline.

## 6. System Architecture

The system is composed of five runtime components, all defined in `docker-compose.yml`:

| Service | Code | Port (host) | Responsibility |
|---|---|---|---|
| `frontend` | `frontend/` (React, built and served by nginx) | 8080 | Wizard UI; reverse-proxies `/api` and `/db` |
| `api` | `api/` + `source/` | 8002 | Compute API: OCR orchestration, statement resolution, ratios, scoring, formulas, weights, graphs |
| `ocr` | `fastapi_app.py` + `src/` | 8000 | PaddleOCR text recognition, table reconstruction, LLM clean-up |
| `db_api` | `db_api/app.py` | 8001 | Storage API over PostgreSQL (SQLAlchemy) |
| `db` | `postgres:16-alpine` | 5433 → 5432 | Persistent storage (`pgdata` volume) |

The browser only ever talks to the frontend origin. In development, Vite proxies `/api → :8002` and `/db → :8001` (`frontend/vite.config.ts`); in Docker, nginx does the same (`frontend/nginx.conf`), with a 900-second read timeout for slow OCR/LLM calls and a 50 MB upload limit.

## 7. Architecture Diagrams

### 7.A High-Level System Architecture

```mermaid
flowchart LR
    User([Credit analyst<br/>browser])

    subgraph FE["frontend :8080 (nginx) / :5173 (Vite dev)"]
        SPA["React SPA<br/>wizard, zustand store"]
        Proxy["Reverse proxy<br/>/api → api, /db → db_api"]
    end

    subgraph Compute["api :8002 (FastAPI)"]
        Services["api/services.py"]
        Source["source/<br/>FinancialCalculator<br/>ScoreCalculator"]
        Files[("json/indicators.json<br/>json/qualitative_ques.json<br/>saved_responses/input_data.json")]
    end

    subgraph OCR["ocr :8000 (FastAPI)"]
        Paddle["PaddleOCR"]
        Struct["Table reconstruction<br/>(TF non-max suppression)"]
        LLMc["LLM table clean-up"]
    end

    subgraph Store["Storage"]
        DBAPI["db_api :8001 (FastAPI)"]
        PG[("PostgreSQL 16")]
    end

    Ext1["OpenAI API"]
    Ext2["Google Gemini API"]

    User --> SPA --> Proxy
    Proxy -- "/api/*" --> Services
    Proxy -- "/db/*" --> DBAPI
    Services --> Source
    Services <--> Files
    Services -- "POST /extract (3 images)" --> Paddle
    Paddle --> Struct --> LLMc
    LLMc --> Ext1
    LLMc --> Ext2
    Services -- "use_llm mapping (optional)" --> Ext1
    Services -- "store / load score" --> DBAPI
    DBAPI --> PG
```

### 7.B Component-Level Architecture

```mermaid
flowchart TB
    subgraph Frontend["frontend/src"]
        App["App.tsx<br/>routes + StepGuard"]
        Flow["flow.ts<br/>STEPS, useFlow()"]
        StoreZ["store/useAppStore.ts"]
        EP["api/endpoints.ts<br/>axios clients"]
        subgraph Pages
            Home["Home"]
            SP["StatementPage<br/>(BS / IS / CFS)"]
            Ind["Indicators (weights)"]
            Form["Formulas (ratios + rate)"]
            Gr["Graphs"]
            Sum["Summary"]
            Par["Parameters (qualitative, off-flow)"]
            OcrP["Ocr (off-flow)"]
        end
        Num["lib/numbers.ts<br/>numerifyTable"]
    end

    subgraph API["api/"]
        Main["main.py<br/>routes, CORS, ServiceError handler"]
        Sch["schemas.py<br/>Pydantic models"]
        Svc["services.py"]
    end

    subgraph Src["source/"]
        Calc["calculation.py<br/>FinancialCalculator"]
        Score["score_calc.py<br/>ScoreCalculator"]
        Cli["api_client.py<br/>OCR + storage HTTP client"]
        Agent["config.py<br/>AgentCall (LangChain)"]
    end

    subgraph OCRS["fastapi_app.py + src/"]
        GD["GetDataFromTablePaddle.getData"]
        GT["GetTableFromImage.getTableOnly"]
        GO["GetOCRFromPaddle.getOCR"]
        GS["GetTableStucture.getStucture"]
        GR["GetResponseFromLLM.GetResponseFromOpenAI"]
    end

    App --> Flow --> StoreZ
    App --> Pages
    Pages --> EP
    Pages --> StoreZ
    StoreZ --> Num
    EP --> Main
    Main --> Sch
    Main --> Svc
    Svc --> Calc
    Svc --> Score
    Svc --> Cli
    Svc --> Agent
    Cli --> GD
    GD --> GT --> GO --> GS --> GR
```

### 7.C End-to-End Data Flow

```mermaid
flowchart TD
    A["3 images<br/>(BS, CFS, IS)"] --> B["POST /api/ocr<br/>multipart"]
    B -->|USE_SAVED_RESPONSE=1| S["saved_responses/input_data.json"]
    B -->|USE_SAVED_RESPONSE=0| C["OCR service /extract"]
    C --> D["PaddleOCR: texts, boxes, scores"]
    D --> E["Row/column bands + NMS<br/>→ raw markdown grid"]
    E --> F["LLM clean-up → corrected table"]
    F -->|LLM error| F2["fall back to raw markdown"]
    F --> G["api_client._adapt_result<br/>→ {column: [cells]}"]
    F2 --> G
    S --> H
    G --> H["OcrResponse {bs, is, cfs, source}"]
    H --> I["Browser store: numerifyTable<br/>'(1,234)' → -1234"]
    I --> J["Analyst edits grid, picks year column"]
    J --> K["POST /api/{sheet}/calculate<br/>mapping → values, missing"]
    K --> K2["db_api /store_ocr_data<br/>(best effort) → bs_id/is_id/cfs_id"]
    K --> L["Merged 19 line-item values"]
    L --> M["POST /api/score (preview)"]
    L --> N["POST /api/score save=true"]
    N --> O["FinancialCalculator: 16 ratios"]
    O --> P["ScoreCalculator: band per ratio"]
    P --> Q["indicators.json: points per band"]
    Q --> R["ScoreResponse: /60, label"]
    R --> T["db_api /store_scoring_data → score_id"]
    R --> U["Graphs (Plotly JSON), Summary, CSV"]
```

### 7.D Core Feature Workflows

**Extraction and statement calculation**

```mermaid
sequenceDiagram
    actor U as Analyst
    participant FE as React (Home / StatementPage)
    participant API as Compute API
    participant OCR as OCR service
    participant LLM as OpenAI / Gemini
    participant DB as db_api

    U->>FE: Enter applicant details, attach 3 images
    FE->>API: POST /ocr (balance_sheet, cash_flow, income_statement)
    alt saved mode
        API-->>FE: OcrResponse (source="saved")
    else live mode
        API->>OCR: POST /extract (file1=BS, file2=CFS, file3=IS)
        loop each image
            OCR->>OCR: PaddleOCR predict, NMS bands, grid to markdown
            OCR->>LLM: "clean this markdown table" (temperature 0)
            LLM-->>OCR: corrected markdown
        end
        OCR-->>API: {ok, provider, files:[...]}
        API-->>FE: OcrResponse (source="backend")
    end
    FE->>FE: numerifyTable, store tables, unlock steps
    U->>FE: Correct cells, choose year column, Calculate
    FE->>API: POST /balance-sheet/calculate {table, year_column}
    API-->>FE: StatementResult {values, mapping, missing, markdown}
    FE->>DB: POST /store_ocr_data {sheet, response}
    DB-->>FE: {id} (failure only shows a warning toast)
    opt Item mapped to the wrong line
        U->>FE: Pick another line in the FROM dropdown
        FE->>API: POST /.../calculate {table, mapping, year_column}
    end
```

**Rating, analysis and summary**

```mermaid
sequenceDiagram
    actor U as Analyst
    participant FE as React (Weights / Indicators / Analysis / Summary)
    participant API as Compute API
    participant FS as json/indicators.json
    participant DB as db_api

    opt Change policy
        U->>FE: Edit weight and band points
        FE->>API: PUT /indicators [16 rows]
        API->>API: validate (all 16, 0 ≤ points ≤ weight)
        API->>FS: write
    end
    FE->>API: POST /score {values} (live preview)
    U->>FE: Continue on Indicators step
    FE->>API: POST /score {values, records, save:true}
    API->>FS: read weights
    API->>DB: POST /store_scoring_data
    DB-->>API: {id}
    API-->>FE: ScoreResponse + score_id
    alt storage down
        FE->>API: POST /score {values} (unsaved result)
    end
    FE->>API: GET /graphs/{id}?score_id=… or POST /graphs/{id} {ScoreResponse}
    API-->>FE: Plotly figure JSON
    U->>FE: Summary, export CSV
```

### 7.E AI/ML Pipeline Architecture (OCR service)

```mermaid
flowchart LR
    I["Uploaded image<br/>(PIL RGB)"] --> T["getTableOnly.detect<br/>(pass-through: no cropping)"]
    T --> O["getOCR.predict<br/>PaddleOCR 3.0<br/>rec_texts, rec_scores, rec_boxes"]
    O --> H["Horizontal bands<br/>full-width box per token"]
    O --> V["Vertical bands<br/>full-height box per token"]
    H --> N1["tf.image.non_max_suppression<br/>IoU 0.50, score ≥ 0.3"]
    V --> N2["tf.image.non_max_suppression<br/>IoU 0.10, score ≥ 0.3"]
    N1 --> G["Grid: rows × columns<br/>cell = token with IoU > 0.1"]
    N2 --> G
    G --> M["pandas → markdown<br/>(incorrect_markdown)"]
    M --> P["Prompt: fix headers, spelling,<br/>duplicates; keep row order;<br/>no new content"]
    P --> L{"LLM_PROVIDER"}
    L -->|openai| OA["chat.completions<br/>OPENAI_MODEL, temp 0, 4000 tokens"]
    L -->|gemini| GE["generate_content<br/>GEMINI_MODEL → GEMINI_FALLBACK_MODEL"]
    OA --> X["Parse markdown → DataFrame<br/>drop separator/unnamed cols"]
    GE --> X
    X --> R["{incorrect_markdown, correct_markdown,<br/>text, bbox}"]
```

## 8. Technology Stack and Rationale

| Layer | Technology | Rationale |
|---|---|---|
| UI framework | React 19, TypeScript, Vite 8 | Typed component model; fast dev server with a proxy that removes CORS from development |
| Routing / state | react-router-dom 7, zustand 5 (persisted), TanStack Query 5 | Wizard routing; a single store that survives refreshes; request caching and mutation states |
| Data grid | AG Grid Community 36 | Spreadsheet-style editing of extracted statements |
| Charts / maths | Plotly.js (figures built server-side), KaTeX | The API returns ready figure JSON, so chart logic lives with the scoring logic; formulas rendered from LaTeX |
| Motion | framer-motion | Animations respecting `prefers-reduced-motion` |
| Lint | oxlint | Fast lint for TS/React |
| Compute API | FastAPI, Pydantic v2, Plotly (Python), requests | Schema-validated endpoints with auto-generated OpenAPI docs at `/docs` |
| OCR | PaddleOCR 3.0.3 / PaddleX, PaddlePaddle 3.0 (CPU) | Strong text detection/recognition on printed financial tables |
| Table reconstruction | TensorFlow-CPU (`non_max_suppression`), scikit-learn (DBSCAN, alternative method), pandas | Rebuild rows and columns from token boxes without a dedicated table-structure model |
| LLM | OpenAI SDK, Google GenAI SDK; LangChain (`langchain_openai`) for the optional mapping agent | Provider choice at request time; deterministic settings (temperature 0 for clean-up) |
| Storage | PostgreSQL 16, SQLAlchemy 2, JSONB | Durable audit trail of statements and scores; JSONB for flexible score payloads |
| Delivery | Docker Compose, nginx 1.27 | One command brings up all five services |

## 9. Repository Structure

```text
.
├── api/                    Compute API (FastAPI, port 8002)
│   ├── main.py             Routes, CORS, ServiceError → HTTP mapping
│   ├── schemas.py          Pydantic request/response models
│   ├── services.py         Statement resolution, scoring, weights, qualitative, OCR, storage, graphs
│   ├── requirements.txt
│   └── Dockerfile
├── source/                 Shared business logic used by api/
│   ├── calculation.py      FinancialCalculator: the 16 ratio formulas
│   ├── score_calc.py       ScoreCalculator: band thresholds per ratio
│   ├── api_client.py       HTTP client for the OCR service and db_api; response adaptation
│   ├── config.py           AgentCall: LangChain prompt for LLM line-item mapping
│   └── conversion.py, file.py, main_function.py, qualitative_calc.py   Legacy (Streamlit era)
├── fastapi_app.py          OCR service entry point (port 8000)
├── src/                    OCR pipeline
│   ├── GetDataFromTablePaddle.py   getData: orchestrates OCR → structure → markdown → LLM
│   ├── GetOCRFromPaddle.py         PaddleOCR wrapper
│   ├── GetTableStucture.py         Row/column reconstruction (NMS or DBSCAN)
│   ├── GetResponseFromLLM.py       OpenAI / Gemini table clean-up
│   ├── GetTableFromImage.py        Table "detection" (currently pass-through)
│   ├── config.py                   Thresholds and method selection
│   ├── pipeline.py                 TablePipeline convenience wrapper
│   ├── DetectTable.py, allinone.py, RecogniseStucture.py, ...  Research scripts (hard-coded paths)
│   └── utils/                      Image helpers (deskew, resize, NMS, JSON/image encoding)
├── db_api/                 Storage API (FastAPI + SQLAlchemy, port 8001)
├── frontend/               React + TypeScript SPA
│   └── src/
│       ├── App.tsx, flow.ts, main.tsx
│       ├── api/            axios clients, endpoint wrappers, TS types
│       ├── pages/          Home, StatementPage (+BS/IS/CFS), Indicators, Formulas, Graphs, Summary, Parameters, Ocr
│       ├── components/     Grid, chart, LaTeX, nav, footer, blocks/ (dropzone, gauge, bars, toasts)
│       ├── store/          zustand store
│       └── lib/numbers.ts  Accounting-number parser
├── json/                   indicators.json (weights), qualitative_ques.json, prompt/intermediate files
├── saved_responses/        Recorded OCR output for offline mode
├── tests/test_api.py       pytest suite for the compute API
├── notebooks/              Exploration notebooks (augmentation, tests)
├── docker-compose.yml, Dockerfile (OCR image), .env.example, package.json
└── HANDOVER.md, PROJECT_SLIDES.md, AGENTS.md, LICENSE
```

## 10. Detailed Feature Documentation

### 10.1 Guided Wizard and Step Locking

- **Purpose:** prevent the analyst from opening a step whose inputs do not exist yet, and keep a single, consistent notion of "next".
- **Implementation:** `frontend/src/flow.ts` defines `STEPS` (Applicant → Balance sheet → Income statement → Cash flow → Weights → Indicators → Analysis → Summary). `useFlow()` derives, from the store, a `blocker` (why a step is locked) and `done` flag per step. `App.tsx::StepGuard` renders an explanatory empty state with a link to the earliest actionable step instead of a broken page. `StepNav` (rail) and `FlowFooter` (Back/Continue) both read from this one source.
- **Rules:** every step after Applicant requires extracted tables; Analysis and Summary additionally require a computed rating.
- **Note on naming:** the route `/weights` renders `pages/Indicators.tsx` (the weight editor) and the route `/formulas` renders `pages/Formulas.tsx`, which is labelled "Indicators" in the UI.

### 10.2 Applicant Details and Document Upload

- **User interaction:** name, address, phone and email fields (required, with inline validation), and three dropzones for the balance sheet, income statement and cash flow statement. A checkbox, "Use the saved extraction", allows proceeding without images.
- **Workflow:** on submit, `runOcr()` (`api/endpoints.ts`) posts a multipart form to `POST /api/ocr`. On success, `setOcr()` stores the three tables, resets any previous calculations, and the user is told to check each statement. Failure shows "Extraction failed. Nothing was changed."
- **Validation:** client-side required fields; server-side, `api/main.py::ocr` returns **422** unless all three files are provided in live mode.
- **Storage:** applicant details live only in the browser store (localStorage); they are **not** sent to any backend.

### 10.3 OCR Orchestration and Saved Mode

- **Purpose:** obtain a `{column: [cells]}` table for each statement.
- **Implementation:** `api/services.py::run_ocr`.
  - **Saved mode** (`use_saved=true` query parameter, or `USE_SAVED_RESPONSE=1`): reads `saved_responses/input_data.json`. The stored image is a pickled NumPy array and is deliberately **never unpickled**; if the user uploaded images, those are returned as data URLs instead.
  - **Live mode:** `source/api_client.py::extract_statements` posts `file1/file2/file3` to `{BACKEND_URL}/extract` in the order **BS, CFS, IS** (`SHEET_KEYS`), with a timeout of `BACKEND_TIMEOUT` seconds (default 900). `_adapt_result` prefers the LLM-corrected table; if the LLM returned an error string beginning `Error from llm`, it falls back to the raw OCR markdown and surfaces the error as `llm_error`. Tables arriving as markdown, list-of-records or dict-of-dicts are all normalised by `_table_to_columns`.
- **Errors:** unreachable or failing backend → `BackendError` → **502**; missing saved file → **404**.

### 10.4 OCR Service (`fastapi_app.py`)

- **Endpoint:** `POST /extract` with exactly three images, optional `provider` query (`openai`/`gemini`, default `LLM_PROVIDER` or `gemini`).
- **Per image:** `getData.get_stucture_data` (see [§13](#13-aiml-methodology)) returns `incorrect_markdown`, `correct_markdown`, `text`, `bbox`. `_make_json_safe` strips the image and converts NumPy values.
- **Errors:** empty upload → 400; any exception → 500 with `{"ok": false, "error", "trace"}`.

### 10.5 Statement Review, Normalisation and Calculation

- **Normalisation (client):** `lib/numbers.ts::numerifyTable` converts a cell only when the **entire** cell is an accounting number: `1,234` → `1234`, `(1,234)` → `-1234`. Line names, note references like `8 (a)` and date headers pass through untouched. The same rule is applied to every edit.
- **User interaction (`StatementPage.tsx`):** an editable grid, a year-column selector, and a Calculate button. After calculating, a "Values used" table shows each line item, its value and a FROM dropdown listing every particular in the table, so an item can be re-pointed at a different line.
- **Server (`api/services.py::calculate_statement`):**
  1. Rejects an empty table or columns of unequal length (**400**).
  2. Chooses the particulars column: a column named `particulars` (case-insensitive) or else the **first** column.
  3. Chooses the year column: the requested one (unknown → **400** listing valid columns) or else the first non-particulars column.
  4. Chooses the mapping: the request's `mapping`, otherwise the LLM mapping if `use_llm=true`, otherwise `DEFAULT_MAPPING`.
  5. For each item of that sheet (`SHEET_ITEMS`), sums `parse_number()` of every mapped particular found (case-insensitive exact match) in the year column. Unmatched or non-numeric items are listed in `missing` and valued at 0.
  6. Returns `values`, `mapping`, `missing`, the columns used, and a markdown rendering of the table.
- **Persistence:** after a successful calculation the page stores the markdown via `db_api /store_ocr_data` and keeps the returned id (`bs_id`, `is_id`, `cfs_id`) to link with the final score. A storage failure only produces a warning.
- **Diagnostics:** when all or all-but-one items are missing, the page tells the analyst whether to check the **year column** (names matched but held no numbers) or the **particulars column** (names did not match). A "stale" banner appears when the table is edited after calculation.

**Line items per statement (`SHEET_ITEMS`)**

| Statement | Items |
|---|---|
| Balance sheet (`bs`) | total assets, total liabilities, current assets, current liabilities, intangible assets, long term loan-current portion, inventories, accounts receivables, non-current assets |
| Income statement (`is`) | revenue, net profit after tax, operating profit, earnings before tax, finance cost, cost of sales |
| Cash flow (`cfs`) | capital work in progress, cash and cash equivalents at end of year, cash flows from operating activities, cash flows from financing activities |

`DEFAULT_MAPPING` maps these to common particulars, e.g. *accounts receivables* = "Trade receivables" + "Other receivables", *finance cost* = "Net finance costs", *cash flows from operating activities* = "Net cash from/(used in) operating activities". *long term loan-current portion* has no default and must be mapped manually.

### 10.6 Indicator Weights (Weights step)

- **Purpose:** let an institution apply its own policy without code changes.
- **User interaction (`pages/Indicators.tsx`):** a table of the 16 indicators with editable *weight* (`scale`) and points for *Excellent / Good / Marginal / Unacceptable*; an "Unsaved changes" note and a Save button.
- **Server:** `GET /indicators` reads `json/indicators.json`; `PUT /indicators` (`save_indicators`) requires exactly the 16 known indicators, weight ≥ 0, and each band's points between 0 and the weight, then rewrites the file.
- **Effect:** every later `/score` and `/formulas` call uses the new values. The file is **global to the API instance**, not per user.

### 10.7 Ratio Preview and Final Rating (Indicators step)

- **User interaction (`pages/Formulas.tsx`):** each of the 16 ratios is shown with its LaTeX formula, its inputs and the source line for each input, a live value and band (via an unsaved `POST /score`), a FROM dropdown for re-mapping, and a "missing only" filter. Continue triggers the final rating.
- **Final rating:** `POST /score` with `save: true` and the record ids; if storage is unreachable, the page re-requests without saving and warns. A toast reports e.g. "Rated 19.5 of 60 (Unacceptable)."

### 10.8 Analysis Charts

- **Server (`build_graph`)** returns Plotly figure JSON:
  - `summary`: score-percentage donut, category bars (scale vs. obtained) and a full analysis table with colour-coded bands.
  - `categories`: quantitative score by category.
  - `ratios`: per-ratio score as % of scale, coloured by band, with hover details.
  - `qualitative`: qualitative category scores (only when qualitative answers exist; otherwise **404**).
- **Client (`pages/Graphs.tsx`):** uses `GET /graphs/{id}?score_id=` for saved scores and `POST /graphs/{id}` with the in-memory result otherwise, so charts work even when storage is down.

### 10.9 Summary and Export

`pages/Summary.tsx` shows applicant details, the total and label (radial gauge), category breakdown, every ratio with value, band and points, and the saved score id. **Export CSV** downloads `credit-rating-<score_id|unsaved>.csv`; **Start over** clears the store.

### 10.10 Qualitative Assessment (off the main flow)

The backend implements an 18-question questionnaire worth 40 points across six categories (Performance Behavior, Business and Industry Risk, Management Risk, Security Risk, Relationship Risk, Compliance Risk), with options and scores in `json/qualitative_ques.json`. `POST /qualitative/score` matches answers case- and whitespace-insensitively and rejects unknown options with **422**. Passing `qualitative` to `/score` yields an overall rating out of 100. The UI page `/parameters` still works but is not part of the wizard and warns that its out-of-100 result will not match the rest of the app.

## 11. Core Modules and Responsibilities

| Module / symbol | Responsibility |
|---|---|
| `api/main.py` | Declares all compute routes, CORS from `CORS_ORIGINS`, maps `ServiceError` to `{"detail": ...}` with its status code |
| `api/schemas.py` | `StatementRequest/Result`, `ScoreRequest/Response`, `FinancialValues` (accepts `"total assets"` or `total_assets`), `Indicator`, `Formula`, `OcrResponse`, qualitative models |
| `api/services.py::parse_number` | `"1,234"`→1234, `"(1,234.5)"`→-1234.5, `"-5"`→-5; `"-"`, `""`, `"37.1(a)"`, NaN, ∞ → `None` |
| `api/services.py::calculate_statement` | Column selection, mapping, summation, missing-item reporting |
| `api/services.py::RATIOS` | Single table of key, name, category, default weight, preference, LaTeX and inputs for all 16 ratios |
| `api/services.py::score` | Runs `FinancialCalculator` and `ScoreCalculator`, applies weights from `indicators.json`, aggregates categories, labels, optional qualitative |
| `api/services.py::list_indicators / save_indicators` | Read/validate/write weights |
| `api/services.py::run_ocr`, `save_score`, `load_score`, `build_graph` | OCR orchestration, persistence via db_api, Plotly figures |
| `source/calculation.py::FinancialCalculator` | Ratio formulas with explicit zero-denominator handling |
| `source/score_calc.py::ScoreCalculator` | Band thresholds; returns labels (its hard-coded points are superseded by `indicators.json`) |
| `source/api_client.py` | `extract_statements`, `_adapt_result`, `store`; `BACKEND_URL`, `DB_API_URL`, `BACKEND_TIMEOUT`, `LLM_PROVIDER` |
| `source/config.py::AgentCall` | LangChain `PromptTemplate | ChatOpenAI` (temperature 0.3) that maps required items to table particulars, returning JSON |
| `src/GetDataFromTablePaddle.py::getData` | OCR pipeline orchestration and grid-to-markdown conversion |
| `src/GetTableStucture.py::getStucture` | Row/column reconstruction (`normal` NMS method, or `cluster` DBSCAN method) |
| `src/GetResponseFromLLM.py::GetResponseFromOpenAI` | Provider selection, clean-up prompt, Gemini model fallback, markdown → DataFrame parsing |
| `db_api/app.py` | ORM models, `store_*` endpoints, generic read endpoints |
| `frontend/src/store/useAppStore.ts` | All session state; persisted to localStorage without images to stay under quota |

## 12. End-to-End Workflow and Data Flow

1. **Input.** Three images and applicant details enter through `Home`.
2. **Extraction.** `/ocr` returns three tables (`source: "backend"` or `"saved"`), raw OCR tokens and boxes, and any LLM error.
3. **Normalisation.** The store converts accounting-notation cells into numbers.
4. **Human review.** The analyst corrects cells and chooses the year column for each statement.
5. **Resolution.** Each `/…/calculate` call reduces a table to that statement's line-item values; ids of the stored statements are kept.
6. **Merge.** The client merges the three `values` objects into one 19-item dictionary.
7. **Scoring.** `/score` computes 16 ratios, bands, weighted points, category totals and a label; with `save: true` the full result is stored as JSONB with links to the statement records.
8. **Output.** Charts, summary and CSV are rendered from the `ScoreResponse`.

Data at rest: tables and results in browser localStorage (per browser), statement markdown and score payloads in PostgreSQL (when reachable), weights in `json/indicators.json`.

## 13. AI/ML Methodology

### 13.1 Text Recognition

`src/GetOCRFromPaddle.py` instantiates `PaddleOCR` with document-orientation classification, unwarping and text-line orientation **disabled**, and returns `rec_texts`, `rec_scores` and `rec_boxes` for the image.

### 13.2 Table Reconstruction (deterministic)

`src/GetTableStucture.py::boxes_from_image` with `method = 'normal'` (set in `src/config.py`):

1. For each token box, create a **full-width horizontal band** and a **full-height vertical band**.
2. Apply `tf.image.non_max_suppression` to each set (horizontal IoU 0.50, vertical IoU 0.10, score threshold 0.3) to keep one band per row and per column.
3. Sort rows; order columns by x-position.
4. For every row × column intersection, place the token whose IoU with the intersection exceeds 0.1 (`getData.convert_to_markdown`).
5. Emit the grid as a markdown table (`incorrect_markdown`).

An alternative `cluster` method (DBSCAN on band centres with `eps = 5`, minimum column gap 90 px) is implemented but not the configured default.

### 13.3 LLM Table Clean-up

`src/GetResponseFromLLM.py` sends the raw markdown with an instruction to fix broken or misspelled headers and entries, remove duplicated or invalid columns/rows, keep empty rows, **preserve row order** and **not hallucinate new content**, returning only the table.

| Setting | OpenAI | Gemini |
|---|---|---|
| Selection | `provider=openai` | `provider=gemini` (OCR service default) |
| Model | `OPENAI_MODEL` (default `gpt-4-turbo` in this module) | `GEMINI_MODEL`, then `GEMINI_FALLBACK_MODEL` on failure |
| Key | `OPENAI_API_KEY` | `GOOGLE_API_KEY` or `GEMINI_API_KEY` |
| Temperature / max tokens | 0.0 / 4000 | 0.0 / 4000 |

The response is parsed from a fenced or bare markdown table into a DataFrame; separator and `Unnamed` columns are dropped. Any exception produces `"Error from llm : ..."`, which the compute API converts into a fallback to the raw OCR table.

### 13.4 Optional LLM Line-Item Mapping

`POST /{sheet}/calculate` with `use_llm: true` and no `mapping` calls `source/config.py::AgentCall` (LangChain `ChatOpenAI`, `OPENAI_MODEL` default `gpt-4o-mini`, optional `OPENAI_API_BASE_URL`, temperature 0.3). The prompt asks for a JSON object mapping each required item to a list of matching particulars (or `null`), with few-shot examples and rules against partial matches and invented keys.

**Output constraints:** the API extracts the outermost `{…}`, parses it as JSON (failure → **502**), and keeps only the requested item keys. Mapped names are then matched exactly against the table; anything the LLM invents simply does not match and appears in `missing`. A missing key returns **503**. The current UI does not send `use_llm`.

### 13.5 How AI Output Is Constrained

- The LLM never produces numbers used in scoring; it only reorganises a table that the analyst then reviews and edits.
- Every value in the score is traceable to a named particular and a named column, returned in `StatementResult.mapping`.
- Raw OCR tokens and boxes are returned alongside the cleaned table for inspection.

## 14. Scoring Methodology

### 14.1 Ratios (`source/calculation.py`)

| Key | Ratio | Formula as implemented | Zero denominator | Preference |
|---|---|---|---|---|
| `dtn` | Debt to Tangible Net Worth | TL / (TA − TL − Intangibles) | ∞ | Low |
| `dta` | Debt to Total Assets | TL / TA | ∞ | Low |
| `current_ratio` | Current Ratio | CA / CL | ∞ | High |
| `cash_ratio` | Cash Ratio | Cash at year end / CL | ∞ | High |
| `npm` | Net Profit Margin | NPAT / Revenue × 100 | 0 | High |
| `roa` | Return on Assets | NPAT / TA × 100 | 0 | High |
| `opoa` | Operating Profit to Operating Assets | Operating profit / TA × 100 | 0 | High |
| `ic` | Interest Coverage | EBT / Finance cost | ∞ | High |
| `dscr` | Debt Service Coverage | Operating profit / (LTL current portion + Finance cost) | ∞ | High |
| `cdr` | Operating Cash Flow to Debt | CFO / TL | 0 | High |
| `ccr` | Cashflow Coverage Ratio | (Non-current assets + CWIP + TA) / TL | ∞ | High |
| `std` | Stock Turnover Days | Inventories / (Cost of sales / 360) | ∞ | Low |
| `tdcd` | Trade Debtor Collection Days | Receivables / (Revenue / 360) | ∞ | Low |
| `at` | Asset Turnover | Revenue / TA | 0 | High |
| `cfs` | Operating Cash Flow to Sales | CFO / Revenue | 0 | High |
| `car` | Cashflow-based Accrual Ratio | (Revenue + CFF) / TA | ∞ | Low |

Infinite values are banded normally (e.g. a current ratio of ∞ is "Excellent") and are returned to clients as `null`.

### 14.2 Bands (`source/score_calc.py`) and Default Weights (`json/indicators.json`)

| Category (weight) | Ratio | Excellent | Good | Marginal | Points E / G / M / U |
|---|---|---|---|---|---|
| Leverage (10) | DTN | < 0.50 | 0.50–0.65 | 0.65–0.80 | 7 / 6 / 4 / 0 |
| | DTA | < 0.50 | 0.50–0.80 | 0.80–1.00 | 3 / 2.5 / 2 / 0 |
| Liquidity (10) | CR | > 3 | 1.5–3 | 1–1.5 | 7 / 6 / 4 / 0 |
| | Cash | > 1 | 0.5–1 | 0–0.5 | 3 / 2.5 / 2 / 0 |
| Profitability (10) | NPM | > 0.20 | 0.10–0.20 | 0.05–0.10 | 5 / 4 / 3 / 0 |
| | ROA | > 0.20 | 0.10–0.20 | 0.05–0.10 | 3 / 2.5 / 1.5 / 0 |
| | OPOA | > 0.20 | 0.10–0.20 | 0.05–0.10 | 2 / 1.5 / 1 / 0 |
| Coverage (15) | IC | > 3 | 1.5–3 | 1–1.5 | 3 / 2.5 / 1 / 0 |
| | DSCR | > 2 | 1.25–2 | 1–1.25 | 5 / 4 / 3 / 0 |
| | CDR | > 0.20 | 0.10–0.20 | 0–0.10 | 4 / 3 / 2 / 0 |
| | CCR | > 3 | 1.5–3 | 1–1.5 | 3 / 2.5 / 2 / 0 |
| Operational Efficiency (10) | STD | < 30 | 30–50 | 50–80 | 4 / 3 / 2 / 0 |
| | TDCD | < 30 | 30–50 | 50–80 | 3 / 2.5 / 2 / 0 |
| | AT | > 2 | 1–2 | 0.5–1 | 3 / 2.5 / 2 / 0 |
| Earning Quality (5) | CFS | ≥ 0.30 | 0.20–0.30 | 0.10–0.20 | 3 / 2.5 / 2 / 0 |
| | CAR | < 0.05 | 0.05–0.10 | 0.10–0.20 | 2 / 1.5 / 1 / 0 |

Anything outside the Marginal band is **Unacceptable**. Thresholds are fixed in code; points and weights come from `indicators.json` and are editable.

### 14.3 Aggregation and Label

```
quantitative_total = Σ points(ratio)            (max = Σ weights, 60 by default)
percentage         = round(100 × total / max, 2)
label              = Excellent ≥ 80 % > Good ≥ 70 % > Marginal ≥ 60 % > Unacceptable
```

With qualitative answers, `overall_total = quantitative_total + qualitative_total` (max 100) and the same label rule applies to the overall percentage.

## 15. API Reference

Interactive OpenAPI documentation: compute API `http://localhost:8002/docs`, storage API `http://localhost:8001/docs`, OCR service `http://localhost:8000/docs`. Through the frontend, prefix compute routes with `/api` and storage routes with `/db`.

### 15.1 Compute API (port 8002)

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | `{"status": "ok"}` |
| POST | `/ocr` | Multipart `balance_sheet`, `cash_flow`, `income_statement`; query `use_saved` |
| POST | `/balance-sheet/calculate` | Resolve balance-sheet items |
| POST | `/income/calculate` | Resolve income-statement items |
| POST | `/cashflow/calculate` | Resolve cash-flow items |
| GET | `/statements/items` | `SHEET_ITEMS` and `DEFAULT_MAPPING` |
| GET | `/qualitative/questions` | 18 questions with options and scores |
| POST | `/qualitative/score` | Score a list of 18 answers |
| POST | `/score` | Ratios, bands, points, totals; optional qualitative and save |
| GET | `/formulas` | 16 formulas with LaTeX, inputs, preference, current weight |
| GET | `/indicators` | Current weights and band points |
| PUT | `/indicators` | Replace weights and band points |
| GET | `/graphs` | `["summary", "categories", "ratios", "qualitative"]` |
| GET | `/graphs/{graph_id}?score_id=` | Plotly figure for a saved score |
| POST | `/graphs/{graph_id}` | Plotly figure from a `ScoreResponse` body |

**Calculate a statement**

```bash
curl -X POST http://localhost:8002/income/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "table": {
      "Particulars": ["Revenue", "Cost of sales", "Operating profit", "Net finance costs",
                      "Profit before tax", "Profit/(loss) after tax"],
      "30 June 2023": ["115,355,397,105", "(89,483,069,654)", "6138853725", "-5053581867",
                       "1652687261", "-493958862"]
    }
  }'
```

```json
{
  "sheet": "is",
  "particulars_column": "Particulars",
  "year_column": "30 June 2023",
  "values": {
    "revenue": 115355397105.0,
    "net profit after tax": -493958862.0,
    "operating profit": 6138853725.0,
    "earnings before tax": 1652687261.0,
    "finance cost": -5053581867.0,
    "cost of sales": -89483069654.0
  },
  "mapping": {"revenue": ["Revenue"], "finance cost": ["Net finance costs"], "...": ["..."]},
  "missing": [],
  "markdown": "| Particulars | 30 June 2023 |\n| --- | --- |\n..."
}
```

Optional body fields: `year_column` (string), `mapping` (`{item: [particular, ...] | null}`), `use_llm` (bool).

**Score**

```bash
curl -X POST http://localhost:8002/score -H "Content-Type: application/json" -d '{
  "values": {"total assets": 100, "total liabilities": 40, "current assets": 60,
             "current liabilities": 20, "revenue": 200, "net profit after tax": 30,
             "operating profit": 50, "earnings before tax": 40, "finance cost": 10,
             "cost of sales": 100, "inventories": 5, "accounts receivables": 10,
             "cash and cash equivalents at end of year": 25,
             "cash flows from operating activities": 70},
  "save": false
}'
```

Abridged response:

```json
{
  "ratios": [
    {"key": "dtn", "name": "Financial Debt to Tangible Net Worth (DTN)", "category": "Leverage",
     "value": 0.6666666666666666, "score": 4.0, "max_score": 7.0, "label": "Marginal", "preference": "Low preferable"}
  ],
  "categories": [{"name": "Leverage", "score": 7.0, "max_score": 10.0}],
  "quantitative_total": 53.0, "quantitative_max": 60.0,
  "quantitative_percentage": 88.33, "quantitative_label": "Excellent",
  "qualitative": null,
  "overall_total": 53.0, "overall_max": 60.0, "overall_percentage": 88.33, "overall_label": "Excellent",
  "score_id": null
}
```

(Output of the request above with default weights; only the first ratio and category are shown.) Additional body fields: `qualitative: {"answers": [18 strings]}`, `save: true`, `records: {bs_id, is_id, cfs_id, llm_id}`.

**Update weights** — `PUT /indicators` with all 16 rows as returned by `GET /indicators`:

```json
[{"key": "dtn", "name": "Financial Debt to Tangible Net Worth (DTN)", "category": "Leverage",
  "group": "A. Leverage", "scale": 7, "scoring": {"Excellent": 7, "Good": 6, "Marginal": 4, "Unacceptable": 0}}]
```

**Error format and codes** — all compute errors return `{"detail": "<message>"}`:

| Code | Cause |
|---|---|
| 400 | Empty table, unequal column lengths, no value columns, unknown `year_column`, invalid weights |
| 404 | Saved OCR file missing, unknown graph, unknown/foreign `score_id`, qualitative graph without qualitative data |
| 422 | Fewer than three files in live OCR mode; wrong number of, or unknown, qualitative answers; Pydantic validation |
| 500 | `qualitative_ques.json` has the wrong number of questions |
| 502 | OCR backend unreachable/failing, LLM call or JSON parse failed, storage API failure |
| 503 | `use_llm=true` without `OPENAI_API_KEY` |

### 15.2 Storage API (port 8001)

| Method | Path | Body / params | Returns |
|---|---|---|---|
| GET | `/health` | — | `{"status":"ok"}` after `SELECT 1` |
| POST | `/store_ocr_data` | `sheet`, `page_number`, `image_base64`, `raw_response`, `response`, extra fields allowed | `{"id": n}` |
| POST | `/store_llm_data` | `system_prompt`, `required_params`, `list_of_params`, `response`, `bs_id`, `is_id`, `cfs_id` | `{"id": n}` |
| POST | `/store_scoring_data` | `total_score`, `bs_id`, `is_id`, `cfs_id`, `llm_id`; all other fields stored in `scores` | `{"id": n}` |
| GET | `/{table}?limit=50` | `ocr_data`, `llm_data`, `scoring_data` | Latest rows, newest first |
| GET | `/{table}/{row_id}` | — | One row; 404 if table or row unknown |

### 15.3 OCR Service (port 8000)

| Method | Path | Notes |
|---|---|---|
| GET | `/health` | `{"status":"ok"}` |
| POST | `/extract` | Multipart `file1`, `file2`, `file3` (all required); query `provider`. Returns `{"ok": true, "provider", "files": [{"filename", "result": {"incorrect_markdown", "correct_markdown", "text", "bbox"}}]}`; errors `{"ok": false, "error", "trace"?}` |

## 16. Data Models and Storage

```mermaid
erDiagram
    OCR_DATA {
        int id PK
        text sheet
        int page_number
        text image_base64
        jsonb raw_response
        text response
        jsonb extra
        timestamptz created_at
    }
    LLM_DATA {
        int id PK
        text system_prompt
        text required_params
        text list_of_params
        text response
        int bs_id
        int is_id
        int cfs_id
        timestamptz created_at
    }
    SCORING_DATA {
        int id PK
        jsonb scores
        float total_score
        int bs_id
        int is_id
        int cfs_id
        int llm_id
        timestamptz created_at
    }
    OCR_DATA ||--o{ SCORING_DATA : "bs_id / is_id / cfs_id (logical)"
    LLM_DATA ||--o{ SCORING_DATA : "llm_id (logical)"
```

- Tables are created by `Base.metadata.create_all` at startup; there are no migrations.
- Relationships are **logical only** (no foreign-key constraints).
- `scoring_data.scores` holds `<ratio>_score` fields plus the full `ScoreResponse` under `result`; `GET /graphs/{id}?score_id=` reads it back. Rows created by other clients without `result` return 404 for graphs.
- In the current UI only `ocr_data` (statement markdown) and `scoring_data` are written. `llm_data` is available but unused by the React flow.

**File-based configuration:** `json/indicators.json` (weights, mutable at runtime), `json/qualitative_ques.json` (questionnaire), `saved_responses/input_data.json` (recorded extraction).

## 17. Installation and Prerequisites

| Requirement | Needed for |
|---|---|
| Docker + Docker Compose | Full stack, or just Postgres + db_api |
| Python 3.12 (as used by the Dockerfiles) | Compute API and tests outside Docker |
| Node.js 24 (as used by the frontend Dockerfile) and npm | Frontend and `npm run dev` |
| OpenAI and/or Google Gemini API key | Live OCR clean-up and optional LLM mapping only |

The OCR image installs PaddlePaddle, PaddleOCR, TensorFlow-CPU and OpenCV (`requirements-docker.txt`) and is large; it is **not** required in saved mode.

## 18. Environment Variables

Copy `.env.example` to `.env`. Never commit `.env`.

| Variable | Default | Used by | Purpose |
|---|---|---|---|
| `USE_SAVED_RESPONSE` | `1` | api | `1` = replay `saved_responses/input_data.json`; `0` = call OCR service |
| `BACKEND_URL` | `http://localhost:8000` (`http://ocr:8000` in compose) | api | OCR service base URL |
| `BACKEND_TIMEOUT` | `900` | api | Seconds to wait for `/extract` |
| `LLM_PROVIDER` | unset → OCR service uses `gemini` | api → ocr | `openai` or `gemini` for table clean-up |
| `OPENAI_API_KEY` | empty | api, ocr | OpenAI access |
| `OPENAI_MODEL` | `gpt-4o-mini` (`.env.example`) | api, ocr | Mapping agent model; clean-up model (module default `gpt-4-turbo`) |
| `OPENAI_API_BASE_URL` | unset | api | Optional OpenAI-compatible endpoint for the mapping agent |
| `GOOGLE_API_KEY` / `GEMINI_API_KEY` | unset | ocr | Gemini access |
| `GEMINI_MODEL`, `GEMINI_FALLBACK_MODEL` | module defaults | ocr | Gemini primary and fallback models |
| `DB_API_URL` | `http://localhost:8001` (`http://db_api:8001` in compose) | api | Storage API base URL |
| `CORS_ORIGINS` | `http://localhost:5173,http://127.0.0.1:5173` | api, db_api | Allowed browser origins |
| `DATABASE_URL` | `postgresql+psycopg2://postgres:postgres@localhost:5432/credit_risk` | db_api | SQLAlchemy URL (set by compose) |
| `STORE_DB_USER`, `STORE_DB_PASSWORD`, `STORE_DB_NAME` | `postgres`, `postgres`, `credit_risk` | compose | Postgres credentials |

`LLM_PROVIDER`, `GOOGLE_API_KEY` and the Gemini variables are read by the code but not listed in `.env.example`; add them when using live extraction.

## 19. Local Development

```bash
# 1. Configuration
cp .env.example .env            # Windows: copy .env.example .env

# 2. Dependencies
pip install -r api/requirements.txt      # compute API (minimal)
# or: pip install -r requirements.txt    # full research environment
npm install
npm --prefix frontend install

# 3. Storage (optional; the app still rates without it)
npm run db                      # docker compose up -d db db_api

# 4. Compute API (:8002) + frontend (:5173)
npm run dev
```

Open `http://localhost:5173`. With `USE_SAVED_RESPONSE=1`, no OCR service or API key is required.

**Live OCR** (optional):

```bash
pip install -r requirements-docker.txt
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000
# then in .env: USE_SAVED_RESPONSE=0, LLM_PROVIDER, and the matching API key
```

When the API runs in a container and the OCR service on the host, use `BACKEND_URL=http://host.docker.internal:8000`.

## 20. Usage Walkthrough

1. **Applicant** — fill in name, address, phone and email; attach the three statement images, or tick *Use the saved extraction*; submit.
2. **Balance sheet / Income statement / Cash flow** — check the grid against the source image, fix misread cells, select the column for the year being rated and click *Calculate*. Read the found/missing toast and any column warning; re-point items with the FROM dropdown if needed.
3. **Weights** — optionally adjust weights and band points and *Save weights*.
4. **Indicators** — review each ratio's formula, inputs and live band; filter to missing inputs; *Continue* to compute and save the rating.
5. **Analysis** — switch between the summary, category and ratio charts.
6. **Summary** — review the complete rating, *Export CSV*, or *Start over*.

## 21. Testing and Quality Assurance

```bash
pytest tests                     # backend
npm --prefix frontend run lint   # oxlint
npm --prefix frontend run build  # tsc -b + vite build
```

`tests/test_api.py` uses FastAPI's `TestClient`, runs without network services, and covers:

| Test | Verifies |
|---|---|
| `test_health`, `test_cors_preflight` | Liveness and CORS headers |
| `test_parse_number` | Commas, brackets, minus, dashes, note references |
| `test_balance_sheet_default_mapping` | Default mapping, summed receivables with a bracketed negative, `missing`, markdown |
| `test_statement_custom_mapping_and_year`, `test_statement_errors` | Custom mapping, year selection, 400 errors |
| `test_qualitative` | 18 questions summing to 40, full score, 422 on bad answers |
| `test_score_matches_score_calculator`, `test_score_zero_denominators_and_qualitative` | 16 ratios, totals, a known DTN band, ∞ → `null`, overall /100 |
| `test_formulas` | 16 formulas summing to 60 with LaTeX |
| `test_graphs_from_result` (×4), `test_unknown_graph` | Figure generation and 404 |
| `test_ocr_saved_response`, `test_ocr_requires_three_files` | Saved mode and live-mode validation |
| `test_indicators_roundtrip_changes_score`, `test_indicators_validation` | Weight edits affect scores (on a temporary file); validation |

**Result at the time of writing:** `19 passed` (local run, 2026-10-19).

**Not covered by automated tests:** the OCR service and `src/` pipeline, `db_api`, the LLM mapping path, and the frontend (no unit or end-to-end tests). `HANDOVER.md` records a manual regression check: the full chain on the saved extraction returned **19.5 / 60** with identical per-ratio scores before and after the UI rework.

## 22. AI/ML Evaluation

No quantitative evaluation of OCR accuracy, table-reconstruction accuracy or LLM clean-up quality (e.g. cell-level precision/recall on a labelled set) is included in the repository. `notebooks/` contains exploratory notebooks only. Accuracy issues observed during manual testing are documented in [§25](#25-known-limitations-and-edge-cases). A labelled benchmark of statement images is the most important evaluation gap.

## 23. Deployment

```bash
cp .env.example .env
docker compose up -d --build
```

| URL | Service |
|---|---|
| `http://localhost:8080` | Application (nginx + SPA) |
| `http://localhost:8002/docs` | Compute API |
| `http://localhost:8001/docs` | Storage API |
| `http://localhost:8000/docs` | OCR service |

```mermaid
flowchart LR
    B([Browser]) -->|":8080"| N["frontend<br/>nginx:1.27-alpine<br/>static SPA"]
    N -->|"/api/ → api:8002"| A["api<br/>python:3.12-slim"]
    N -->|"/db/ → db_api:8001"| D["db_api<br/>python"]
    A -->|"BACKEND_URL=http://ocr:8000"| O["ocr<br/>python:3.12-slim<br/>Paddle + TF CPU"]
    A -->|"DB_API_URL=http://db_api:8001"| D
    D -->|"DATABASE_URL"| P[("db<br/>postgres:16-alpine<br/>volume pgdata")]
```

- All services use `restart: unless-stopped`; `db_api` waits for the Postgres health check.
- The `api` image copies `json/` and `saved_responses/` at build time, so weight edits made through `PUT /indicators` live inside the container and are lost on rebuild unless a volume is mounted.
- Useful commands: `docker compose ps`, `docker compose logs -f api`, `docker compose down` (`-v` also deletes the database volume).

## 24. Security, Privacy and Data Handling

The system is a prototype; the following is a factual account of what is and is not in place.

**In place**
- Secrets are read from environment variables; `.env` is untracked and `.env.example` has empty keys.
- Pydantic validation on all compute and storage request bodies; weight edits are range-checked.
- Saved pickled images are never unpickled by the API.
- Browser access to backends goes through a same-origin proxy; CORS on the compute and storage APIs is restricted to configured origins.
- SQLAlchemy ORM is used for all queries (no string-built SQL).

**Not in place — required before handling real customer data**
- No authentication or authorisation on any service. Anyone who can reach port 8001 can list all stored records via `GET /{table}`; anyone who can reach port 8002 can change the global weights.
- The OCR service allows CORS from `*` and returns Python stack traces in 500 responses.
- No encryption at rest beyond what the Postgres deployment provides; default Postgres credentials in compose.
- Statement images are sent to third-party LLM providers in live mode (as OCR-derived markdown text). Organisations must assess this against their data-protection obligations.
- Applicant personal details are kept in browser localStorage and persist until *Start over*.
- No rate limiting, audit log of weight changes, or upload size validation beyond nginx's 50 MB limit.

## 25. Known Limitations and Edge Cases

**Accuracy**
1. **Unreadable values become zero.** Unmatched items and unparsable cells are valued at 0 and the rating still completes. The UI lists them and warns when nearly all are missing, but a partly wrong statement can still produce a plausible-looking score.
2. **Particulars column chosen by position.** Unless a column is named `particulars`, the first column is used; an index column in front breaks every match (`api/services.py::_particulars_column`).
3. **Default year column** is the first value column, which can be a note-reference column (observed on the saved cash flow). The UI lets the analyst choose but the default can be wrong.
4. **Number parsing gaps.** En-dash negatives (`–1,234`), trailing-minus (`1,234-`) and one-sided brackets are not parsed and become zero.
5. **Percentage-scale mismatch in profitability bands.** `npm_calc`, `roa_calc` and `opoa_calc` return percentages (× 100) while `ScoreCalculator` compares them against fractional thresholds (0.05 / 0.10 / 0.20). In effect, a margin above 0.20 % is banded "Excellent". This is existing behaviour, preserved unchanged.
6. **Unconventional formulas.** "DTN" and "DTA" use total liabilities rather than financial debt; CCR and CAR are computed as shown in [§14.1](#141-ratios-sourcecalculationpy). The LaTeX served by `/formulas` documents exactly what is computed.
7. **Sign conventions pass straight through.** Costs written as negatives in the statement (e.g. `(89,483,069,654)` cost of sales, `-5053581867` finance cost) stay negative, which flips ratios such as interest coverage and stock turnover days. The analyst must correct signs in the grid.
8. **Infinite ratios** (zero denominator) are banded by the same thresholds and can earn full points, e.g. a zero finance cost gives an "Excellent" interest coverage.

**Functional**
- Images only; PDF input is not handled in the live path. Each statement is one image; multi-page statements are not merged.
- Table "detection" is a pass-through: the whole image is OCR'd. `src/DetectTable.py` (YOLO) and the Table Transformer model names in `src/config.py` belong to research scripts with hard-coded local paths and are not used by the service.
- Single-year rating; no trend analysis across year columns.
- The qualitative assessment is outside the main flow; mixing it in yields a different scale (/100).
- Weights are global per API instance, not per user or per rating, and saved scores do not record which weights were used beyond the stored points.
- Several legacy modules (`ocr_data.py`, `source/main_function.py`, `source/qualitative_calc.py`, `input_data.py`, `Responses.py`) still import Streamlit and are not used by the current services.

## 26. Performance and Scalability

- **Compute API:** pure-Python arithmetic over 19 values; scoring cost is negligible. Figures are built per request with Plotly.
- **OCR service:** the expensive component. `getData` (PaddleOCR + LLM client) is constructed **per request**, so model loading is repeated; the three images are processed sequentially; CPU-only Paddle is configured. Timeouts are set to 900 s end-to-end to accommodate this.
- **Storage:** single Postgres instance; simple inserts and primary-key reads; `GET /{table}` is bounded by `limit`.
- **Scaling path:** the services are stateless except for `json/indicators.json` (move to the database) and could be replicated behind nginx; caching the OCR model across requests and processing images concurrently would be the first OCR optimisations. No load testing has been performed.

## 27. Roadmap

Derived from `HANDOVER.md` and the limitations above; none of these are implemented.

1. Surface unreadable values explicitly instead of treating them as zero; block rating when key items are missing.
2. Detect the particulars and year columns by content rather than position.
3. Extend number parsing (en dash, trailing minus, broken brackets) in both `parse_number` and `lib/numbers.ts`.
4. Align profitability thresholds with the percentage scale of the ratios.
5. Expose LLM-assisted mapping in the UI, with the LLM's suggestion shown for analyst approval.
6. Add PDF and multi-page input; enable real table detection.
7. Authentication, role-based access, per-tenant weights stored in the database, and an audit trail.
8. A labelled benchmark for OCR and table reconstruction, and frontend/end-to-end tests.
9. Remove or port the remaining Streamlit-era modules.

## 28. Team and Acknowledgments

**Team ONNESHX.** Contributors in the git history: Sourav Saha, Ahnaf Samin, Jaasia Anjum and Shamim Rahim.

Acknowledgments:
- Four UI components in `frontend/src/components/blocks/` (upload dropzone, radial gauge, stacked bars, toast stack) are ported from [bencho.dev](https://bencho.dev) under the MIT licence.
- Open-source projects: PaddleOCR, FastAPI, React, AG Grid Community, Plotly, KaTeX, SQLAlchemy, PostgreSQL.

## 29. License and Contact

Copyright (c) 2026 Sourav Saha, Team ONNESHX. All rights reserved.

This is proprietary software. The source code is visible for review and evaluation only. Copying, modifying, distributing, or using it in any product or service requires prior written permission. See the [LICENSE](LICENSE) file for details.

For permission requests or questions, contact the repository owners through the project's hosting platform.
