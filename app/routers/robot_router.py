from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import get_current_user
from app.schemas.robot import RobotAdd, RobotUpdate, RobotDelete, RobotSendCmd
from app.services.robot_service import RobotService

router = APIRouter(prefix="/api/robot", tags=["机器人模块"])

@router.get("/list")
async def get_robot_list(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.get_robot_list(db)

@router.get("/sn/{robot_sn}")
async def get_robot_by_sn(robot_sn: str = Path(...), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.get_robot_by_sn(db, robot_sn)

@router.get("/statistics")
async def get_robot_statistics(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.get_robot_statistics(db)

@router.post("/add")
async def add_robot(data: RobotAdd, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.add_robot(db, data.robot_sn, data.robot_name, data.area_name, data.remark, user.username)

@router.put("/update")
async def update_robot(data: RobotUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.update_robot(db, data.id, data.robot_name, data.area_name, data.remark)

@router.post("/delete")
async def delete_robot(data: RobotDelete, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.delete_robot(db, data.id)

@router.post("/sendCmd")
async def send_cmd(data: RobotSendCmd, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.send_cmd(db, data.robot_sn, data.cmd_code, data.param, user.username)

@router.get("/cmd/list")
async def get_cmd_list(
    robot_sn: str = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    cmd_status: int = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return RobotService.get_cmd_list(db, robot_sn, page, pageSize, cmd_status)

@router.get("/sensor/history")
async def get_sensor_history(
    robot_sn: str = Query(None),
    page: int = Query(1, ge=1),
    pageSize: int = Query(20, ge=1, le=100),
    startTime: str = Query(None),
    endTime: str = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return RobotService.get_sensor_history(db, robot_sn, page, pageSize, startTime, endTime)

@router.get("/sensor/latest/{robot_sn}")
async def get_latest_sensor(robot_sn: str = Path(...), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.get_latest_sensor(db, robot_sn)

@router.get("/sensor/statistics")
async def get_sensor_statistics(
    robot_sn: str = Query(None),
    startTime: str = Query(None),
    endTime: str = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return RobotService.get_sensor_statistics(db, robot_sn, startTime, endTime)

@router.get("/{id}")
async def get_robot_detail(id: int = Path(..., gt=0), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return RobotService.get_robot_detail(db, id)