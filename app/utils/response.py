from typing import Any, Optional
from datetime import datetime
from app.schemas.common import ApiResponse

def success_response(data: Any = None, message: str = "success") -> ApiResponse:
    return ApiResponse(
        code=200,
        message=message,
        data=data,
        timestamp=int(datetime.now().timestamp() * 1000)
    )

def error_response(code: int, message: str) -> ApiResponse:
    return ApiResponse(
        code=code,
        message=message,
        data=None,
        timestamp=int(datetime.now().timestamp() * 1000)
    )

def unauthorized_response(message: str = "未登录或Token失效") -> ApiResponse:
    return error_response(401, message)

def forbidden_response(message: str = "无权限访问") -> ApiResponse:
    return error_response(403, message)

def not_found_response(message: str = "资源不存在") -> ApiResponse:
    return error_response(404, message)

def bad_request_response(message: str = "请求参数错误") -> ApiResponse:
    return error_response(400, message)