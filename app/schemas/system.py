from pydantic import BaseModel, Field
from typing import Optional, List

class SystemStatusResponse(BaseModel):
    status: str = Field(..., description="系统状态：normal/warning/danger")
    uptime: float = Field(..., description="运行时长(秒)")
    version: str = Field(..., description="系统版本")
    cpuUsage: Optional[float] = Field(None, description="CPU使用率(%)")
    memoryUsage: Optional[float] = Field(None, description="内存使用率(%)")

class SystemLogRequest(BaseModel):
    level: Optional[str] = Field(None, description="日志级别：info/warn/error")
    startTime: Optional[str] = Field(None, description="开始时间")
    endTime: Optional[str] = Field(None, description="结束时间")
    page: Optional[int] = Field(1, description="页码")
    size: Optional[int] = Field(20, description="每页数量")

class SystemLogResponse(BaseModel):
    id: int = Field(..., description="日志ID")
    level: str = Field(..., description="日志级别")
    module: Optional[str] = Field(None, description="模块名")
    content: Optional[str] = Field(None, description="日志内容")
    time: str = Field(..., description="创建时间")

class SystemLogListResponse(BaseModel):
    list: List['SystemLogResponse'] = Field(..., description="日志列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")

SystemLogListResponse.model_rebuild()

class SystemConfigUpdate(BaseModel):
    updateInterval: Optional[int] = Field(None, description="数据更新间隔(毫秒)")
    alertThreshold: Optional[dict] = Field(None, description="告警阈值配置")