import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import json

logger = logging.getLogger("inspection_system.request")

class RequestLoggerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        client_ip = request.client.host
        
        # 记录请求信息
        logger.info(
            f"Request: {request.method} {request.url.path} | IP: {client_ip} | Headers: {dict(request.headers)}"
        )
        
        try:
            response: Response = await call_next(request)
            process_time = time.time() - start_time
            
            # 记录响应信息
            logger.info(
                f"Response: {request.method} {request.url.path} | Status: {response.status_code} | Time: {process_time:.2f}s"
            )
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error: {request.method} {request.url.path} | IP: {client_ip} | Time: {process_time:.2f}s | Error: {str(e)}",
                exc_info=True
            )
            raise