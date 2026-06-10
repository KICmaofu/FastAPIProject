from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services import sensor_service
from app.schemas.sensor import SensorResponse, SensorListResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api/sensors", tags=["传感器模块"])

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
