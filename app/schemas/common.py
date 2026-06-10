from pydantic import BaseModel, Field
from typing import Optional, Any

class ApiResponse(BaseModel):
    code: int = Field(200, description="状态码")
    message: str = Field("success", description="响应消息")
    data: Any = Field(None, description="响应数据")
    timestamp: int = Field(..., description="时间戳")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": {},
                "timestamp": 1699999999999
            }
        }