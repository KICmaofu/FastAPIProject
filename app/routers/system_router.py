# 系统日志模块路由 - /api/sys
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.common import ApiResponse
from app.models.user import SysUser
from app.models.system_log import SysLog
from app.dependencies.auth import require_admin

router = APIRouter(prefix="/api/sys", tags=["系统模块"])


# 健康检查
@router.get("/health", summary="健康检查")
async def health_check():
    """健康检查"""
    return ApiResponse(code=200, msg="fire-patrol-server is running", data=None)


# 1. 获取日志列表
@router.get("/log/list", summary="获取日志列表")
async def get_log_list(
    page: int = 1, pageSize: int = 10,
    username: str = None, startTime: str = None, endTime: str = None,
    current_user: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取日志列表（管理员）"""
    query = db.query(SysLog)
    if username:
        query = query.filter(SysLog.username == username)
    if startTime:
        query = query.filter(SysLog.create_time >= startTime)
    if endTime:
        query = query.filter(SysLog.create_time <= endTime)
    
    total = query.count()
    logs = query.order_by(SysLog.create_time.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    
    log_list = [{
        "id": l.id, "username": l.username, "module": l.module,
        "operation": l.operation, "ip_address": l.ip_address,
        "detail": l.detail, "create_time": l.create_time.isoformat() if l.create_time else None
    } for l in logs]
    
    return ApiResponse(code=200, msg="success", data={
        "list": log_list, "total": total, "page": page, "pageSize": pageSize
    })