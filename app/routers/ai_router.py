from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import get_current_user
from app.schemas.ai import AiAlarmAnalyze, AiChat, AiReportAnalyze
from app.services.ai_service import AiService

router = APIRouter(prefix="/api/ai", tags=["AI智能模块"])

@router.post("/alarm/analyze")
async def analyze_alarm(data: AiAlarmAnalyze, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AiService.analyze_alarm(db, data.alarm_id, user.username)

@router.post("/chat")
async def chat(data: AiChat, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AiService.chat(db, data.message, data.relate_alarm_id, data.relate_robot_sn, user.username)

@router.get("/chat/list")
async def get_chat_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return AiService.get_chat_list(db, user.username, page, pageSize)

@router.post("/report/analyze")
async def analyze_report(data: AiReportAnalyze, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return AiService.analyze_report(db, data.robot_sn, data.startTime, data.endTime, user.username)