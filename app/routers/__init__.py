from app.routers.auth_router import router as auth_router
from app.routers.robot_router import router as robot_router
from app.routers.thermal_router import router as thermal_router
from app.routers.environment_router import router as environment_router
from app.routers.alert_router import router as alert_router
from app.routers.device_router import router as device_router
from app.routers.sensor_router import router as sensor_router
from app.routers.message_router import router as message_router
from app.routers.user_router import router as user_router
from app.routers.system_router import router as system_router
from app.routers.report_router import router as report_router

routers = [
    auth_router,
    robot_router,
    thermal_router,
    environment_router,
    alert_router,
    device_router,
    sensor_router,
    message_router,
    user_router,
    system_router,
    report_router
]