from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import re

class UserResponse(BaseModel):
    model_config = {"from_attributes": True}
    
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    role: str = Field(..., description="角色")
    status: bool = Field(..., description="状态")

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    role: str = Field(..., description="角色")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,32}$', v):
            raise ValueError('密码必须包含大小写字母和数字')
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    role: Optional[str] = Field(None, description="角色(仅管理员)")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v

class UserListRequest(BaseModel):
    page: Optional[int] = Field(1, description="页码")
    size: Optional[int] = Field(20, description="每页数量")
    role: Optional[str] = Field(None, description="角色筛选")

class UserListResponse(BaseModel):
    list: List['UserResponse'] = Field(..., description="用户列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")

UserListResponse.model_rebuild()