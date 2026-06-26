from pydantic import BaseModel, Field, field_validator
from typing import Optional

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    real_name: str = Field(..., min_length=1, max_length=30)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)

class UserAdd(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    real_name: str = Field(..., min_length=1, max_length=30)
    role: int = Field(..., ge=1, le=2)

class UserUpdate(BaseModel):
    id: int = Field(..., gt=0)
    real_name: Optional[str] = Field(None, max_length=30)
    phone: Optional[str] = None
    role: Optional[int] = Field(None, ge=1, le=2)

class UserDelete(BaseModel):
    id: int = Field(..., gt=0)

class UserUpdateStatus(BaseModel):
    id: int = Field(..., gt=0)
    status: int = Field(..., ge=0, le=1)

class UserResetPwd(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    phone: str = Field(...)
    newPassword: str = Field(..., min_length=6, max_length=100)

class UserInfoResponse(BaseModel):
    id: int
    username: str
    real_name: str
    phone: Optional[str]
    role: int
    status: int

class UserListResponse(UserInfoResponse):
    create_time: str