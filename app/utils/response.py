from fastapi import status
from fastapi.responses import JSONResponse
from typing import Optional, Any

class ApiResponse:
    @staticmethod
    def success(data: Any = None, msg: str = "success"):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 200,
                "msg": msg,
                "data": data
            }
        )
    
    @staticmethod
    def success_pagination(list_data: list, total: int, page: int, page_size: int, msg: str = "success"):
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "code": 200,
                "msg": msg,
                "data": {
                    "list": list_data,
                    "total": total,
                    "page": page,
                    "pageSize": page_size
                }
            }
        )
    
    @staticmethod
    def error(code: int = 400, msg: str = "请求参数错误"):
        return JSONResponse(
            status_code=code,
            content={
                "code": code,
                "msg": msg,
                "data": None
            }
        )
    
    @staticmethod
    def unauthorized(msg: str = "未登录或token过期"):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "code": 401,
                "msg": msg,
                "data": None
            }
        )
    
    @staticmethod
    def forbidden(msg: str = "无权限访问"):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "code": 403,
                "msg": msg,
                "data": None
            }
        )
    
    @staticmethod
    def not_found(msg: str = "资源不存在"):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "code": 404,
                "msg": msg,
                "data": None
            }
        )
    
    @staticmethod
    def server_error(msg: str = "服务器内部错误"):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "code": 500,
                "msg": msg,
                "data": None
            }
        )