from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.utils.auth import get_current_user, require_admin
from app.utils.response import ApiResponse
from app.schemas.user import (
    UserRegister, UserLogin, UserAdd, UserUpdate, UserDelete,
    UserUpdateStatus, UserResetPwd
)
from app.services.user_service import UserService

router = APIRouter(prefix="/api/user", tags=["用户模块"])

@router.post("/register")
async def register(data: UserRegister, db: Session = Depends(get_db)):
    return UserService.register(db, data.username, data.password, data.real_name, data.phone)

@router.post("/login")
async def login(data: UserLogin, db: Session = Depends(get_db)):
    return UserService.login(db, data.username, data.password)

@router.post("/logout")
async def logout(user = Depends(get_current_user)):
    return ApiResponse.success(msg="退出成功")

@router.get("/info")
async def get_user_info(db: Session = Depends(get_db), user = Depends(get_current_user)):
    return UserService.get_user_info(db, user)

@router.get("/list")
async def get_user_list(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    status: int = Query(None),
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    return UserService.get_user_list(db, page, pageSize, status)

@router.get("/{id}")
async def get_user_detail(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    return UserService.get_user_detail(db, id)

@router.post("/add")
async def add_user(data: UserAdd, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return UserService.add_user(db, data.username, data.password, data.real_name, data.role)

@router.put("/update")
async def update_user(data: UserUpdate, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return UserService.update_user(db, data.id, data.real_name, data.phone, data.role)

@router.post("/delete")
async def delete_user(data: UserDelete, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return UserService.delete_user(db, data.id)

@router.post("/updateStatus")
async def update_user_status(data: UserUpdateStatus, db: Session = Depends(get_db), admin = Depends(require_admin)):
    return UserService.update_user_status(db, data.id, data.status)

@router.post("/resetPwd")
async def reset_password(data: UserResetPwd, db: Session = Depends(get_db)):
    return UserService.reset_password(db, data.username, data.phone, data.newPassword)