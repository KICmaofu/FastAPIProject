"""
智能体路由模块
提供智能体功能的API接口
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.agent_service import agent_service
from typing import Optional, Dict, Any
from pydantic import BaseModel

router = APIRouter(prefix="/api/agent", tags=["智能体模块"])

class ChatRequest(BaseModel):
    query: str

@router.get("/status", summary="获取智能体综合状态")
async def get_agent_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取智能体综合状态信息
    """
    status = agent_service.get_agent_status()
    return {"code": 200, "message": "状态获取成功", "data": status, "timestamp": datetime.now().isoformat()}

@router.get("/database/status", summary="获取数据库连接状态")
async def get_database_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取数据库连接状态
    """
    status = agent_service.get_database_connection_status()
    return {"code": 200, "message": "数据库状态获取成功", "data": status, "timestamp": datetime.now().isoformat()}

@router.get("/system/metrics", summary="获取系统资源占用情况")
async def get_system_metrics(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取系统资源占用情况（CPU、内存、磁盘、网络）
    """
    metrics = agent_service.get_system_metrics()
    return {"code": 200, "message": "系统指标获取成功", "data": metrics, "timestamp": datetime.now().isoformat()}

@router.get("/business/metrics", summary="获取关键业务指标")
async def get_business_metrics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取关键业务指标（设备数量、告警数量、传感器数据统计等）
    """
    metrics = agent_service.get_business_metrics(db)
    return {"code": 200, "message": "业务指标获取成功", "data": metrics, "timestamp": datetime.now().isoformat()}

@router.post("/task/create", summary="创建分析任务")
async def create_task(
    task_type: str,
    parameters: Optional[Dict[str, Any]] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    创建分析任务
    
    参数:
        task_type: 任务类型 (query_analysis, business_metrics, trend_analysis, ai_insights)
        parameters: 任务参数
    """
    task_id = agent_service.add_task(task_type, parameters or {})
    return {"code": 200, "message": "任务创建成功", "data": {"taskId": task_id}, "timestamp": datetime.now().isoformat()}

@router.get("/task/{task_id}/execute", summary="执行任务")
async def execute_task(
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    执行指定任务
    """
    result = agent_service.execute_task(task_id, db)
    if result is None:
        raise HTTPException(status_code=404, detail="任务未找到或执行失败")
    return {"code": 200, "message": "任务执行完成", "data": result, "timestamp": datetime.now().isoformat()}

@router.get("/tasks", summary="获取任务队列")
async def get_task_queue(
    current_user: User = Depends(get_current_active_user)
):
    """
    获取当前任务队列状态
    """
    queue = agent_service.get_task_queue()
    return {"code": 200, "message": "任务队列获取成功", "data": queue, "timestamp": datetime.now().isoformat()}

@router.get("/trend/analysis", summary="获取趋势数据分析")
async def get_trend_analysis(
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    interval: str = Query("1h"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取趋势数据分析
    
    参数:
        start_time: 开始时间（默认24小时前）
        end_time: 结束时间（默认当前时间）
        interval: 时间间隔（1h, 6h, 1d）
    """
    if not end_time:
        end_time = datetime.now().isoformat()
    if not start_time:
        start_time = (datetime.now() - timedelta(hours=24)).isoformat()
    
    result = agent_service.get_trend_analysis(db, {
        "start_time": start_time,
        "end_time": end_time,
        "interval": interval
    })
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"code": 200, "message": "趋势分析获取成功", "data": result, "timestamp": datetime.now().isoformat()}

@router.post("/query/execute", summary="执行数据库查询")
async def execute_query(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    执行数据库查询（仅允许SELECT查询）
    
    参数:
        query: SQL查询语句
    """
    result = agent_service.execute_query_analysis(db, {"query": query})
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"code": 200, "message": "查询执行成功", "data": result, "timestamp": datetime.now().isoformat()}

@router.post("/ai/insights", summary="生成AI分析洞察")
async def generate_ai_insights(
    parameters: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成AI分析洞察，整合业务指标和系统数据进行深度分析
    
    参数:
        parameters: 分析参数（可选）
    """
    result = agent_service.generate_ai_insights(db, parameters or {})
    return {"code": 200, "message": "AI分析完成", "data": result, "timestamp": datetime.now().isoformat()}

@router.post("/chat", summary="自然语言交互查询")
async def natural_language_query(
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    自然语言交互查询
    
    参数:
        request: 包含查询内容的请求体
    """
    result = agent_service.natural_language_query(request.query, db)
    return {"code": 200, "message": "查询完成", "data": result, "timestamp": datetime.now().isoformat()}

@router.get("/alarms", summary="获取告警列表")
async def get_alarms(
    acknowledged: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取告警列表
    
    参数:
        acknowledged: 是否只获取已确认的告警（默认获取所有）
    """
    alarms = agent_service.get_alarms(acknowledged)
    return {"code": 200, "message": "告警列表获取成功", "data": alarms, "timestamp": datetime.now().isoformat()}

@router.post("/alarm/{alarm_id}/acknowledge", summary="确认告警")
async def acknowledge_alarm(
    alarm_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    确认指定告警
    
    参数:
        alarm_id: 告警ID
    """
    success = agent_service.acknowledge_alarm(alarm_id)
    if not success:
        raise HTTPException(status_code=404, detail="告警未找到")
    return {"code": 200, "message": "告警已确认", "data": {"alarmId": alarm_id}, "timestamp": datetime.now().isoformat()}