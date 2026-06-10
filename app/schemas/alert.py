from pydantic import BaseModel, Field
from typing import Optional, List

class AlertResponse(BaseModel):
    id: str = Field(..., description="告警ID")
    type: str = Field(..., description="告警类型")
    level: str = Field(..., description="告警级别")
    message: str = Field(..., description="告警消息")
    device: Optional[str] = Field(None, description="设备ID")
    time: str = Field(..., description="告警时间")
    status: str = Field(..., description="处理状态")

class AlertProcessRequest(BaseModel):
    action: str = Field(..., description="处理动作：confirm/ignore")
    remark: Optional[str] = Field(None, description="处理备注")

class AlertListRequest(BaseModel):
    level: Optional[str] = Field(None, description="告警级别：warning/danger")
    status: Optional[str] = Field(None, description="状态：pending/processed")
    page: Optional[int] = Field(1, description="页码")
    size: Optional[int] = Field(20, description="每页数量")

class AlertListResponse(BaseModel):
    list: List['AlertResponse'] = Field(..., description="告警列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")

AlertListResponse.model_rebuild()