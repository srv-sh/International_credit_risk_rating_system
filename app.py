from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import List
from PIL import Image
import io
from src.GetDataFromTable import getTableFromImage
import psycopg2
from psycopg2 import sql

app = FastAPI(
    title="Credit Scoring System API",
    description="This API allows users to upload financial documents for processing and store OCR, LLM, and scoring data in the database.",
    version="1.0.0",
    docs_url="/docs",  # Customize Swagger UI URL path
    redoc_url="/redoc"  # Customize Redoc UI URL path
)

# pydantic models
class OCRData(BaseModel):
    """Model for OCR data extraction from uploaded files."""
    url: str = "http://example.com"  # Example URL for reference
    prompt: str = "Extract data from the provided table"
    page_number: int = 1
    response: str = "OCR result as JSON"

    class Config:
        schema_extra = {
            "example": {
                "url": "http://example.com/file.pdf",
                "prompt": "Extract data from the first page",
                "page_number": 1,
                "response": "{\"column1\": 100, \"column2\": 200}"
            }
        }

class LLMData(BaseModel):
    """Model for LLM data and related scoring parameters."""
    system_prompt: str = "Generate the financial scoring report."
    required_params: str = "param1, param2"
    list_of_params: str = "param1=100, param2=200"
    response: str = "LLM result"
    bs_id: int | None = None  # Foreign key (nullable)
    is_id: int | None = None  # Foreign key (nullable)
    cfs_id: int | None = None  # Foreign key (nullable)

    class Config:
        schema_extra = {
            "example": {
                "system_prompt": "Generate the financial scoring report.",
                "required_params": "param1, param2",
                "list_of_params": "param1=100, param2=200",
                "response": "{\"score\": 85}",
                "bs_id": 1,
                "is_id": 2,
                "cfs_id": 3
            }
        }

class Scoring(BaseModel):
    """Model for financial scoring data."""
    dtn_score: float = 85.0
    dta_score: float = 90.0
    current_ratio_score: float = 70.0
    cash_ratio_score: float = 50.0
    npm_score: float = 60.0
    roa_score: float = 65.0
    opoa_score: float = 55.0
    ic_score: float = 80.0
    dscr_score: float = 75.0
    cdr_score: float = 72.0
    ccr_score: float = 78.0
    std_score: float = 88.0
    tdcd_score: float = 85.0
    at_score: float = 90.0
    cfs_score: float = 95.0
    car_score: float = 92.0
    total_score: float = 80.5
    bs_id: int | None = None  # Foreign key (nullable)
    is_id: int | None = None  # Foreign key (nullable)
    cfs_id: int | None = None  # Foreign key (nullable)
    llm_id: int | None = None  # Foreign key (nullable)

    class Config:
        schema_extra = {
            "example": {
                "dtn_score": 85.0,
                "dta_score": 90.0,
                "current_ratio_score": 70.0,
                "cash_ratio_score": 50.0,
                "npm_score": 60.0,
                "roa_score": 65.0,
                "opoa_score": 55.0,
                "ic_score": 80.0,
                "dscr_score": 75.0,
                "cdr_score": 72.0,
                "ccr_score": 78.0,
                "std_score": 88.0,
                "tdcd_score": 85.0,
                "at_score": 90.0,
                "cfs_score": 95.0,
                "car_score": 92.0,
                "total_score": 80.5,
                "bs_id": 1,
                "is_id": 2,
                "cfs_id": 3,
                "llm_id": 4
            }
        }

class Main:
    """Main class to handle data extraction and database interactions."""
    
    def __init__(self):
        self.data_extraction_cls = getTableFromImage()
        self.DB_CONFIG = {
            "dbname": "credit_scoring",
            "user": "sourav",  # Change this to your DB username
            "password": "sourav@59",  # Change this to your DB password
            "host": "192.168.10.50",  # Change if using a remote server
            "port": 5432  # Default PostgreSQL port
        }

    def get_db_connection(self):
        """Establish a database connection."""
        return psycopg2.connect(**self.DB_CONFIG)
    
    def get_data(self, image_content):
        """Extract table data from the image."""
        image = Image.open(io.BytesIO(image_content)).convert("RGB")
        particular , year1 , year2 , columns , url , prompt , data = self.data_extraction_cls.get_table_data(image)
        return particular , year1 , year2 , columns , url , prompt , data


