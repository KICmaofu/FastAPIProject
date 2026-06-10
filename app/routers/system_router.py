from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user, require_admin
from app.models.user import User
from app.services import system_service
from app.schemas.system import SystemStatusResponse, SystemConfigUpdate, SystemLogListResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api/system", tags=["系统模块"])

@router.get("/status", summary="获取系统状态")
async def get_system_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    status = system_service.get_system_status(db)
    return success_response(data=status)

@router.get("/logs", summary="获取系统日志")
async def get_system_logs(
    level: Optional[str] = Query(None, regex="^(info|warn|error)$"),
    startTime: Optional[str] = Query(None),
    endTime: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = system_service.get_system_logs(db, level, startTime, endTime, page, size)

    log_list = []
    for log in result["list"]:
        log_list.append({
            "id": log.id,
            "level": log.level,
            "module": log.module,
            "content": log.content,
            "time": log.create_time.isoformat()
        })

    return success_response(data={
        "list": log_list,
        "total": result["total"],
        "page": result["page"]
    })

@router.put("/config", summary="更新系统配置")
async def update_system_config(
    config: SystemConfigUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    system_service.update_system_config(db, config)
    return success_response(message="配置更新成功")
