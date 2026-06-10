from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services import ai_service
from app.schemas.ai import AIPredictionRequest, AIPredictionResponse, AIDetectRequest, AIQueryRequest, AIReportRequest
from app.utils.response import success_response

router = APIRouter(prefix="/api/ai", tags=["AI模块"])

@router.post("/predict/environment", summary="环境数据预测")
async def predict_environment(
    request: AIPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = ai_service.predict_environment(db, request.hours)
    return success_response(data=result)

@router.post("/predict/device-failure", summary="设备故障预测")
async def predict_device_failure(
    deviceId: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = ai_service.predict_device_failure(db, deviceId)
    return success_response(data=result)

@router.post("/detect/anomalies", summary="异常检测")
async def detect_anomalies(
    request: AIDetectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = ai_service.detect_anomalies(db, request.data)
    return success_response(data=result)

@router.post("/generate/report", summary="智能分析报告")
async def generate_report(
    request: AIReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = ai_service.generate_report(db, request.type, request.startTime, request.endTime)
    return success_response(data=result)

@router.post("/query", summary="自然语言查询")
async def natural_language_query(
    request: AIQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = ai_service.query_natural_language(db, request.query)
    return success_response(data=result)

@router.get("/analyze/environment", summary="环境数据分析")
async def analyze_environment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = ai_service.analyze_environment(db)
    return success_response(data=result)
