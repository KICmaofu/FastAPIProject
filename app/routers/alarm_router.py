from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import get_current_user
from app.schemas.alarm import AlarmDeal, AlarmDelete
from app.services.alarm_service import AlarmService

router = APIRouter(prefix="/api/alarm", tags=["告警模块"])

@router.get("/list")
async def get_alarm_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    alarm_level: str = Query(None),
    deal_status: int = Query(None),
    robot_sn: str = Query(None),
    startTime: str = Query(None),
    endTime: str = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return AlarmService.get_alarm_list(db, page, pageSize, alarm_level, deal_status, robot_sn, startTime, endTime)

@router.post("/deal")
async def deal_alarm(data: AlarmDeal, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AlarmService.deal_alarm(db, data.id, data.deal_content, user.username)

@router.post("/delete")
async def delete_alarm(data: AlarmDelete, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AlarmService.delete_alarm(db, data.id)

@router.get("/statistics")
async def get_alarm_statistics(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AlarmService.get_alarm_statistics(db)

@router.get("/recent")
async def get_recent_alarm(limit: int = Query(10, ge=1, le=100), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AlarmService.get_recent_alarm(db, limit)

@router.get("/trend")
async def get_alarm_trend(days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AlarmService.get_alarm_trend(db, days)

@router.get("/{id}")
async def get_alarm_detail(id: int = Path(..., gt=0), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AlarmService.get_alarm_detail(db, id)