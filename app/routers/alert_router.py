from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user, require_operator
from app.models.user import User
from app.services import alert_service
from app.schemas.alert import AlertResponse, AlertProcessRequest, AlertListResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api/alerts", tags=["告警模块"])

@router.get("", summary="获取告警列表")
async def get_alert_list(
    level: Optional[str] = Query(None, regex="^(warning|danger)$"),
    status: Optional[str] = Query(None, regex="^(pending|processed)$"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = alert_service.get_alert_list(db, level, status, page, size)

    alert_list = []
    for alert in result["list"]:
        alert_list.append(AlertResponse(
            id=alert.id,
            type=alert.type,
            level=alert.level,
            message=alert.message,
            device=alert.device_id,
            time=alert.create_time.isoformat(),
            status=alert.status
        ))

    return success_response(data={
        "list": alert_list,
        "total": result["total"],
        "page": result["page"]
    })

@router.put("/{alertId}/process", summary="处理告警")
async def process_alert(
    alertId: str,
    request: AlertProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    success = alert_service.process_alert(db, alertId, request.process_remark, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="告警不存在")
    return success_response(message="处理成功")
