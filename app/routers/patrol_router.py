from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import get_current_user
from app.schemas.patrol import (
    PatrolTaskAdd, PatrolTaskUpdate, PatrolTaskUpdateStatus, PatrolTaskDelete,
    PatrolStart, PatrolEnd
)
from app.services.patrol_service import PatrolService

router = APIRouter(prefix="/api/patrol", tags=["巡检任务模块"])

@router.get("/task/list")
async def get_task_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    robot_sn: str = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return PatrolService.get_task_list(db, page, pageSize, robot_sn)

@router.get("/task/statistics")
async def get_task_statistics(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return PatrolService.get_task_statistics(db)

@router.post("/task/add")
async def add_task(data: PatrolTaskAdd, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return PatrolService.add_task(db, data.task_name, data.robot_sn, data.cycle_type, data.start_time, data.end_time, data.route_points, user.username)

@router.put("/task/update")
async def update_task(data: PatrolTaskUpdate, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return PatrolService.update_task(db, data.id, data.task_name, data.cycle_type, data.start_time, data.end_time, data.route_points, data.status)

@router.post("/task/status")
async def update_task_status(data: PatrolTaskUpdateStatus, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return PatrolService.update_task_status(db, data.id, data.status)

@router.post("/task/delete")
async def delete_task(data: PatrolTaskDelete, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return PatrolService.delete_task(db, data.id)

@router.get("/record/list")
async def get_record_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    robot_sn: str = Query(None),
    startTime: str = Query(None),
    endTime: str = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return PatrolService.get_record_list(db, page, pageSize, robot_sn, startTime, endTime)

@router.get("/record/statistics")
async def get_record_statistics(
    startTime: str = Query(None),
    endTime: str = Query(None),
    db: Session = Depends(get_db),
    user = Depends(get_current_user)
):
    return PatrolService.get_record_statistics(db, startTime, endTime)

@router.get("/record/{id}")
async def get_record_detail(id: int = Path(..., gt=0), db: Session = Depends(get_db), user = Depends(get_current_user)):
    return PatrolService.get_record_detail(db, id)

@router.post("/start")
async def start_patrol(data: PatrolStart, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return PatrolService.start_patrol(db, data.robot_sn, data.task_id, user.username)

@router.post("/end")
async def end_patrol(data: PatrolEnd, db: Session = Depends(get_db), user = Depends(get_current_user)):
    return PatrolService.end_patrol(db, data.id, data.patrol_result)