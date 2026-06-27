from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config.settings import settings
from app.config.database import engine, Base
from app.routers.user_router import router as user_router
from app.routers.robot_router import router as robot_router
from app.routers.patrol_router import router as patrol_router
from app.routers.alarm_router import router as alarm_router
from app.routers.report_router import router as report_router
from app.routers.ai_router import router as ai_router
from app.routers.sys_log_router import router as sys_log_router
from app.routers.socket_router import router as socket_router
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("server.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("inspection_system")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智能巡检系统后端API"
)

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

app.include_router(user_router)
app.include_router(robot_router)
app.include_router(patrol_router)
app.include_router(alarm_router)
app.include_router(report_router)
app.include_router(ai_router)
app.include_router(sys_log_router)
app.include_router(socket_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Socket Server...")
    from socket_server.socket_server import start_server, PORT
    start_server(background=True)
    logger.info(f"Socket Server started on port {PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Socket Server...")
    from socket_server.socket_server import shutdown_server
    shutdown_server()
    logger.info("Socket Server shutdown complete")

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