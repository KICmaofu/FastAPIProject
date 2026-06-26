# 认证依赖模块
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from datetime import datetime

from app.config.database import get_db
from app.config.settings import settings
from app.models.user import SysUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/user/login")


def decode_access_token(token: str) -> Optional[int]:
    """解码JWT Token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("user_id")
        return user_id
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> SysUser:
    """获取当前用户"""
    user_id = decode_access_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或Token失效",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(SysUser).filter(SysUser.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户不存在",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_active_user(
    current_user: SysUser = Depends(get_current_user)
) -> SysUser:
    """获取当前活跃用户"""
    if current_user.status != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户已被禁用"
        )
    return current_user


async def require_admin(
    current_user: SysUser = Depends(get_current_active_user)
) -> SysUser:
    """需要管理员权限"""
    if current_user.role != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


async def require_operator(
    current_user: SysUser = Depends(get_current_active_user)
) -> SysUser:
    """需要操作员权限（管理员或运维员）"""
    if current_user.role not in [1, 2]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要操作员权限"
        )
    return current_user