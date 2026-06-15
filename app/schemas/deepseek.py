"""
DeepSeek 相关的数据模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class SimpleChatRequest(BaseModel):
    """简单对话请求"""
    message: str = Field(..., description="用户消息")
    system_prompt: Optional[str] = Field(None, description="系统提示词")

class SimpleChatResponse(BaseModel):
    """简单对话响应"""
    response: str = Field(..., description="AI 回复")

class EnvironmentAnalysisRequest(BaseModel):
    """环境分析请求"""
    temperature: float = Field(..., description="温度")
    humidity: float = Field(..., description="湿度")
    smoke_level: float = Field(..., description="烟雾浓度")

class EnvironmentAnalysisResponse(BaseModel):
    """环境分析响应"""
    avgTemperature: float = Field(..., description="平均温度")
    avgHumidity: float = Field(..., description="平均湿度")
    maxSmokeLevel: float = Field(..., description="最大烟雾浓度")
    status: str = Field(..., description="状态")
    analysis: str = Field(..., description="分析内容")

class ReportGenerationRequest(BaseModel):
    """报告生成请求"""
    type: str = Field(..., description="报告类型")
    data_points: int = Field(..., description="数据点数量")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")

class ReportGenerationResponse(BaseModel):
    """报告生成响应"""
    type: str = Field(..., description="报告类型")
    startTime: str = Field(..., description="开始时间")
    endTime: str = Field(..., description="结束时间")
    dataPoints: int = Field(..., description="数据点数量")
    summary: str = Field(..., description="报告内容")

class NaturalLanguageQueryRequest(BaseModel):
    """自然语言查询请求"""
    query: str = Field(..., description="查询语句")

class NaturalLanguageQueryResponse(BaseModel):
    """自然语言查询响应"""
    query: str = Field(..., description="查询语句")
    answer: str = Field(..., description="AI 回答")
    confidence: float = Field(..., description="置信度")

class EnvironmentPredictionRequest(BaseModel):
    """环境预测请求"""
    current_temp: float = Field(..., description="当前温度")
    current_humidity: float = Field(..., description="当前湿度")
    hours: int = Field(..., description="预测小时数")

class EnvironmentPredictionResponse(BaseModel):
    """环境预测响应"""
    predictions: List[Dict] = Field(..., description="预测数据")
    ai_analysis: str = Field(..., description="AI 分析")

class InspectionPlanRequest(BaseModel):
    """巡检计划生成请求"""
    location: str = Field(..., description="巡检地点")
    time_range: str = Field(..., description="时间范围")
    requirements: str = Field(..., description="巡检要求")

class InspectionPlanResponse(BaseModel):
    """巡检计划响应"""
    location: str = Field(..., description="巡检地点")
    timeRange: str = Field(..., description="时间范围")
    requirements: str = Field(..., description="巡检要求")
    plan: str = Field(..., description="巡检计划")
    status: str = Field(..., description="状态")

class EquipmentHealthRequest(BaseModel):
    """设备健康分析请求"""
    equipment_name: str = Field(..., description="设备名称")
    operation_hours: int = Field(..., description="运行时间")
    error_count: int = Field(..., description="错误次数")
    performance_data: Dict = Field(..., description="性能数据")

class EquipmentHealthResponse(BaseModel):
    """设备健康分析响应"""
    equipmentName: str = Field(..., description="设备名称")
    operationHours: int = Field(..., description="运行时间")
    errorCount: int = Field(..., description="错误次数")
    healthStatus: str = Field(..., description="健康状态")
    analysis: str = Field(..., description="分析内容")