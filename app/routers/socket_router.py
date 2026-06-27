from fastapi import APIRouter, Depends
from app.utils.response import ApiResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/socket", tags=["Socket服务"])

@router.get("/status", summary="获取Socket服务器状态", dependencies=[Depends(get_current_user)])
async def get_socket_status():
    from socket_server.socket_server import get_server_status
    status = get_server_status()
    return ApiResponse.success(status)

@router.post("/start", summary="启动Socket服务器", dependencies=[Depends(get_current_user)])
async def start_socket_server():
    from socket_server.socket_server import start_server, server_running
    
    if server_running:
        return ApiResponse.success({"message": "Socket服务器已在运行中"})
    
    result = start_server(background=True)
    
    if result:
        return ApiResponse.success({"message": "Socket服务器启动成功"})
    else:
        return ApiResponse.error("Socket服务器启动失败")

@router.post("/stop", summary="停止Socket服务器", dependencies=[Depends(get_current_user)])
async def stop_socket_server():
    from socket_server.socket_server import shutdown_server, server_running
    
    if not server_running:
        return ApiResponse.success({"message": "Socket服务器已停止"})
    
    shutdown_server()
    return ApiResponse.success({"message": "Socket服务器已停止"})