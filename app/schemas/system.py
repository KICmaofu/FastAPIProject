# 系统日志模块Schema
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LogInfo(BaseModel):
    """系统日志信息"""
    id: int = Field(..., description="日志ID")
    username: Optional[str] = Field(None, description="操作用户")
    module: Optional[str] = Field(None, description="操作模块")
    operation: Optional[str] = Field(None, description="操作类型")
    ip_address: Optional[str] = Field(None, description="IP地址")
    detail: Optional[str] = Field(None, description="操作详情")
    create_time: Optional[datetime] = Field(None, description="创建时间")