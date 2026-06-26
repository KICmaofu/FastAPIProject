# AI智能模块路由 - /api/ai
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.config.database import get_db
from app.schemas.common import ApiResponse, PagedData
from app.schemas.ai import (
    AlarmAnalyzeRequest, AiChatRequest, ReportAnalyzeRequest
)
from app.models.user import SysUser
from app.models.ai_chat import AiChatRecord
from app.models.alarm import PatrolAlarm
from app.models.sensor import PatrolSensorData
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/ai", tags=["AI智能模块"])


# 模拟AI分析函数
def mock_ai_analysis(alarm_info: dict) -> str:
    """模拟AI分析结果"""
    level = alarm_info.get("alarm_level", "NORMAL")
    desc = alarm_info.get("alarm_desc", "")
    
    if level == "RED":
        return f"【严重告警分析】{desc}。建议立即处理：1. 现场确认情况；2. 检查相关设备；3. 启动应急预案。"
    elif level == "ORANGE":
        return f"【预警分析】{desc}。建议：1. 加强监控频率；2. 准备应对措施；3. 关注发展趋势。"
    else:
        return f"【提示信息】{desc}。建议：1. 记录异常情况；2. 定期复查确认。"


def mock_ai_chat(message: str, context: dict = None) -> str:
    """模拟AI对话"""
    return f"针对您的问题「{message}」，AI智能助手分析如下：根据当前系统数据和巡检记录，建议您关注重点区域的监控状态，及时处理潜在风险。如有更多问题，请继续提问。"


# 1. AI分析告警
@router.post("/alarm/analyze", summary="AI分析告警")
async def analyze_alarm(
    request: AlarmAnalyzeRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI分析告警"""
    alarm = db.query(PatrolAlarm).filter(PatrolAlarm.id == request.alarm_id).first()
    if not alarm:
        return ApiResponse(code=404, msg="告警不存在", data=None)
    
    # 获取传感器数据
    sensor_data = None
    if alarm.sensor_record_id:
        sensor = db.query(PatrolSensorData).filter(PatrolSensorData.id == alarm.sensor_record_id).first()
        if sensor:
            sensor_data = {
                "temperature": sensor.temperature,
                "humidity": sensor.humidity,
                "smoke_level": sensor.smoke_level,
                "max_single_temp": sensor.max_single_temp
            }
    
    alarm_info = {
        "alarm_level": alarm.alarm_level,
        "alarm_desc": alarm.alarm_desc,
        "robot_sn": alarm.robot_sn,
        "sensor_data": sensor_data
    }
    
    analysis = mock_ai_analysis(alarm_info)
    
    # 记录AI对话
    chat_record = AiChatRecord(
        user_id=current_user.id,
        user_query=f"分析告警 #{request.alarm_id}",
        ai_answer=analysis,
        chat_type=2,  # 告警自动分析
        relate_alarm_id=request.alarm_id,
        relate_robot_sn=alarm.robot_sn
    )
    db.add(chat_record)
    db.commit()
    
    return ApiResponse(code=200, msg="success", data={"analysis": analysis})


# 2. AI对话
@router.post("/chat", summary="AI对话")
async def ai_chat(
    request: AiChatRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI对话"""
    context = {}
    if request.relate_alarm_id:
        alarm = db.query(PatrolAlarm).filter(PatrolAlarm.id == request.relate_alarm_id).first()
        if alarm:
            context["alarm"] = {
                "level": alarm.alarm_level,
                "desc": alarm.alarm_desc
            }
    if request.relate_robot_sn:
        context["robot_sn"] = request.relate_robot_sn
    
    answer = mock_ai_chat(request.message, context)
    
    # 记录AI对话
    chat_record = AiChatRecord(
        user_id=current_user.id,
        user_query=request.message,
        ai_answer=answer,
        chat_type=1,  # 手动问答
        relate_alarm_id=request.relate_alarm_id,
        relate_robot_sn=request.relate_robot_sn
    )
    db.add(chat_record)
    db.commit()
    
    return ApiResponse(code=200, msg="success", data={"answer": answer})


# 3. 获取对话历史
@router.get("/chat/list", summary="获取对话历史")
async def get_chat_history(
    page: int = 1, pageSize: int = 20,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取对话历史"""
    query = db.query(AiChatRecord).filter(AiChatRecord.user_id == current_user.id)
    
    total = query.count()
    records = query.order_by(AiChatRecord.create_time.desc()).offset((page - 1) * pageSize).limit(pageSize).all()
    
    chat_list = [{
        "id": r.id, "user_query": r.user_query, "ai_answer": r.ai_answer,
        "chat_type": r.chat_type, "relate_alarm_id": r.relate_alarm_id,
        "relate_robot_sn": r.relate_robot_sn,
        "create_time": r.create_time.isoformat() if r.create_time else None
    } for r in records]
    
    return ApiResponse(code=200, msg="success", data={
        "list": chat_list, "total": total, "page": page, "pageSize": pageSize
    })


# 4. AI分析报表
@router.post("/report/analyze", summary="AI分析报表")
async def analyze_report(
    request: ReportAnalyzeRequest,
    current_user: SysUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """AI分析报表"""
    # 构建分析内容
    analysis = f"【报表智能分析】"
    if request.robot_sn:
        analysis += f"机器人 {request.robot_sn}："
    else:
        analysis += "全系统："
    
    analysis += "巡检数据正常，环境监测指标在安全范围内。建议：1. 保持当前巡检频率；2. 关注告警趋势变化；3. 定期检查设备状态。"
    
    # 记录AI对话
    chat_record = AiChatRecord(
        user_id=current_user.id,
        user_query="报表分析",
        ai_answer=analysis,
        chat_type=3,  # 报表AI解读
        relate_robot_sn=request.robot_sn
    )
    db.add(chat_record)
    db.commit()
    
    return ApiResponse(code=200, msg="success", data={"analysis": analysis})