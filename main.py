from fastapi import FastAPI, Request, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from app.routers import routers
from app.config.settings import settings
from app.config.database import engine, Base
from app.middleware.request_logger import RequestLoggerMiddleware
import logging
import threading
import time

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

socket_server_thread = None
socket_server_sock = None

def start_socket_server():
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    from socket_server.socket_server import start_server
    global socket_server_sock
    socket_server_sock = start_server(background=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("================================================")
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    try:
        socket_server_thread = threading.Thread(target=start_socket_server, daemon=True)
        socket_server_thread.start()
        time.sleep(1)
        logger.info("Socket Server started successfully")
    except Exception as e:
        logger.warning(f"Socket Server not started: {e}")
    
    logger.info("================================================")
    
    yield
    
    logger.info("================================================")
    logger.info("Shutting down application...")
    if socket_server_sock:
        try:
            socket_server_sock.close()
            logger.info("Socket Server shutdown successfully")
        except Exception as e:
            logger.error(f"Error shutting down Socket Server: {e}")
    logger.info("================================================")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智能巡检系统后端API - 智能机器人巡检管理系统",
    lifespan=lifespan
)

app.add_middleware(RequestLoggerMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": 500,
            "msg": "服务器内部错误",
            "data": None
        }
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": 400,
            "msg": str(exc),
            "data": None
        }
    )

for router in routers:
    app.include_router(router)

@app.get("/health", summary="健康检查")
async def health_check():
    return {"code": 200, "msg": "fire-patrol-server is running", "data": None}

@app.get("/", summary="系统信息")
async def root():
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "api_docs": "/docs"
        }
    }

@app.get("/socket/status", summary="Socket服务器状态")
async def socket_status():
    import socket_server.socket_server as ss
    return {
        "code": 200,
        "msg": "success",
        "data": {
            "active_connections": ss.connection_pool['active_connections'],
            "max_connections": ss.connection_pool['max_connections'],
            "total_connections": ss.connection_pool['connection_stats']['total_connections'],
            "peak_connections": ss.connection_pool['connection_stats']['peak_connections'],
            "total_requests": ss.performance_metrics['total_requests'],
            "successful_requests": ss.performance_metrics['successful_requests'],
            "failed_requests": ss.performance_metrics['failed_requests'],
            "total_alarms_created": ss.performance_metrics['total_alarms_created'],
            "avg_response_time": f"{ss.performance_metrics['avg_response_time']:.2f} ms"
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("================================================")
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("================================================")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )