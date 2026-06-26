from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from app.routers import routers
from app.config.settings import settings
from app.config.database import engine, Base
from app.utils.rate_limiter import rate_limiter
from app.middleware.request_logger import RequestLoggerMiddleware
import threading
import time
import socket
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("inspection_system")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智能巡检系统后端API"
)

# 请求限流中间件
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    
    # 健康检查接口不限流
    if request.url.path == "/" or request.url.path.startswith("/docs") or request.url.path.startswith("/openapi.json"):
        return await call_next(request)
    
    if not rate_limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "code": 429,
                "message": "请求过于频繁，请稍后再试",
                "data": None
            }
        )
    
    response = await call_next(request)
    response.headers["X-RateLimit-Remaining"] = str(rate_limiter.get_remaining(client_ip))
    return response

# 请求日志中间件
app.add_middleware(RequestLoggerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "message": "服务器内部错误",
            "data": None
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "message": str(exc),
            "data": None
        }
    )

# 挂载静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

for router in routers:
    app.include_router(router)

@app.get("/")
async def root():
    return {"message": "智能巡检系统 API", "version": settings.APP_VERSION}

socket_server_thread = None
socket_server_sock = None

def start_socket_server():
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from socket_server.socket_server import start_server
    global socket_server_sock
    socket_server_sock = start_server(background=True)

@app.on_event("startup")
async def startup_event():
    global socket_server_thread
    print("================================================")
    print("Starting Socket Server in background thread...")
    socket_server_thread = threading.Thread(target=start_socket_server, daemon=True)
    socket_server_thread.start()
    time.sleep(1)
    print("Socket Server started successfully")
    print("================================================")

@app.on_event("shutdown")
async def shutdown_event():
    global socket_server_sock
    if socket_server_sock:
        print("================================================")
        print("Shutting down Socket Server...")
        try:
            socket_server_sock.close()
            print("Socket Server shutdown successfully")
        except Exception as e:
            print(f"Error shutting down Socket Server: {e}")
        print("================================================")

if __name__ == "__main__":
    import uvicorn
    print("================================================")
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    print("================================================")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )