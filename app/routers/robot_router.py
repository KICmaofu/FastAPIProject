# 机器人模块路由 - /api/robot
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional

from app.config.database import get_db
from app.schemas.common import ApiResponse, PagedData
from app.schemas.robot import (
    RobotInfo, RobotStatistics, RobotAddRequest, RobotUpdateRequest,
    RobotDeleteRequest, SendCmdRequest, CmdRecordInfo, SensorDataInfo
)
from app.models.user import SysUser
from app.models.robot import PatrolRobot, RobotCmdRecord
from app.models.sensor import PatrolSensorData
from app.models.system_log import SysLog
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/robot", tags=["机器人模块"])


def create_log(db: Session, username: str, module: str, operation: str, ip: str, detail: str):
    log = SysLog(username=username, module=module, operation=operation, ip_address=ip, detail=detail)
    db.add(log)
    db.commit()


# 1. 获取机器人列表
@router.get("/list", summary="获取机器人列表")
async def get_robot_list(
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机器人列表"""
    robots = db.query(PatrolRobot).all()
    robot_list = [{
        "id": r.id, "robot_sn": r.robot_sn, "robot_name": r.robot_name,
        "area_name": r.area_name, "online_status": r.online_status,
        "battery": r.battery, "run_mode": r.run_mode,
        "firmware_version": r.firmware_version, "last_upload_time": r.last_upload_time.isoformat() if r.last_upload_time else None,
        "create_by": r.create_by, "remark": r.remark,
        "create_time": r.create_time.isoformat() if r.create_time else None,
        "update_time": r.update_time.isoformat() if r.update_time else None
    } for r in robots]
    return ApiResponse(code=200, msg="success", data=robot_list)


# 2. 获取机器人详情
@router.get("/{id}", summary="获取机器人详情")
async def get_robot_detail(
    id: int,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机器人详情"""
    robot = db.query(PatrolRobot).filter(PatrolRobot.id == id).first()
    if not robot:
        return ApiResponse(code=404, msg="机器人不存在", data=None)
    
    return ApiResponse(code=200, msg="success", data={
        "id": robot.id, "robot_sn": robot.robot_sn, "robot_name": robot.robot_name,
        "area_name": robot.area_name, "online_status": robot.online_status,
        "battery": robot.battery, "run_mode": robot.run_mode,
        "firmware_version": robot.firmware_version, "last_upload_time": robot.last_upload_time.isoformat() if robot.last_upload_time else None,
        "create_by": robot.create_by, "remark": robot.remark,
        "create_time": robot.create_time.isoformat() if robot.create_time else None,
        "update_time": robot.update_time.isoformat() if robot.update_time else None
    })


# 3. 按SN获取机器人
@router.get("/sn/{robot_sn}", summary="按SN获取机器人")
async def get_robot_by_sn(
    robot_sn: str,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按SN获取机器人"""
    robot = db.query(PatrolRobot).filter(PatrolRobot.robot_sn == robot_sn).first()
    if not robot:
        return ApiResponse(code=404, msg="机器人不存在", data=None)
    
    return ApiResponse(code=200, msg="success", data={
        "id": robot.id, "robot_sn": robot.robot_sn, "robot_name": robot.robot_name,
        "area_name": robot.area_name, "online_status": robot.online_status,
        "battery": robot.battery, "run_mode": robot.run_mode,
        "firmware_version": robot.firmware_version, "last_upload_time": robot.last_upload_time.isoformat() if robot.last_upload_time else None,
        "create_by": robot.create_by, "remark": robot.remark,
        "create_time": robot.create_time.isoformat() if robot.create_time else None,
        "update_time": robot.update_time.isoformat() if robot.update_time else None
    })


# 4. 获取机器人统计
@router.get("/statistics", summary="获取机器人统计")
async def get_robot_statistics(
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取机器人统计"""
    total = db.query(PatrolRobot).count()
    online = db.query(PatrolRobot).filter(PatrolRobot.online_status == 1).count()
    offline = total - online
    
    return ApiResponse(code=200, msg="success", data={
        "total": total, "online": online, "offline": offline
    })


# 5. 添加机器人
@router.post("/add", summary="添加机器人")
async def add_robot(
    request: RobotAddRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """添加机器人"""
    existing = db.query(PatrolRobot).filter(PatrolRobot.robot_sn == request.robot_sn).first()
    if existing:
        return ApiResponse(code=400, msg="机器人SN已存在", data=None)
    
    robot = PatrolRobot(
        robot_sn=request.robot_sn,
        robot_name=request.robot_name,
        area_name=request.area_name,
        remark=request.remark,
        create_by=current_user.username
    )
    db.add(robot)
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "机器人", "添加", ip, f"添加机器人 {request.robot_sn}")
    
    return ApiResponse(code=200, msg="添加成功", data=None)


# 6. 更新机器人
@router.put("/update", summary="更新机器人")
async def update_robot(
    request: RobotUpdateRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """更新机器人"""
    robot = db.query(PatrolRobot).filter(PatrolRobot.id == request.id).first()
    if not robot:
        return ApiResponse(code=404, msg="机器人不存在", data=None)
    
    if request.robot_name:
        robot.robot_name = request.robot_name
    if request.area_name:
        robot.area_name = request.area_name
    if request.remark:
        robot.remark = request.remark
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "机器人", "更新", ip, f"更新机器人 {robot.robot_sn}")
    
    return ApiResponse(code=200, msg="更新成功", data=None)


# 7. 删除机器人
@router.post("/delete", summary="删除机器人")
async def delete_robot(
    request: RobotDeleteRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """删除机器人"""
    robot = db.query(PatrolRobot).filter(PatrolRobot.id == request.id).first()
    if not robot:
        return ApiResponse(code=404, msg="机器人不存在", data=None)
    
    robot_sn = robot.robot_sn
    db.delete(robot)
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "机器人", "删除", ip, f"删除机器人 {robot_sn}")
    
    return ApiResponse(code=200, msg="删除成功", data=None)


# 8. 发送控制命令
@router.post("/sendCmd", summary="发送控制命令")
async def send_cmd(
    request: SendCmdRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """发送控制命令"""
    robot = db.query(PatrolRobot).filter(PatrolRobot.robot_sn == request.robot_sn).first()
    if not robot:
        return ApiResponse(code=404, msg="机器人不存在", data=None)
    
    # 创建指令记录
    cmd_record = RobotCmdRecord(
        robot_sn=request.robot_sn,
        cmd_code=request.cmd_code,
        cmd_param=request.param,
        operator=current_user.username,
        cmd_status=1  # 已下发
    )
    db.add(cmd_record)
    db.commit()
    db.refresh(cmd_record)
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "机器人", "发送指令", ip, f"向 {request.robot_sn} 发送指令 {request.cmd_code}")
    
    return ApiResponse(code=200, msg="指令下发成功", data={"cmd_id": cmd_record.id})


# 9. 获取指令记录
@router.get("/cmd/list", summary="获取指令记录")
async def get_cmd_list(
    robot_sn: str = None, page: int = 1, pageSize: int = 10, cmd_status: int = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取指令记录"""
    query = db.query(RobotCmdRecord)
    if robot_sn:
        query = query.filter(RobotCmdRecord.robot_sn == robot_sn)
    if cmd_status:
        query = query.filter(RobotCmdRecord.cmd_status == cmd_status)
    
    total = query.count()
    records = query.order_by(RobotCmdRecord.send_time.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    
    cmd_list = [{
        "id": r.id, "robot_sn": r.robot_sn, "sensor_record_id": r.sensor_record_id,
        "cmd_code": r.cmd_code, "hardware_cmd": r.hardware_cmd, "cmd_param": r.cmd_param,
        "operator": r.operator, "send_time": r.send_time.isoformat() if r.send_time else None,
        "response_code": r.response_code, "response_msg": r.response_msg,
        "finish_time": r.finish_time.isoformat() if r.finish_time else None,
        "cmd_status": r.cmd_status
    } for r in records]
    
    return ApiResponse(code=200, msg="success", data={
        "list": cmd_list, "total": total, "page": page, "pageSize": pageSize
    })


# 10. 获取传感器历史数据
@router.get("/sensor/history", summary="获取传感器历史数据")
async def get_sensor_history(
    robot_sn: str = None, page: int = 1, pageSize: int = 20,
    startTime: str = None, endTime: str = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取传感器历史数据"""
    query = db.query(PatrolSensorData)
    if robot_sn:
        query = query.filter(PatrolSensorData.robot_sn == robot_sn)
    if startTime:
        query = query.filter(PatrolSensorData.collect_time >= startTime)
    if endTime:
        query = query.filter(PatrolSensorData.collect_time <= endTime)
    
    total = query.count()
    records = query.order_by(PatrolSensorData.collect_time.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    
    sensor_list = [{
        "id": r.id, "robot_sn": r.robot_sn, "patrol_record_id": r.patrol_record_id,
        "temperature": r.temperature, "humidity": r.humidity, "smoke_level": r.smoke_level,
        "max_single_temp": r.max_single_temp, "human_detected": r.human_detected,
        "fire_risk": r.fire_risk, "thermal_matrix": r.thermal_matrix,
        "battery": r.battery, "collect_time": r.collect_time.isoformat() if r.collect_time else None
    } for r in records]
    
    return ApiResponse(code=200, msg="success", data={
        "list": sensor_list, "total": total, "page": page, "pageSize": pageSize
    })


# 11. 获取最新传感器数据
@router.get("/sensor/latest/{robot_sn}", summary="获取最新传感器数据")
async def get_sensor_latest(
    robot_sn: str,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取最新传感器数据"""
    sensor = db.query(PatrolSensorData).filter(
        PatrolSensorData.robot_sn == robot_sn
    ).order_by(PatrolSensorData.collect_time.desc()).first()
    
    if not sensor:
        return ApiResponse(code=404, msg="无传感器数据", data=None)
    
    return ApiResponse(code=200, msg="success", data={
        "id": sensor.id, "robot_sn": sensor.robot_sn, "patrol_record_id": sensor.patrol_record_id,
        "temperature": sensor.temperature, "humidity": sensor.humidity, "smoke_level": sensor.smoke_level,
        "max_single_temp": sensor.max_single_temp, "human_detected": sensor.human_detected,
        "fire_risk": sensor.fire_risk, "thermal_matrix": sensor.thermal_matrix,
        "battery": sensor.battery, "collect_time": sensor.collect_time.isoformat() if sensor.collect_time else None
    })


# 12. 获取传感器统计
@router.get("/sensor/statistics", summary="获取传感器统计")
async def get_sensor_statistics(
    robot_sn: str = None, startTime: str = None, endTime: str = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取传感器统计"""
    query = db.query(PatrolSensorData)
    if robot_sn:
        query = query.filter(PatrolSensorData.robot_sn == robot_sn)
    if startTime:
        query = query.filter(PatrolSensorData.collect_time >= startTime)
    if endTime:
        query = query.filter(PatrolSensorData.collect_time <= endTime)
    
    result = query.with_entities(
        func.count(PatrolSensorData.id).label('count'),
        func.avg(PatrolSensorData.temperature).label('avg_temp'),
        func.avg(PatrolSensorData.humidity).label('avg_humidity'),
        func.avg(PatrolSensorData.smoke_level).label('avg_smoke'),
        func.max(PatrolSensorData.max_single_temp).label('max_temp'),
        func.min(PatrolSensorData.temperature).label('min_temp')
    ).first()
    
    return ApiResponse(code=200, msg="success", data={
        "data_count": result.count or 0,
        "avg_temperature": result.avg_temp,
        "avg_humidity": result.avg_humidity,
        "avg_smoke_level": result.avg_smoke,
        "max_temperature": result.max_temp,
        "min_temperature": result.min_temp
    })