# 报表模块路由 - /api/report
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.config.database import get_db
from app.schemas.common import ApiResponse
from app.models.user import SysUser
from app.models.sensor import PatrolSensorData
from app.models.alarm import PatrolAlarm
from app.models.patrol import PatrolRecord
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/report", tags=["报表模块"])


# 1. 获取环境趋势
@router.get("/env/trend", summary="获取环境趋势")
async def get_env_trend(
    robot_sn: str = None, startTime: str = None, endTime: str = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取环境趋势"""
    # 默认今天
    if not startTime:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        startTime = today.isoformat()
    if not endTime:
        endTime = datetime.utcnow().isoformat()
    
    query = db.query(PatrolSensorData).filter(
        PatrolSensorData.collect_time >= startTime,
        PatrolSensorData.collect_time <= endTime
    )
    if robot_sn:
        query = query.filter(PatrolSensorData.robot_sn == robot_sn)
    
    records = query.order_by(PatrolSensorData.collect_time.asc()).all()
    
    trend_data = [{
        "time": r.collect_time.isoformat() if r.collect_time else None,
        "temperature": r.temperature,
        "humidity": r.humidity,
        "smoke_level": r.smoke_level,
        "max_single_temp": r.max_single_temp
    } for r in records]
    
    return ApiResponse(code=200, msg="success", data=trend_data)


# 2. 获取告警趋势
@router.get("/alarm/trend", summary="获取告警趋势")
async def get_alarm_trend(
    type: str = "day",
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取告警趋势"""
    labels = []
    level1_data = []
    level2_data = []
    level3_data = []
    
    if type == "day":
        # 当天按小时统计
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        for hour in range(24):
            start = today + timedelta(hours=hour)
            end = start + timedelta(hours=1)
            labels.append(start.strftime("%H:00"))
            
            level1 = db.query(PatrolAlarm).filter(
                PatrolAlarm.alarm_level == "RED",
                PatrolAlarm.create_time >= start,
                PatrolAlarm.create_time < end
            ).count()
            
            level2 = db.query(PatrolAlarm).filter(
                PatrolAlarm.alarm_level == "ORANGE",
                PatrolAlarm.create_time >= start,
                PatrolAlarm.create_time < end
            ).count()
            
            level3 = db.query(PatrolAlarm).filter(
                PatrolAlarm.alarm_level == "NORMAL",
                PatrolAlarm.create_time >= start,
                PatrolAlarm.create_time < end
            ).count()
            
            level1_data.append(level1)
            level2_data.append(level2)
            level3_data.append(level3)
    else:
        # 近7天按天统计
        for i in range(7):
            date = datetime.utcnow() - timedelta(days=6 - i)
            start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end = start + timedelta(days=1)
            labels.append(start.strftime("%m/%d"))
            
            level1 = db.query(PatrolAlarm).filter(
                PatrolAlarm.alarm_level == "RED",
                PatrolAlarm.create_time >= start,
                PatrolAlarm.create_time < end
            ).count()
            
            level2 = db.query(PatrolAlarm).filter(
                PatrolAlarm.alarm_level == "ORANGE",
                PatrolAlarm.create_time >= start,
                PatrolAlarm.create_time < end
            ).count()
            
            level3 = db.query(PatrolAlarm).filter(
                PatrolAlarm.alarm_level == "NORMAL",
                PatrolAlarm.create_time >= start,
                PatrolAlarm.create_time < end
            ).count()
            
            level1_data.append(level1)
            level2_data.append(level2)
            level3_data.append(level3)
    
    return ApiResponse(code=200, msg="success", data={
        "labels": labels, "level1": level1_data,
        "level2": level2_data, "level3": level3_data
    })


# 3. 获取日报
@router.get("/daily", summary="获取日报")
async def get_daily_report(
    startTime: str = None, endTime: str = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取日报"""
    # 默认今天
    if not startTime:
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        startTime = today.isoformat()
    if not endTime:
        endTime = datetime.utcnow().isoformat()
    
    # 统计巡检
    total_patrol = db.query(PatrolRecord).filter(
        PatrolRecord.start_time >= startTime,
        PatrolRecord.start_time <= endTime
    ).count()
    
    completed_patrol = db.query(PatrolRecord).filter(
        PatrolRecord.start_time >= startTime,
        PatrolRecord.start_time <= endTime,
        PatrolRecord.patrol_status == 2
    ).count()
    
    # 统计告警
    total_alarm = db.query(PatrolAlarm).filter(
        PatrolAlarm.create_time >= startTime,
        PatrolAlarm.create_time <= endTime
    ).count()
    
    processed_alarm = db.query(PatrolAlarm).filter(
        PatrolAlarm.create_time >= startTime,
        PatrolAlarm.create_time <= endTime,
        PatrolAlarm.deal_status == 1
    ).count()
    
    # 统计环境
    sensor_query = db.query(PatrolSensorData).filter(
        PatrolSensorData.collect_time >= startTime,
        PatrolSensorData.collect_time <= endTime
    )
    
    avg_temp = sensor_query.with_entities(
        func.avg(PatrolSensorData.temperature)
    ).scalar()
    
    avg_humidity = sensor_query.with_entities(
        func.avg(PatrolSensorData.humidity)
    ).scalar()
    
    max_temp = sensor_query.with_entities(
        func.max(PatrolSensorData.max_single_temp)
    ).scalar()
    
    date_str = datetime.utcnow().strftime("%Y-%m-%d")
    
    return ApiResponse(code=200, msg="success", data={
        "date": date_str,
        "total_patrol": total_patrol,
        "completed_patrol": completed_patrol,
        "total_alarm": total_alarm,
        "processed_alarm": processed_alarm,
        "avg_temperature": avg_temp,
        "avg_humidity": avg_humidity,
        "max_temperature": max_temp
    })