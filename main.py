from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import routers
from app.config.settings import settings
from app.config.database import engine, Base
import threading
import time
import socket

Base.metadata.create_all(bind=engine)

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