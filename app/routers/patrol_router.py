# 巡检任务模块路由 - /api/patrol
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
import json

from app.config.database import get_db
from app.schemas.common import ApiResponse, PagedData
from app.schemas.patrol import (
    PatrolTaskInfo, PatrolTaskStatistics, PatrolTaskAddRequest,
    PatrolTaskUpdateRequest, PatrolTaskDeleteRequest, PatrolTaskStatusRequest,
    PatrolRecordInfo, PatrolRecordStatistics, StartPatrolRequest, EndPatrolRequest
)
from app.models.user import SysUser
from app.models.patrol import PatrolTask, PatrolRecord
from app.models.sensor import PatrolSensorData
from app.models.alarm import PatrolAlarm
from app.models.system_log import SysLog
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/patrol", tags=["巡检模块"])


def create_log(db: Session, username: str, module: str, operation: str, ip: str, detail: str):
    log = SysLog(username=username, module=module, operation=operation, ip_address=ip, detail=detail)
    db.add(log)
    db.commit()


# 1. 获取巡检任务列表
@router.get("/task/list", summary="获取巡检任务列表")
async def get_task_list(
    page: int = 1, pageSize: int = 10, robot_sn: str = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取巡检任务列表"""
    query = db.query(PatrolTask)
    if robot_sn:
        query = query.filter(PatrolTask.robot_sn == robot_sn)
    
    total = query.count()
    tasks = query.offset((page - 1) * pageSize).limit(pageSize).all()
    
    task_list = [{
        "id": t.id, "task_name": t.task_name, "robot_sn": t.robot_sn,
        "cycle_type": t.cycle_type, "start_time": t.start_time, "end_time": t.end_time,
        "route_points": json.loads(t.route_points) if t.route_points else [],
        "status": t.status, "create_by": t.create_by, "remark": t.remark,
        "create_time": t.create_time.isoformat() if t.create_time else None,
        "update_time": t.update_time.isoformat() if t.update_time else None
    } for t in tasks]
    
    return ApiResponse(code=200, msg="success", data={
        "list": task_list, "total": total, "page": page, "pageSize": pageSize
    })


# 2. 获取巡检任务统计
@router.get("/task/statistics", summary="获取巡检任务统计")
async def get_task_statistics(
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取巡检任务统计"""
    total = db.query(PatrolTask).count()
    enabled = db.query(PatrolTask).filter(PatrolTask.status == 1).count()
    disabled = total - enabled
    
    return ApiResponse(code=200, msg="success", data={
        "total": total, "enabled": enabled, "disabled": disabled
    })


# 3. 添加巡检任务
@router.post("/task/add", summary="添加巡检任务")
async def add_task(
    request: PatrolTaskAddRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """添加巡检任务"""
    task = PatrolTask(
        task_name=request.task_name,
        robot_sn=request.robot_sn,
        cycle_type=request.cycle_type,
        start_time=request.start_time,
        end_time=request.end_time,
        route_points=json.dumps(request.route_points) if request.route_points else None,
        create_by=current_user.username
    )
    db.add(task)
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "巡检", "添加任务", ip, f"添加任务 {request.task_name}")
    
    return ApiResponse(code=200, msg="添加成功", data=None)


# 4. 更新巡检任务
@router.put("/task/update", summary="更新巡检任务")
async def update_task(
    request: PatrolTaskUpdateRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """更新巡检任务"""
    task = db.query(PatrolTask).filter(PatrolTask.id == request.id).first()
    if not task:
        return ApiResponse(code=404, msg="任务不存在", data=None)
    
    if request.task_name:
        task.task_name = request.task_name
    if request.cycle_type:
        task.cycle_type = request.cycle_type
    if request.start_time:
        task.start_time = request.start_time
    if request.end_time:
        task.end_time = request.end_time
    if request.route_points:
        task.route_points = json.dumps(request.route_points)
    if request.status:
        task.status = request.status
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "巡检", "更新任务", ip, f"更新任务 {task.task_name}")
    
    return ApiResponse(code=200, msg="更新成功", data=None)


# 5. 更新任务状态
@router.post("/task/status", summary="更新任务状态")
async def update_task_status(
    request: PatrolTaskStatusRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """更新任务状态"""
    task = db.query(PatrolTask).filter(PatrolTask.id == request.id).first()
    if not task:
        return ApiResponse(code=404, msg="任务不存在", data=None)
    
    task.status = request.status
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    status_text = "启用" if request.status == 1 else "停用"
    create_log(db, current_user.username, "巡检", "更新状态", ip, f"{status_text}任务 {task.task_name}")
    
    return ApiResponse(code=200, msg="状态更新成功", data=None)


# 6. 删除巡检任务
@router.post("/task/delete", summary="删除巡检任务")
async def delete_task(
    request: PatrolTaskDeleteRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """删除巡检任务"""
    task = db.query(PatrolTask).filter(PatrolTask.id == request.id).first()
    if not task:
        return ApiResponse(code=404, msg="任务不存在", data=None)
    
    task_name = task.task_name
    db.delete(task)
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "巡检", "删除任务", ip, f"删除任务 {task_name}")
    
    return ApiResponse(code=200, msg="删除成功", data=None)


# 7. 获取巡检记录列表
@router.get("/record/list", summary="获取巡检记录列表")
async def get_record_list(
    page: int = 1, pageSize: int = 10,
    robot_sn: str = None, startTime: str = None, endTime: str = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取巡检记录列表"""
    query = db.query(PatrolRecord)
    if robot_sn:
        query = query.filter(PatrolRecord.robot_sn == robot_sn)
    if startTime:
        query = query.filter(PatrolRecord.start_time >= startTime)
    if endTime:
        query = query.filter(PatrolRecord.start_time <= endTime)
    
    total = query.count()
    records = query.order_by(PatrolRecord.start_time.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    
    record_list = [{
        "id": r.id, "task_id": r.task_id, "robot_sn": r.robot_sn,
        "start_time": r.start_time.isoformat() if r.start_time else None,
        "end_time": r.end_time.isoformat() if r.end_time else None,
        "patrol_status": r.patrol_status, "data_count": r.data_count,
        "alarm_count": r.alarm_count, "patrol_result": r.patrol_result,
        "create_by": r.create_by, "create_time": r.create_time.isoformat() if r.create_time else None
    } for r in records]
    
    return ApiResponse(code=200, msg="success", data={
        "list": record_list, "total": total, "page": page, "pageSize": pageSize
    })


# 8. 获取巡检记录详情
@router.get("/record/{id}", summary="获取巡检记录详情")
async def get_record_detail(
    id: int,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取巡检记录详情"""
    record = db.query(PatrolRecord).filter(PatrolRecord.id == id).first()
    if not record:
        return ApiResponse(code=404, msg="记录不存在", data=None)
    
    return ApiResponse(code=200, msg="success", data={
        "id": record.id, "task_id": record.task_id, "robot_sn": record.robot_sn,
        "start_time": record.start_time.isoformat() if record.start_time else None,
        "end_time": record.end_time.isoformat() if record.end_time else None,
        "patrol_status": record.patrol_status, "data_count": record.data_count,
        "alarm_count": record.alarm_count, "patrol_result": record.patrol_result,
        "create_by": record.create_by, "create_time": record.create_time.isoformat() if record.create_time else None
    })


# 9. 获取巡检记录统计
@router.get("/record/statistics", summary="获取巡检记录统计")
async def get_record_statistics(
    startTime: str = None, endTime: str = None,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取巡检记录统计"""
    query = db.query(PatrolRecord)
    if startTime:
        query = query.filter(PatrolRecord.start_time >= startTime)
    if endTime:
        query = query.filter(PatrolRecord.start_time <= endTime)
    
    total = query.count()
    ongoing = query.filter(PatrolRecord.patrol_status == 1).count()
    completed = query.filter(PatrolRecord.patrol_status == 2).count()
    interrupted = query.filter(PatrolRecord.patrol_status == 3).count()
    
    total_data = db.query(func.sum(PatrolRecord.data_count)).scalar() or 0
    total_alarm = db.query(func.sum(PatrolRecord.alarm_count)).scalar() or 0
    
    return ApiResponse(code=200, msg="success", data={
        "total": total, "ongoing": ongoing, "completed": completed,
        "interrupted": interrupted, "total_data_count": total_data,
        "total_alarm_count": total_alarm
    })


# 10. 开始巡检
@router.post("/start", summary="开始巡检")
async def start_patrol(
    request: StartPatrolRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """开始巡检"""
    # 检查是否有进行中的巡检
    existing = db.query(PatrolRecord).filter(
        PatrolRecord.robot_sn == request.robot_sn,
        PatrolRecord.patrol_status == 1
    ).first()
    if existing:
        return ApiResponse(code=400, msg="该机器人正在巡检中", data=None)
    
    record = PatrolRecord(
        task_id=request.task_id,
        robot_sn=request.robot_sn,
        patrol_status=1,  # 进行中
        create_by=current_user.username
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "巡检", "开始巡检", ip, f"机器人 {request.robot_sn} 开始巡检")
    
    return ApiResponse(code=200, msg="巡检开始成功", data={"record_id": record.id})


# 11. 结束巡检
@router.post("/end", summary="结束巡检")
async def end_patrol(
    request: EndPatrolRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    http_request: Request = None
):
    """结束巡检"""
    record = db.query(PatrolRecord).filter(PatrolRecord.id == request.id).first()
    if not record:
        return ApiResponse(code=404, msg="巡检记录不存在", data=None)
    
    if record.patrol_status != 1:
        return ApiResponse(code=400, msg="巡检已结束", data=None)
    
    # 统计数据
    data_count = db.query(PatrolSensorData).filter(
        PatrolSensorData.patrol_record_id == record.id
    ).count()
    alarm_count = db.query(PatrolAlarm).filter(
        PatrolAlarm.robot_sn == record.robot_sn,
        PatrolAlarm.create_time >= record.start_time
    ).count()
    
    record.patrol_status = 2  # 已完成
    record.end_time = datetime.utcnow()
    record.data_count = data_count
    record.alarm_count = alarm_count
    record.patrol_result = request.patrol_result
    db.commit()
    
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, current_user.username, "巡检", "结束巡检", ip, f"机器人 {record.robot_sn} 结束巡检")
    
    return ApiResponse(code=200, msg="巡检结束成功", data=None)