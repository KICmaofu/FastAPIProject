from pydantic import BaseModel, Field
from typing import Optional, List

class RobotCreate(BaseModel):
    name: str = Field(..., description="机器人名称")
    model: str = Field(..., description="型号")
    location: Optional[str] = Field(None, description="部署位置")

class RobotUpdate(BaseModel):
    name: Optional[str] = Field(None, description="机器人名称")
    model: Optional[str] = Field(None, description="型号")
    location: Optional[str] = Field(None, description="部署位置")

class RobotResponse(BaseModel):
    id: str = Field(..., description="机器人ID")
    name: str = Field(..., description="机器人名称")
    model: str = Field(..., description="型号")
    battery: float = Field(..., description="电量(%)")
    status: str = Field(..., description="状态")
    location: Optional[str] = Field(None, description="部署位置")
    speed: Optional[float] = Field(None, description="速度(m/s)")

class RobotPositionResponse(BaseModel):
    id: str = Field(..., description="机器人ID")
    x: float = Field(..., description="X坐标")
    y: float = Field(..., description="Y坐标")
    battery: Optional[float] = Field(None, description="电量(%)")
    status: str = Field(..., description="状态：moving/idle/offline")
    speed: Optional[float] = Field(None, description="速度(m/s)")

class RobotControlRequest(BaseModel):
    action: str = Field(..., description="动作：move/stop/turn_left/turn_right")
    speed: Optional[float] = Field(1, description="速度(0-10)")
    duration: Optional[float] = Field(None, description="持续时间(秒)")

class PasswordVerifyRequest(BaseModel):
    password: str = Field(..., description="密码验证")

class RobotListResponse(BaseModel):
    list: List['RobotResponse'] = Field(..., description="机器人列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")

RobotListResponse.model_rebuild()