from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services import sensor_service
from app.schemas.sensor import SensorResponse, SensorListResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api/sensors", tags=["传感器模块"])

@router.get("/temperature", summary="获取最新温度数据")
async def get_latest_temperature(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有传感器的最新温度数据（平均值）"""
    data = sensor_service.get_latest_temperature(db)
    return success_response(data=data, message="温度数据获取成功")

@router.get("/humidity", summary="获取最新湿度数据")
async def get_latest_humidity(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有传感器的最新湿度数据（平均值）"""
    data = sensor_service.get_latest_humidity(db)
    return success_response(data=data, message="湿度数据获取成功")

@router.get("/gas", summary="获取最新可燃气体数据")
async def get_latest_gas(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """获取所有传感器的最新可燃气体浓度数据（最大值）"""
    data = sensor_service.get_latest_gas(db)
    return success_response(data=data, message="可燃气体数据获取成功")

@router.get("", summary="获取传感器数据")
async def get_sensor_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sensors = sensor_service.get_sensor_list(db)

    sensor_list = []
    for sensor in sensors:
        sensor_list.append(SensorResponse(
            id=sensor.id,
            name=sensor.name,
            type=sensor.type,
            unit=sensor.unit,
            status=sensor.status
        ))

    return success_response(data={"list": sensor_list})
