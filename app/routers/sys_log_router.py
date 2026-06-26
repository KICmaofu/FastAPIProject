from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import require_admin
from app.services.sys_log_service import SysLogService

router = APIRouter(prefix="/api/sys", tags=["系统日志模块"])

@router.get("/log/list")
async def get_log_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    username: str = Query(None),
    startTime: str = Query(None),
    endTime: str = Query(None),
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    return SysLogService.get_log_list(db, page, pageSize, username, startTime, endTime)