# 告警模块Schema
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class AlarmInfo(BaseModel):
    """告警信息"""
    id: int = Field(..., description="告警ID")
    robot_sn: str = Field(..., description="机器人序列号")
    sensor_record_id: Optional[int] = Field(None, description="关联传感器记录ID")
    hardware_alarm_type: int = Field(0, description="板端告警类型")
    alarm_type: Optional[str] = Field(None, description="告警类型")
    alarm_level: Optional[str] = Field(None, description="告警等级：RED/ORANGE/NORMAL")
    alarm_desc: Optional[str] = Field(None, description="告警描述")
    area_name: Optional[str] = Field(None, description="区域名称")
    point_name: Optional[str] = Field(None, description="点位名称")
    deal_status: int = Field(0, description="处置状态：0-未处理 1-已处理")
    deal_user: Optional[str] = Field(None, description="处置人")
    deal_content: Optional[str] = Field(None, description="处置内容")
    deal_time: Optional[datetime] = Field(None, description="处置时间")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class AlarmDetail(BaseModel):
    """告警详情（含传感器数据）"""
    id: int = Field(..., description="告警ID")
    robot_sn: str = Field(..., description="机器人序列号")
    alarm_level: Optional[str] = Field(None, description="告警等级")
    alarm_desc: Optional[str] = Field(None, description="告警描述")
    sensor_data: Optional[Dict[str, Any]] = Field(None, description="传感器数据")


class AlarmStatistics(BaseModel):
    """告警统计"""
    total: int = Field(0, description="总数")
    red: int = Field(0, description="红色告警数")
    orange: int = Field(0, description="橙色告警数")
    normal: int = Field(0, description="普通告警数")
    pending: int = Field(0, description="待处理数")
    dealt: int = Field(0, description="已处理数")


class AlarmTrend(BaseModel):
    """告警趋势"""
    labels: list = Field(default_factory=list, description="时间标签")
    level1: list = Field(default_factory=list, description="RED级别数量")
    level2: list = Field(default_factory=list, description="ORANGE级别数量")
    level3: list = Field(default_factory=list, description="NORMAL级别数量")


class DealAlarmRequest(BaseModel):
    """处置告警请求"""
    id: int = Field(..., description="告警ID")
    deal_content: str = Field(..., description="处置内容")


class AlarmDeleteRequest(BaseModel):
    """删除告警请求"""
    id: int = Field(..., description="告警ID")