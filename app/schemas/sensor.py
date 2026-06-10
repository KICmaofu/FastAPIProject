from pydantic import BaseModel, Field
from typing import Optional, List

class SensorResponse(BaseModel):
    id: str = Field(..., description="传感器ID")
    name: str = Field(..., description="传感器名称")
    type: str = Field(..., description="类型：temperature/humidity/gas")
    value: Optional[float] = Field(None, description="当前值")
    unit: str = Field(..., description="单位")
    status: str = Field(..., description="状态：normal/warning/danger")

class SensorListResponse(BaseModel):
    list: List['SensorResponse'] = Field(..., description="传感器列表")

SensorListResponse.model_rebuild()