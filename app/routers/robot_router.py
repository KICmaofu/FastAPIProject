from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user, require_operator, require_admin
from app.dependencies.password_verify import verify_user_password, get_client_ip
from app.models.user import User
from app.services import robot_service
from app.services.log_service import log_robot_operation
from app.schemas.robot import RobotCreate, RobotUpdate, RobotResponse, RobotControlRequest, PasswordVerifyRequest
from app.utils.response import success_response

router = APIRouter(prefix="/api/robot", tags=["机器人模块"])

@router.get("/positions", summary="获取机器人位置")
async def get_robot_positions(
    robotId: Optional[str] = Query(None, description="机器人ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    positions = robot_service.get_positions(db, robotId)
    return success_response(data=positions)

@router.get("", summary="获取机器人列表")
async def get_robot_list(
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = robot_service.get_robot_list(db, page, size, status)
    return success_response(data=result)

@router.post("", summary="添加机器人")
async def create_robot(
    request: Request,
    robot_data: RobotCreate,
    password_verify: PasswordVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    verify_user_password(db, current_user, password_verify.password, "添加机器人", request)
    
    robot = robot_service.create_robot(db, robot_data)
    
    log_robot_operation(
        db=db,
        operation="添加",
        robot_id=robot.id,
        user_id=current_user.id,
        username=current_user.username,
        success=True,
        details=f"机器人名称:{robot.name}",
        ip_address=get_client_ip(request)
    )
    
    return success_response(data=RobotResponse.model_validate(robot), message="添加成功")

@router.put("/{robotId}", summary="更新机器人信息")
async def update_robot(
    robotId: str,
    request: Request,
    robot_data: RobotUpdate,
    password_verify: PasswordVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    existing_robot = robot_service.get_robot_by_id(db, robotId)
    if not existing_robot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="机器人不存在")
    
    verify_user_password(db, current_user, password_verify.password, "修改机器人信息", request)
    
    robot = robot_service.update_robot(db, robotId, robot_data)
    
    log_robot_operation(
        db=db,
        operation="修改",
        robot_id=robotId,
        user_id=current_user.id,
        username=current_user.username,
        success=True,
        details=f"机器人名称:{robot.name if robot else existing_robot.name}",
        ip_address=get_client_ip(request)
    )
    
    return success_response(data=RobotResponse.model_validate(robot), message="更新成功")

@router.delete("/{robotId}", summary="删除机器人")
async def delete_robot(
    robotId: str,
    request: Request,
    password_verify: PasswordVerifyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    existing_robot = robot_service.get_robot_by_id(db, robotId)
    if not existing_robot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="机器人不存在")
    
    verify_user_password(db, current_user, password_verify.password, "删除机器人", request)
    
    success = robot_service.delete_robot(db, robotId)
    
    log_robot_operation(
        db=db,
        operation="删除",
        robot_id=robotId,
        user_id=current_user.id,
        username=current_user.username,
        success=True,
        details=f"机器人名称:{existing_robot.name}",
        ip_address=get_client_ip(request)
    )
    
    return success_response(message="删除成功")

@router.post("/{robotId}/control", summary="机器人控制")
async def control_robot(
    robotId: str,
    request: RobotControlRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_operator)
):
    result = robot_service.control_robot(db, robotId, request, current_user)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="机器人不存在")
    return success_response(data=result, message="控制成功")
