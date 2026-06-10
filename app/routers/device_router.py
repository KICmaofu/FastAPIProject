from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services import device_service
from app.schemas.device import DeviceResponse, DeviceStatsResponse, DeviceListResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api/devices", tags=["设备模块"])

@router.get("/stats", summary="获取设备统计")
async def get_device_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    stats = device_service.get_device_stats(db)
    return success_response(data=stats)

@router.get("", summary="获取设备列表")
async def get_device_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = device_service.get_device_list(db, page, size, status)

    device_list = []
    for device in result["list"]:
        device_list.append(DeviceResponse(
            id=device.id,
            name=device.name,
            type=device.type,
            model=device.model,
            status=device.status,
            location=device.location
        ))

    return success_response(data={
        "list": device_list,
        "total": result["total"],
        "page": result["page"]
    })

@router.get("/{deviceId}", summary="获取设备详情")
async def get_device_detail(
    deviceId: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    device = device_service.get_device_by_id(db, deviceId)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备不存在")
    return success_response(data=DeviceResponse.from_orm(device))
