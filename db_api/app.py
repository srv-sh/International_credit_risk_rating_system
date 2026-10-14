"""Storage API for the credit risk rating frontend (PostgreSQL)."""
import json
import os
from datetime import datetime
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import (Column, DateTime, Float, Integer, Text, create_engine, func, select)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Session

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost:5432/credit_risk"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


class Base(DeclarativeBase):
    pass


class OcrData(Base):
    __tablename__ = "ocr_data"
    id = Column(Integer, primary_key=True)
    sheet = Column(Text)
    page_number = Column(Integer)
    image_base64 = Column(Text)
    raw_response = Column(JSONB)
    response = Column(Text)
    extra = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class LlmData(Base):
    __tablename__ = "llm_data"
    id = Column(Integer, primary_key=True)
    system_prompt = Column(Text)
    required_params = Column(Text)
    list_of_params = Column(Text)
    response = Column(Text)
    bs_id = Column(Integer)
    is_id = Column(Integer)
    cfs_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ScoringData(Base):
    __tablename__ = "scoring_data"
    id = Column(Integer, primary_key=True)
    scores = Column(JSONB)
    total_score = Column(Float)
    bs_id = Column(Integer)
    is_id = Column(Integer)
    cfs_id = Column(Integer)
    llm_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


Base.metadata.create_all(engine)

app = FastAPI(title="Credit Risk Storage API", version="1.0.0")


class OcrIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    sheet: Optional[str] = None
    page_number: Optional[int] = 1
    image_base64: Optional[str] = None
    raw_response: Optional[Any] = None
    response: Optional[Any] = None


class LlmIn(BaseModel):
    system_prompt: Optional[str] = None
    required_params: Optional[str] = None
    list_of_params: Optional[str] = None
    response: Optional[str] = None
    bs_id: Optional[int] = None
    is_id: Optional[int] = None
    cfs_id: Optional[int] = None


class ScoringIn(BaseModel):
    model_config = ConfigDict(extra="allow")
    total_score: Optional[float] = None
    bs_id: Optional[int] = None
    is_id: Optional[int] = None
    cfs_id: Optional[int] = None
    llm_id: Optional[int] = None


def _as_text(value):
    return value if value is None or isinstance(value, str) else json.dumps(value, default=str)


def _row_to_dict(row):
    out = {c.name: getattr(row, c.name) for c in row.__table__.columns}
    return {k: v.isoformat() if isinstance(v, datetime) else v for k, v in out.items()}


def _save(obj):
    with Session(engine) as s:
        s.add(obj)
        s.commit()
        return {"id": obj.id}


@app.get("/health")
def health():
    with engine.connect() as conn:
        conn.exec_driver_sql("SELECT 1")
    return {"status": "ok"}


@app.post("/store_ocr_data")
def store_ocr_data(body: OcrIn):
    raw = body.raw_response
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except ValueError:
            raw = {"text": raw}
    return _save(OcrData(
        sheet=body.sheet, page_number=body.page_number, image_base64=body.image_base64,
        raw_response=raw, response=_as_text(body.response), extra=body.model_extra or None,
    ))


@app.post("/store_llm_data")
def store_llm_data(body: LlmIn):
    return _save(LlmData(**body.model_dump()))


@app.post("/store_scoring_data")
def store_scoring_data(body: ScoringIn):
    return _save(ScoringData(
        scores=body.model_extra, total_score=body.total_score,
        bs_id=body.bs_id, is_id=body.is_id, cfs_id=body.cfs_id, llm_id=body.llm_id,
    ))


TABLES = {"ocr_data": OcrData, "llm_data": LlmData, "scoring_data": ScoringData}


@app.get("/{table}")
def list_rows(table: str, limit: int = 50):
    model = TABLES.get(table)
    if not model:
        raise HTTPException(404, f"Unknown table '{table}'")
    with Session(engine) as s:
        rows = s.scalars(select(model).order_by(model.id.desc()).limit(limit)).all()
        return [_row_to_dict(r) for r in rows]


@app.get("/{table}/{row_id}")
def get_row(table: str, row_id: int):
    model = TABLES.get(table)
    if not model:
        raise HTTPException(404, f"Unknown table '{table}'")
    with Session(engine) as s:
        row = s.get(model, row_id)
        if not row:
            raise HTTPException(404, "Not found")
        return _row_to_dict(row)
