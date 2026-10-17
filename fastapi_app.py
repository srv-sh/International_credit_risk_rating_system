import json
import os
import traceback
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.exceptions import HTTPException as StarletteHTTPException
from PIL import Image

from src.GetDataFromTablePaddle import getData


app = FastAPI(title="OCR to LLM Table API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(_: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"ok": False, "error": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={"ok": False, "error": str(exc), "trace": traceback.format_exc()},
    )


def _process_bytes(file_bytes: bytes, extractor):
    image = Image.open(BytesIO(file_bytes)).convert("RGB")
    return extractor.get_stucture_data(image)


def _make_json_safe(value):
    if isinstance(value, dict):
        return {key: _make_json_safe(val) for key, val in value.items() if key != "image"}
    if isinstance(value, list):
        return [_make_json_safe(item) for item in value]
    if hasattr(value, "tolist"):
        return value.tolist()
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return value.item()
        except Exception:
            pass
    return value


async def _process_upload(file: UploadFile, extractor):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail=f"File '{file.filename}' is empty")
    result = _process_bytes(content, extractor)
    return {"filename": file.filename, "result": result}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/extract")
async def extract(
    file1: UploadFile = File(..., description="First image"),
    file2: UploadFile = File(..., description="Second image"),
    file3: UploadFile = File(..., description="Third image"),
    provider: Optional[str] = Query(default=None),
):
    files = [file1, file2, file3]

    llm_provider = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()
    extractor = getData(provider=llm_provider)
    payload = []
    for file in files:
        item = await _process_upload(file, extractor)
        payload.append(_make_json_safe(item))
    return {"ok": True, "provider": llm_provider, "files": payload}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("fastapi_app:app", host="0.0.0.0", port=8000, reload=False)
