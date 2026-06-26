# 路由导出
from app.routers.user_router import router as user_router
from app.routers.robot_router import router as robot_router
from app.routers.patrol_router import router as patrol_router
from app.routers.alarm_router import router as alarm_router
from app.routers.report_router import router as report_router
from app.routers.ai_router import router as ai_router
from app.routers.system_router import router as system_router

routers = [
    user_router,
    robot_router,
    patrol_router,
    alarm_router,
    report_router,
    ai_router,
    system_router
]