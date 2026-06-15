"""
DeepSeek AI 路由模块
提供基于 DeepSeek API 的 AI 功能接口
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services.deepseek_service import deepseek_service
from app.schemas.deepseek import (
    SimpleChatRequest, SimpleChatResponse,
    EnvironmentAnalysisRequest, EnvironmentAnalysisResponse,
    ReportGenerationRequest, ReportGenerationResponse,
    NaturalLanguageQueryRequest, NaturalLanguageQueryResponse,
    EnvironmentPredictionRequest, EnvironmentPredictionResponse,
    InspectionPlanRequest, InspectionPlanResponse,
    EquipmentHealthRequest, EquipmentHealthResponse
)
from app.utils.response import success_response

router = APIRouter(prefix="/api/ai", tags=["AI 模块 (DeepSeek)"])

@router.post("/chat", summary="AI 对话")
async def ai_chat(
    request: SimpleChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    与 AI 进行对话
    
    参数:
        message: 用户消息
        system_prompt: 系统提示词 (可选)
    """
    response = deepseek_service.simple_chat(request.message, request.system_prompt)
    return success_response(data={"response": response}, message="对话成功")

@router.post("/analyze/environment", summary="环境数据分析")
async def analyze_environment(
    request: EnvironmentAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    分析环境数据
    
    参数:
        temperature: 温度
        humidity: 湿度
        smoke_level: 烟雾浓度
    """
    result = deepseek_service.analyze_environment(
        request.temperature,
        request.humidity,
        request.smoke_level
    )
    return success_response(data=result, message="分析完成")

@router.post("/generate/report", summary="生成分析报告")
async def generate_report(
    request: ReportGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成分析报告
    
    参数:
        type: 报告类型 (daily/weekly/monthly)
        data_points: 数据点数量
        start_time: 开始时间
        end_time: 结束时间
    """
    result = deepseek_service.generate_report(
        request.type,
        request.data_points,
        request.start_time,
        request.end_time
    )
    return success_response(data=result, message="报告生成成功")

@router.post("/query", summary="自然语言查询")
async def natural_language_query(
    request: NaturalLanguageQueryRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    自然语言查询
    
    参数:
        query: 查询语句
    """
    result = deepseek_service.natural_language_query(request.query)
    return success_response(data=result, message="查询完成")

@router.post("/predict/environment", summary="环境数据预测")
async def predict_environment(
    request: EnvironmentPredictionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    预测环境数据
    
    参数:
        current_temp: 当前温度
        current_humidity: 当前湿度
        hours: 预测小时数
    """
    result = deepseek_service.predict_environment(
        request.current_temp,
        request.current_humidity,
        request.hours
    )
    return success_response(data=result, message="预测完成")

@router.post("/inspection/plan", summary="生成巡检计划")
async def generate_inspection_plan(
    request: InspectionPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    生成巡检计划
    
    参数:
        location: 巡检地点
        time_range: 时间范围
        requirements: 巡检要求
    """
    result = deepseek_service.generate_inspection_plan(
        request.location,
        request.time_range,
        request.requirements
    )
    return success_response(data=result, message="巡检计划生成成功")

@router.post("/equipment/health", summary="设备健康分析")
async def analyze_equipment_health(
    request: EquipmentHealthRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    分析设备健康状态
    
    参数:
        equipment_name: 设备名称
        operation_hours: 运行时间
        error_count: 错误次数
        performance_data: 性能数据
    """
    result = deepseek_service.analyze_equipment_health(
        request.equipment_name,
        request.operation_hours,
        request.error_count,
        request.performance_data
    )
    return success_response(data=result, message="设备健康分析完成")