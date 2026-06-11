from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user, require_admin
from app.models.user import User
from app.services import user_service
from app.schemas.user import UserResponse, UserListResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api/users", tags=["用户模块"])

@router.get("", summary="获取用户列表")
async def get_user_list(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = user_service.get_user_list(db, page, size, role)

    user_list = []
    for user in result["list"]:
        user_list.append(UserResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            role=user.role,
            status=user.status
        ))

    return success_response(data={
        "list": user_list,
        "total": result["total"],
        "page": result["page"]
    })

@router.get("/me", summary="获取当前用户信息")
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return success_response(data=UserResponse.model_validate(current_user))

@router.put("/{userId}", summary="更新用户信息")
async def update_user(
    userId: str,
    username: Optional[str] = Query(None),
    phone: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    from app.schemas.user import UserUpdate
    update_data = UserUpdate(username=username, phone=phone, role=role)

    user = user_service.update_user(db, userId, update_data, current_user)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return success_response(data=UserResponse(
        id=user.id,
        username=user.username,
        phone=user.phone,
        role=user.role,
        status=user.status
    ))

@router.delete("/{userId}", summary="删除用户")
async def delete_user(
    userId: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    success = user_service.delete_user(db, userId)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")

    return success_response(message="删除成功")
