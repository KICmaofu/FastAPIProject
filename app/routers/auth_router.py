from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.services import auth_service
from app.schemas.auth import LoginRequest, LoginResponse, UserInfoResponse, RegisterRequest, ResetPasswordRequest
from app.utils.response import success_response, error_response

router = APIRouter(prefix="/api/auth", tags=["认证模块"])

@router.post("/login", response_model=LoginResponse, summary="用户登录")
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    token, user = auth_service.login(db, request.username, request.phone, request.password)
    
    if not token or not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名或密码错误")
    
    permissions = auth_service.get_user_permissions(user)
    
    return LoginResponse(
        token=token,
        user=UserInfoResponse(
            id=user.id,
            username=user.username,
            phone=user.phone,
            role=user.role,
            permissions=permissions
        )
    )

@router.post("/register", summary="用户注册")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    if request.password != request.confirmPassword:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="两次输入的密码不一致")
    
    user, error = auth_service.register(
        db, 
        request.username, 
        request.phone, 
        request.password,
        request.role or "viewer",
        request.adminKey
    )
    
    if not user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error)
    
    return success_response(data={"id": user.id, "username": user.username, "role": user.role}, message="注册成功")

@router.post("/reset-password", summary="密码重置")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    success = auth_service.reset_password(db, request.phone, request.newPassword)
    
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户不存在")
    
    return success_response(message="密码重置成功")