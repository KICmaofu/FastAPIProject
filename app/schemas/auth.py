from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class LoginRequest(BaseModel):
    username: Optional[str] = Field(None, description="用户名")
    phone: Optional[str] = Field(None, description="手机号")
    password: str = Field(..., description="密码")
    captcha: Optional[str] = Field(None, description="验证码")

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
    username: str = Field(..., description="用户名")
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")
    confirmPassword: str = Field(..., description="确认密码")

class ResetPasswordRequest(BaseModel):
    phone: str = Field(..., description="手机号")
    newPassword: str = Field(..., description="新密码")
    captcha: str = Field(..., description="验证码")