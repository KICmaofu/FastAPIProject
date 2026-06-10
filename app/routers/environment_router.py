from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services import sensor_service
from app.schemas.environment import EnvironmentDataResponse, EnvironmentHistoryRequest
from app.utils.response import success_response

router = APIRouter(prefix="/api/environment", tags=["环境监测模块"])

@router.get("/latest", summary="获取环境数据")
async def get_latest_environment(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    data = sensor_service.get_latest_environment_data(db)
    return success_response(data=data)

@router.get("/history", summary="获取环境数据历史")
async def get_environment_history(
    startTime: str = Query(...),
    endTime: str = Query(...),
    interval: str = Query("1m", regex="^(1m|5m|15m|1h)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        history = sensor_service.get_environment_history(db, startTime, endTime, interval)
        return success_response(data=history)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
