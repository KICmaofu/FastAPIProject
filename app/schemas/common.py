# 统一响应格式Schema
from pydantic import BaseModel, Field
from typing import Optional, Any, Generic, TypeVar, List

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    code: int = Field(200, description="状态码")
    msg: str = Field("success", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
                "data": None
            }
        }


class PagedData(BaseModel, Generic[T]):
    """分页数据格式"""
    list: List[T] = Field(default_factory=list, description="数据列表")
    total: int = Field(0, description="总数量")
    page: int = Field(1, description="当前页")
    pageSize: int = Field(10, description="每页数量")


class PagedResponse(BaseModel, Generic[T]):
    """分页响应格式"""
    code: int = Field(200)
    msg: str = Field("success")
    data: PagedData[T]


class PasswordVerifyRequest(BaseModel):
    """密码验证请求模型"""
    password: str = Field(..., min_length=1, description="用户密码")


class IdRequest(BaseModel):
    """通用ID请求"""
    id: int = Field(..., description="ID")


class StatusRequest(BaseModel):
    """状态更新请求"""
    id: int = Field(..., description="ID")
    status: int = Field(..., description="状态值")