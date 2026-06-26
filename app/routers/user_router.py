# 用户模块路由 - /api/user
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
import bcrypt
import jwt

from app.config.database import get_db
from app.config.settings import settings
from app.schemas.user import (
    UserRegisterRequest, UserLoginRequest, UserInfoResponse, LoginResponse,
    UserAddRequest, UserUpdateRequest, ResetPwdRequest, UserDeleteRequest
)
from app.schemas.common import ApiResponse, PagedData, StatusRequest
from app.models.user import SysUser
from app.models.system_log import SysLog
from app.dependencies.auth import get_current_user, require_admin

router = APIRouter(prefix="/api/user", tags=["用户模块"])


def create_log(db: Session, username: str, module: str, operation: str, ip: str, detail: str):
    """创建操作日志"""
    log = SysLog(username=username, module=module, operation=operation, ip_address=ip, detail=detail)
    db.add(log)
    db.commit()


def hash_password(password: str) -> str:
    """密码加密"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """密码验证"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_token(user_id: int) -> str:
    """生成JWT Token"""
    payload = {"user_id": user_id, "exp": datetime.utcnow() + settings.JWT_EXPIRE_HOURS}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")


# 1. 注册
@router.post("/register", summary="用户注册")
async def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册"""
    # 检查用户名是否存在
    existing = db.query(SysUser).filter(SysUser.username == request.username).first()
    if existing:
        return ApiResponse(code=400, msg="用户名已存在", data=None)
    
    # 创建用户
    user = SysUser(
        username=request.username,
        password=hash_password(request.password),
        real_name=request.real_name,
        phone=request.phone,
        role=2,  # 默认运维员
        status=1  # 直接启用，可登录
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return ApiResponse(code=200, msg="注册成功", data=None)


# 2. 登录
@router.post("/login", summary="用户登录")
async def login(request: UserLoginRequest, db: Session = Depends(get_db), http_request: Request = None):
    """用户登录"""
    user = db.query(SysUser).filter(SysUser.username == request.username).first()
    if not user:
        return ApiResponse(code=400, msg="用户不存在", data=None)
    
    if not verify_password(request.password, user.password):
        return ApiResponse(code=400, msg="密码错误", data=None)
    
    if user.status != 1:
        return ApiResponse(code=400, msg="用户已被禁用", data=None)
    
    # 更新登录时间
    user.last_login_time = datetime.utcnow()
    db.commit()
    
    # 生成Token
    token = create_token(user.id)
    
    # 记录日志
    ip = http_request.client.host if http_request else "unknown"
    create_log(db, user.username, "用户", "登录", ip, f"用户 {user.username} 登录成功")
    
    return ApiResponse(code=200, msg="登录成功", data={
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "phone": user.phone,
            "role": user.role,
            "status": user.status
        }
    })


# 3. 退出登录
@router.post("/logout", summary="退出登录")
async def logout(current_user: SysUser = Depends(get_current_user), db: Session = Depends(get_db)):
    """退出登录"""
    return ApiResponse(code=200, msg="退出成功", data=None)


# 4. 获取用户信息
@router.get("/info", summary="获取用户信息")
async def get_user_info(current_user: SysUser = Depends(get_current_user)):
    """获取当前用户信息"""
    return ApiResponse(code=200, msg="success", data={
        "id": current_user.id,
        "username": current_user.username,
        "real_name": current_user.real_name,
        "phone": current_user.phone,
        "role": current_user.role,
        "status": current_user.status
    })


# 5. 获取用户列表（管理员）
@router.get("/list", summary="获取用户列表")
async def get_user_list(
    page: int = 1, pageSize: int = 10, status: int = None,
    current_user: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户列表（管理员）"""
    query = db.query(SysUser)
    if status is not None:
        query = query.filter(SysUser.status == status)
    
    total = query.count()
    users = query.offset((page - 1) * pageSize).limit(pageSize).all()
    
    user_list = [{
        "id": u.id, "username": u.username, "real_name": u.real_name,
        "phone": u.phone, "role": u.role, "status": u.status,
        "create_time": u.create_time.isoformat() if u.create_time else None
    } for u in users]
    
    return ApiResponse(code=200, msg="success", data={
        "list": user_list, "total": total, "page": page, "pageSize": pageSize
    })


# 6. 获取用户详情（管理员）
@router.get("/{id}", summary="获取用户详情")
async def get_user_detail(
    id: int,
    current_user: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """获取用户详情"""
    user = db.query(SysUser).filter(SysUser.id == id).first()
    if not user:
        return ApiResponse(code=404, msg="用户不存在", data=None)
    
    return ApiResponse(code=200, msg="success", data={
        "id": user.id, "username": user.username, "real_name": user.real_name,
        "phone": user.phone, "role": user.role, "status": user.status,
        "create_time": user.create_time.isoformat() if user.create_time else None
    })


# 7. 添加用户（管理员）
@router.post("/add", summary="添加用户")
async def add_user(
    request: UserAddRequest,
    current_user: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """添加用户（管理员）"""
    existing = db.query(SysUser).filter(SysUser.username == request.username).first()
    if existing:
        return ApiResponse(code=400, msg="用户名已存在", data=None)
    
    user = SysUser(
        username=request.username,
        password=hash_password(request.password),
        real_name=request.real_name,
        role=request.role,
        status=1
    )
    db.add(user)
    db.commit()
    
    return ApiResponse(code=200, msg="添加成功", data=None)


# 8. 更新用户（管理员）
@router.put("/update", summary="更新用户")
async def update_user(
    request: UserUpdateRequest,
    current_user: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新用户（管理员）"""
    user = db.query(SysUser).filter(SysUser.id == request.id).first()
    if not user:
        return ApiResponse(code=404, msg="用户不存在", data=None)
    
    if request.real_name:
        user.real_name = request.real_name
    if request.phone:
        user.phone = request.phone
    if request.role:
        user.role = request.role
    db.commit()
    
    return ApiResponse(code=200, msg="更新成功", data=None)


# 9. 删除用户（管理员）
@router.post("/delete", summary="删除用户")
async def delete_user(
    request: UserDeleteRequest,
    current_user: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """删除用户（管理员）"""
    user = db.query(SysUser).filter(SysUser.id == request.id).first()
    if not user:
        return ApiResponse(code=404, msg="用户不存在", data=None)
    
    if user.id == current_user.id:
        return ApiResponse(code=400, msg="不能删除自己", data=None)
    
    db.delete(user)
    db.commit()
    
    return ApiResponse(code=200, msg="删除成功", data=None)


# 10. 更新用户状态（管理员）
@router.post("/updateStatus", summary="更新用户状态")
async def update_user_status(
    request: StatusRequest,
    current_user: SysUser = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """更新用户状态（管理员）"""
    user = db.query(SysUser).filter(SysUser.id == request.id).first()
    if not user:
        return ApiResponse(code=404, msg="用户不存在", data=None)
    
    user.status = request.status
    db.commit()
    
    return ApiResponse(code=200, msg="状态更新成功", data=None)


# 11. 重置密码
@router.post("/resetPwd", summary="重置密码")
async def reset_password(request: ResetPwdRequest, db: Session = Depends(get_db)):
    """重置密码"""
    user = db.query(SysUser).filter(
        SysUser.username == request.username,
        SysUser.phone == request.phone
    ).first()
    if not user:
        return ApiResponse(code=400, msg="用户信息不匹配", data=None)
    
    user.password = hash_password(request.newPassword)
    db.commit()
    
    return ApiResponse(code=200, msg="密码重置成功", data=None)