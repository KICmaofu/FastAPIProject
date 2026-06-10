from pydantic import BaseModel, Field
from typing import Optional, List

class DeviceCreate(BaseModel):
    name: str = Field(..., description="设备名称")
    type: str = Field(..., description="设备类型")
    model: Optional[str] = Field(None, description="型号")
    location: Optional[str] = Field(None, description="位置描述")

class DeviceUpdate(BaseModel):
    name: Optional[str] = Field(None, description="设备名称")
    type: Optional[str] = Field(None, description="设备类型")
    model: Optional[str] = Field(None, description="型号")
    location: Optional[str] = Field(None, description="位置描述")

class DeviceResponse(BaseModel):
    id: str = Field(..., description="设备ID")
    name: str = Field(..., description="设备名称")
    type: str = Field(..., description="设备类型")
    model: Optional[str] = Field(None, description="型号")
    status: str = Field(..., description="状态")
    location: Optional[str] = Field(None, description="位置描述")

class DeviceStatsResponse(BaseModel):
    total: int = Field(..., description="设备总数")
    online: int = Field(..., description="在线数量")
    offline: int = Field(..., description="离线数量")
    warning: int = Field(..., description="告警数量")

class DeviceListResponse(BaseModel):
    list: List['DeviceResponse'] = Field(..., description="设备列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")

DeviceListResponse.model_rebuild()