# AI模块Schema
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AlarmAnalyzeRequest(BaseModel):
    """AI分析告警请求"""
    alarm_id: int = Field(..., description="告警ID")


class AlarmAnalyzeResponse(BaseModel):
    """AI分析告警响应"""
    analysis: str = Field(..., description="分析结果")


class AiChatRequest(BaseModel):
    """AI对话请求"""
    message: str = Field(..., description="用户消息")
    relate_alarm_id: Optional[int] = Field(None, description="关联告警ID")
    relate_robot_sn: Optional[str] = Field(None, description="关联机器人序列号")


class AiChatResponse(BaseModel):
    """AI对话响应"""
    answer: str = Field(..., description="AI回复")


class AiChatRecord(BaseModel):
    """AI对话记录"""
    id: int = Field(..., description="记录ID")
    user_query: str = Field(..., description="用户提问")
    ai_answer: Optional[str] = Field(None, description="AI回答")
    chat_type: int = Field(1, description="对话类型")
    relate_alarm_id: Optional[int] = Field(None, description="关联告警ID")
    relate_robot_sn: Optional[str] = Field(None, description="关联机器人序列号")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class ReportAnalyzeRequest(BaseModel):
    """AI分析报表请求"""
    robot_sn: Optional[str] = Field(None, description="机器人序列号")
    startTime: Optional[str] = Field(None, description="开始时间")
    endTime: Optional[str] = Field(None, description="结束时间")