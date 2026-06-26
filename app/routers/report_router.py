from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import get_current_user
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/report", tags=["报表模块"])

@router.get("/env/trend")
async def get_env_trend(
    robot_sn: str = Query(None),
    startTime: str = Query(None),
    endTime: str = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return ReportService.get_env_trend(db, robot_sn, startTime, endTime)

@router.get("/alarm/trend")
async def get_alarm_trend(type: str = Query("day"), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return ReportService.get_alarm_trend(db, type)

@router.get("/daily")
async def get_daily_report(
    startTime: str = Query(None),
    endTime: str = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return ReportService.get_daily_report(db, startTime, endTime)