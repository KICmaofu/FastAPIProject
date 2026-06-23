from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
import re

class LoginRequest(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., description="密码")
    captcha: Optional[str] = Field(None, description="验证码")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if v and not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v

class UserInfoResponse(BaseModel):
    id: str = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    role: str = Field(..., description="用户角色")
    permissions: List[str] = Field(..., description="权限列表")

class LoginResponse(BaseModel):
    token: str = Field(..., description="JWT token")
    user: UserInfoResponse = Field(..., description="用户信息")

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    phone: str = Field(..., description="手机号")
    password: str = Field(..., min_length=6, max_length=32, description="密码")
    confirmPassword: str = Field(..., description="确认密码")
    role: Optional[str] = Field("viewer", description="角色 (viewer/operator/admin)，注册为管理员需要提供管理员密钥")
    adminKey: Optional[str] = Field(None, description="管理员密钥（注册管理员账户时必填）")
    
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

class ResetPasswordRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    newPassword: str = Field(..., min_length=6, max_length=32, description="新密码")
    captcha: str = Field(..., description="验证码")
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^1[3-9]\d{9}$', v):
            raise ValueError('手机号格式不正确')
        return v
    
    @field_validator('newPassword')
    @classmethod
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{6,32}$', v):
            raise ValueError('密码必须包含大小写字母和数字')
        return v