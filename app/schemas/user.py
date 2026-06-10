from pydantic import BaseModel, Field
from typing import Optional, List

class UserResponse(BaseModel):
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    role: str = Field(..., description="角色")
    status: bool = Field(..., description="状态")

class UserCreate(BaseModel):
    username: str = Field(..., description="用户名")
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")
    role: str = Field(..., description="角色")

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    role: Optional[str] = Field(None, description="角色(仅管理员)")

class UserListRequest(BaseModel):
    page: Optional[int] = Field(1, description="页码")
    size: Optional[int] = Field(20, description="每页数量")
    role: Optional[str] = Field(None, description="角色筛选")

class UserListResponse(BaseModel):
    list: List['UserResponse'] = Field(..., description="用户列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")

UserListResponse.model_rebuild()