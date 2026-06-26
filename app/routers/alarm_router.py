# 告警模块路由 - /api/alarm
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.config.database import get_db
from app.schemas.common import ApiResponse, PagedData
from app.schemas.alarm import (
    AlarmInfo, AlarmDetail, AlarmStatistics, AlarmTrend,
    DealAlarmRequest, AlarmDeleteRequest
)
from app.models.user import SysUser
from app.models.alarm import PatrolAlarm
from app.models.sensor import PatrolSensorData
from app.models.system_log import SysLog
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/alarm", tags=["告警模块"])


def create_log(db: Session, username: str, module: str, operation: str, ip: str, detail: str):
    log = SysLog(username=username, module=module, operation=operation, ip_address=ip, detail=detail)
    db.add(log)
    db.commit()


# 1. 获取告警列表
@router.get("/list", summary="获取告警列表")
async def get_alarm_list(
    page: int = 1, pageSize: int = 10,
    alarm_level: str = None, deal_status: int = None,
    robot_sn: str = None, startTime: str = None, endTime: str = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取告警列表"""
    query = db.query(PatrolAlarm)
    if alarm_level:
        query = query.filter(PatrolAlarm.alarm_level == alarm_level)
    if deal_status is not None:
        query = query.filter(PatrolAlarm.deal_status == deal_status)
    if robot_sn:
        query = query.filter(PatrolAlarm.robot_sn == robot_sn)
    if startTime:
        query = query.filter(PatrolAlarm.create_time >= startTime)
    if endTime:
        query = query.filter(PatrolAlarm.create_time <= endTime)
    
    total = query.count()
    alarms = query.order_by(PatrolAlarm.create_time.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    
    alarm_list = [{
        "id": a.id, "robot_sn": a.robot_sn, "sensor_record_id": a.sensor_record_id,
        "hardware_alarm_type": a.hardware_alarm_type, "alarm_type": a.alarm_type,
        "alarm_level": a.alarm_level, "alarm_desc": a.alarm_desc,
        "area_name": a.area_name, "point_name": a.point_name,
        "deal_status": a.deal_status, "deal_user": a.deal_user,
        "deal_content": a.deal_content,
        "deal_time": a.deal_time.isoformat() if a.deal_time else None,
        "create_time": a.create_time.isoformat() if a.create_time else None
    } for a in alarms]
    
    return ApiResponse(code=200, msg="success", data={
        "list": alarm_list, "total": total, "page": page, "pageSize": pageSize
    })


# 2. 获取告警详情
@router.get("/{id}", summary="获取告警详情")
async def get_alarm_detail(
    id: int,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取告警详情"""
    alarm = db.query(PatrolAlarm).filter(PatrolAlarm.id == id).first()
    if not alarm:
        return ApiResponse(code=404, msg="告警不存在", data=None)
    
    # 获取关联传感器数据
    sensor_data = None
    if alarm.sensor_record_id:
        sensor = db.query(PatrolSensorData).filter(PatrolSensorData.id == alarm.sensor_record_id).first()
        if sensor:
            sensor_data = {
                "temperature": sensor.temperature,
                "humidity": sensor.humidity,
                "smoke_level": sensor.smoke_level,
                "max_single_temp": sensor.max_single_temp,
                "collect_time": sensor.collect_time.isoformat() if sensor.collect_time else None
            }
    
    return ApiResponse(code=200, msg="success", data={
        "id": alarm.id, "robot_sn": alarm.robot_sn,
        "alarm_level": alarm.alarm_level, "alarm_desc": alarm.alarm_desc,
        "sensor_data": sensor_data
    })


# 3. 处置告警
@router.post("/deal", summary="处置告警")
async def deal_alarm(
    request: DealAlarmRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """处置告警"""
    alarm = db.query(PatrolAlarm).filter(PatrolAlarm.id == request.id).first()
    if not alarm:
        return ApiResponse(code=404, msg="告警不存在", data=None)
    
    if alarm.deal_status == 1:
        return ApiResponse(code=400, msg="告警已处理", data=None)
    
    alarm.deal_status = 1
    alarm.deal_user = current_user.username
    alarm.deal_content = request.deal_content
    alarm.deal_time = datetime.utcnow()
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "告警", "处置", ip, f"处置告警 {request.id}")
    
    return ApiResponse(code=200, msg="处置成功", data=None)


# 4. 删除告警
@router.post("/delete", summary="删除告警")
async def delete_alarm(
    request: AlarmDeleteRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """删除告警"""
    alarm = db.query(PatrolAlarm).filter(PatrolAlarm.id == request.id).first()
    if not alarm:
        return ApiResponse(code=404, msg="告警不存在", data=None)
    
    db.delete(alarm)
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "告警", "删除", ip, f"删除告警 {request.id}")
    
    return ApiResponse(code=200, msg="删除成功", data=None)


# 5. 获取告警统计
@router.get("/statistics", summary="获取告警统计")
async def get_alarm_statistics(
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取告警统计"""
    total = db.query(PatrolAlarm).count()
    red = db.query(PatrolAlarm).filter(PatrolAlarm.alarm_level == "RED").count()
    orange = db.query(PatrolAlarm).filter(PatrolAlarm.alarm_level == "ORANGE").count()
    normal = db.query(PatrolAlarm).filter(PatrolAlarm.alarm_level == "NORMAL").count()
    pending = db.query(PatrolAlarm).filter(PatrolAlarm.deal_status == 0).count()
    dealt = db.query(PatrolAlarm).filter(PatrolAlarm.deal_status == 1).count()
    
    return ApiResponse(code=200, msg="success", data={
        "total": total, "red": red, "orange": orange,
        "normal": normal, "pending": pending, "dealt": dealt
    })


# 6. 获取最近告警
@router.get("/recent", summary="获取最近告警")
async def get_recent_alarms(
    limit: int = 10,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取最近告警"""
    alarms = db.query(PatrolAlarm).order_by(
        PatrolAlarm.create_time.desc()
    ).limit(limit).all()
    
    alarm_list = [{
        "id": a.id, "robot_sn": a.robot_sn,
        "alarm_level": a.alarm_level, "alarm_desc": a.alarm_desc,
        "deal_status": a.deal_status,
        "create_time": a.create_time.isoformat() if a.create_time else None
    } for a in alarms]
    
    return ApiResponse(code=200, msg="success", data=alarm_list)


# 7. 获取告警趋势
@router.get("/trend", summary="获取告警趋势")
async def get_alarm_trend(
    days: int = 7,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取告警趋势"""
    labels = []
    level1_data = []
    level2_data = []
    level3_data = []
    
    for i in range(days):
        date = datetime.utcnow() - timedelta(days=days - i - 1)
        date_str = date.strftime("%m/%d")
        labels.append(date_str)
        
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        
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