main_cls = Main()
assign_file_name = {0: "bs", 1: "is", 2: "cfs"}


@app.post("/uploadfiles/", summary="Upload Financial Files", description="Uploads 3 financial documents (Balance Sheet, Income Statement, and Cash Flow Statement) for processing and data extraction.")
async def upload_files(files: List[UploadFile]):
    """
    Uploads exactly 3 files for OCR processing and returns the extracted data.
    - **files**: List of file objects (3 files are required)
    """
    if len(files) != 3:
        raise HTTPException(status_code=400, detail="You must upload exactly 3 files")
    
    final_response = {}
    for idx, file in enumerate(files):
        content = await file.read()
        particular, year1, year2, columns, url, prompt, data = main_cls.get_data(content)
        doc_type = assign_file_name[idx]
        dist = {"particulars": particular, columns[0]: year1, columns[1]: year2}
        final_response[doc_type] = {"processed_response": dist, "pdf_url": url, "prompt": prompt, "raw_response": data}
    
    return final_response


@app.post("/store_ocr_data/", summary="Store OCR Data", description="Store OCR data into the database.")
async def store_ocr_data(data: OCRData):
    """
    Stores OCR data into the database.
    - **data**: The OCR data extracted from the document.
    """
    conn = main_cls.get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        INSERT INTO ocr_data (url, prompt, page_number, response)
        VALUES (%s, %s, %s , %s)
        RETURNING id
        """
        cur.execute(query, (data.url, data.prompt, data.page_number, data.response))
        inserted_id = cur.fetchone()[0]
        conn.commit()
        return {"message": "Data inserted successfully", "id": inserted_id}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


@app.post("/store_llm_data/", summary="Store LLM Data", description="Store LLM data in the database for further processing.")
async def store_llm_data(data: LLMData):
    """
    Stores LLM data into the database.
    - **data**: The LLM data related to scoring parameters.
    """
    conn = main_cls.get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        INSERT INTO LLMData (system_prompt, required_params, list_of_params, response, bs_id, is_id, cfs_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        cur.execute(query, (data.system_prompt, data.required_params, data.list_of_params, 
                            data.response, data.bs_id, data.is_id, data.cfs_id))
        inserted_id = cur.fetchone()[0]
        conn.commit()
        return {"message": "LLMData inserted successfully", "id": inserted_id}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


@app.post("/store_scoring_data/", summary="Store Scoring Data", description="Store the scoring data based on financial metrics.")
async def store_scoring_data(data: Scoring):
    """
    Stores scoring data into the database.
    - **data**: The calculated financial scores based on various metrics.
    """
    conn = main_cls.get_db_connection()
    cur = conn.cursor()
    try:
        query = """
        INSERT INTO Scoring (dtn_score, dta_score, current_ratio_score, cash_ratio_score, npm_score,
                             roa_score, opoa_score, ic_score, dscr_score, cdr_score, ccr_score, std_score,
                             tdcd_score, at_score, cfs_score, car_score, total_score, bs_id, is_id, cfs_id, llm_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        cur.execute(query, (
            data.dtn_score, data.dta_score, data.current_ratio_score, data.cash_ratio_score, data.npm_score,
            data.roa_score, data.opoa_score, data.ic_score, data.dscr_score, data.cdr_score, data.ccr_score,
            data.std_score, data.tdcd_score, data.at_score, data.cfs_score, data.car_score, data.total_score,
            data.bs_id, data.is_id, data.cfs_id, data.llm_id
        ))
        inserted_id = cur.fetchone()[0]
        conn.commit()
        return {"message": "Scoring data inserted successfully", "id": inserted_id}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()
