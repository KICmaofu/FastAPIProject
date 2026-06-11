from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.password_verify import require_password_verified, verify_user_password
from app.models.user import User
from app.services import device_service
from app.schemas.device import DeviceResponse, DeviceStatsResponse, DeviceListResponse, DeviceCreate, DeviceUpdate
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

@router.post("", summary="创建设备（需密码验证）")
async def create_device(
    device_data: DeviceCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    创建新设备
    
    此操作需要用户输入密码进行二次验证。
    请求体需要包含password字段。
    """
    # 手动验证密码（从请求体中获取）
    body = await request.body()
    import json
    try:
        data = json.loads(body)
        password = data.get('password')
    except:
        password = None
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不能为空"
        )
    
    # 验证密码
    verify_user_password(db, current_user, password, "创建设备", request)
    
    # 移除password字段，只保留设备数据
    device_dict = device_data.model_dump(exclude={'password'})
    
    device = device_service.create_device(db, DeviceCreate(**device_dict))
    return success_response(data=DeviceResponse.from_orm(device), message="设备创建成功")

@router.put("/{deviceId}", summary="更新设备（需密码验证）")
async def update_device(
    deviceId: str,
    device_data: DeviceUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新设备信息
    
    此操作需要用户输入密码进行二次验证。
    请求体需要包含password字段。
    """
    # 手动验证密码（从请求体中获取）
    body = await request.body()
    import json
    try:
        data = json.loads(body)
        password = data.get('password')
    except:
        password = None
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不能为空"
        )
    
    # 验证密码
    verify_user_password(db, current_user, password, "更新设备", request)
    
    # 移除password字段，只保留设备数据
    device_dict = device_data.model_dump(exclude={'password'}, exclude_unset=True)
    
    device = device_service.update_device(db, deviceId, DeviceUpdate(**device_dict))
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备不存在")
    return success_response(data=DeviceResponse.from_orm(device), message="设备更新成功")

@router.delete("/{deviceId}", summary="删除设备（需密码验证）")
async def delete_device(
    deviceId: str,
    request: Request,
    password: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除设备
    
    此操作需要用户输入密码进行二次验证。
    请求参数需要包含password字段。
    """
    verify_user_password(db, current_user, password, "删除设备", request)
    
    success = device_service.delete_device(db, deviceId)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="设备不存在")
    return success_response(message="设备删除成功")
