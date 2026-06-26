# 报表模块Schema
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class EnvTrendData(BaseModel):
    """环境趋势数据"""
    time: Optional[str] = Field(None, description="采集时间")
    temperature: Optional[float] = Field(None, description="温度")
    humidity: Optional[float] = Field(None, description="湿度")
    smoke_level: Optional[float] = Field(None, description="烟雾浓度")
    max_single_temp: Optional[float] = Field(None, description="最高单点温度")


class AlarmTrendData(BaseModel):
    """告警趋势数据"""
    labels: List[str] = Field(default_factory=list, description="时间标签")
    level1: List[int] = Field(default_factory=list, description="RED数量")
    level2: List[int] = Field(default_factory=list, description="ORANGE数量")
    level3: List[int] = Field(default_factory=list, description="NORMAL数量")


class DailyReport(BaseModel):
    """日报数据"""
    date: str = Field(..., description="日期")
    total_patrol: int = Field(0, description="巡检总数")
    completed_patrol: int = Field(0, description="完成巡检数")
    total_alarm: int = Field(0, description="告警总数")
    processed_alarm: int = Field(0, description="已处理告警数")
    avg_temperature: Optional[float] = Field(None, description="平均温度")
    avg_humidity: Optional[float] = Field(None, description="平均湿度")
    max_temperature: Optional[float] = Field(None, description="最高温度")


class SensorStatistics(BaseModel):
    """传感器统计"""
    avg_temperature: Optional[float] = Field(None, description="平均温度")
    avg_humidity: Optional[float] = Field(None, description="平均湿度")
    avg_smoke_level: Optional[float] = Field(None, description="平均烟雾浓度")
    max_temperature: Optional[float] = Field(None, description="最高温度")
    min_temperature: Optional[float] = Field(None, description="最低温度")
    data_count: int = Field(0, description="数据条数")