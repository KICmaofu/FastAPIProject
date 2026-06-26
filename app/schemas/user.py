# 用户模块Schema
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(..., min_length=2, max_length=50, description="用户名")
    password: str = Field(..., min_length=6, max_length=100, description="密码")
    real_name: str = Field(..., min_length=1, max_length=50, description="真实姓名")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    real_name: str = Field(..., description="真实姓名")
    phone: Optional[str] = Field(None, description="手机号")
    role: int = Field(..., description="角色：1-超级管理员 2-运维员")
    status: int = Field(..., description="状态：0-待审核/禁用 1-正常启用")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class LoginResponse(BaseModel):
    """登录响应"""
    token: str = Field(..., description="JWT Token")
    user: UserInfoResponse = Field(..., description="用户信息")


class UserAddRequest(BaseModel):
    """添加用户请求（管理员）"""
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    real_name: str = Field(..., min_length=1, max_length=50)
    role: int = Field(..., ge=1, le=2, description="角色：1-管理员 2-运维员")


class UserUpdateRequest(BaseModel):
    """更新用户请求（管理员）"""
    id: int = Field(..., description="用户ID")
    real_name: Optional[str] = Field(None, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[int] = Field(None, ge=1, le=2)


class ResetPwdRequest(BaseModel):
    """重置密码请求"""
    username: str = Field(..., description="用户名")
    phone: str = Field(..., description="手机号")
    newPassword: str = Field(..., min_length=6, description="新密码")


class UserDeleteRequest(BaseModel):
    """删除用户请求"""
    id: int = Field(..., description="用户ID")