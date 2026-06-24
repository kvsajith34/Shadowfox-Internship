"""Unversioned API route aliases for frontend compatibility."""
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile, File, Form

from app.database.db import get_db
from app.api.v1.health_routes import health_check
from app.api.v1.metrics_routes import get_metrics
from app.api.v1.history_routes import get_history
from app.api.v1.reports_routes import get_reports
from app.schemas.chat_schema import VisualChatRequest
from app.schemas.rag_schema import RagQueryRequest
from app.schemas.evaluation_schema import EvaluationRequest
from app.schemas.settings_schema import SettingsRequest
from app.api.v1.visual_chat_routes import visual_chat
from app.api.v1.rag_routes import pdf_rag_query
from app.api.v1.upload_routes import upload_file as _upload
from app.api.v1.invoice_routes import extract_invoice
from app.api.v1.chart_routes import analyze_chart
from app.api.v1.evaluation_routes import evaluate
from app.api.v1.settings_routes import save_settings

router = APIRouter()


# ─── GET Aliases ─────────────────────────────────────────────

@router.get("/health")
async def health_alias():
    return await health_check()


@router.get("/metrics")
async def metrics_alias(db=Depends(get_db)):
    return await get_metrics(db)


@router.get("/history")
async def history_alias(db=Depends(get_db)):
    return await get_history(db)


@router.get("/reports")
async def reports_alias(db=Depends(get_db)):
    return await get_reports(db)


# ─── POST Aliases ────────────────────────────────────────────

@router.post("/upload")
async def upload_alias(
    file: UploadFile = File(...),
    analysisType: str = Form("general"),
    db=Depends(get_db),
):
    return await _upload(file=file, analysisType=analysisType, db=db)


@router.post("/visual-chat")
async def visual_chat_alias(request: VisualChatRequest, db=Depends(get_db)):
    return await visual_chat(request, db=db)


@router.post("/pdf-rag-query")
async def pdf_rag_query_alias(request: RagQueryRequest, db=Depends(get_db)):
    return await pdf_rag_query(request, db=db)


@router.post("/extract-invoice")
async def extract_invoice_alias(
    file: UploadFile = File(...),
    db=Depends(get_db),
):
    return await extract_invoice(file=file, db=db)


@router.post("/analyze-chart")
async def analyze_chart_alias(
    file: UploadFile = File(...),
    question: Optional[str] = Form(""),
    db=Depends(get_db),
):
    return await analyze_chart(file=file, question=question, db=db)


@router.post("/evaluate")
async def evaluate_alias(request: EvaluationRequest, db=Depends(get_db)):
    return await evaluate(request, db=db)


@router.get("/settings")
async def get_settings_alias(db=Depends(get_db)):
    from app.api.v1.settings_routes import get_settings as _get_settings
    return await _get_settings(db=db)


@router.post("/settings")
async def settings_alias(request: SettingsRequest, db=Depends(get_db)):
    return await save_settings(request, db=db)


@router.get("/provider-debug")
async def provider_debug_alias(db=Depends(get_db)):
    from app.api.v1.settings_routes import provider_debug as _provider_debug
    return await _provider_debug(db=db)
