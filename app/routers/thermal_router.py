from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services import sensor_service
from app.crud import thermal_data as thermal_data_crud, sensor_data as sensor_data_crud
from app.schemas.thermal import ThermalDataResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api", tags=["热成像模块"])

@router.get("/sse/latest-data", summary="获取热成像数据")
async def get_latest_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    thermal = thermal_data_crud.get_latest(db)

    if not thermal:
        return success_response(data={
            "maxTemp": [[0]*8 for _ in range(8)],
            "temperature": 0,
            "humidity": 0,
            "gas": 0,
            "battery": 0,
            "humanDetected": False
        })

    sensor_data = sensor_data_crud.get(db, thermal.sensor_data_id)

    return success_response(data=ThermalDataResponse(
        maxTemp=thermal.max_temp_matrix,
        temperature=sensor_data.temperature if sensor_data else 0,
        humidity=sensor_data.humidity if sensor_data else 0,
        gas=sensor_data.smoke_level if sensor_data else 0,
        battery=sensor_data.battery if sensor_data else 0,
        humanDetected=bool(sensor_data.human_detected) if sensor_data else False
    ))

@router.get("/thermal-imaging/history", summary="获取历史热成像数据")
async def get_thermal_history(
    startTime: str = Query(...),
    endTime: str = Query(...),
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from datetime import datetime
    try:
        start = datetime.fromisoformat(startTime)
        end = datetime.fromisoformat(endTime)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="时间格式错误")

    data = thermal_data_crud.get_multi_by_time_range(db, start, end, skip=(page-1)*size, limit=size)
    return success_response(data=data)
