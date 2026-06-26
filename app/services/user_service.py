from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import SysUser
from app.utils.password import verify_password, get_password_hash
from app.utils.auth import create_access_token
from app.utils.response import ApiResponse
from app.services.sys_log_service import SysLogService
from datetime import datetime

class UserService:
    @staticmethod
    def register(db: Session, username: str, password: str, real_name: str, phone: str = None):
        existing_user = db.query(SysUser).filter(SysUser.username == username).first()
        if existing_user:
            return ApiResponse.error(400, "用户名已存在")
        
        if phone:
            existing_phone = db.query(SysUser).filter(SysUser.phone == phone).first()
            if existing_phone:
                return ApiResponse.error(400, "手机号已被使用")
        
        hashed_password = get_password_hash(password)
        new_user = SysUser(
            username=username,
            password=hashed_password,
            real_name=real_name,
            phone=phone,
            role=2,
            status=1
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return ApiResponse.success(msg="注册成功，请等待管理员审核")
    
    @staticmethod
    def login(db: Session, username: str, password: str):
        user = db.query(SysUser).filter(SysUser.username == username, SysUser.is_deleted == 0).first()
        if not user:
            return ApiResponse.error(400, "用户名或密码错误")
        
        if not verify_password(password, user.password):
            return ApiResponse.error(400, "用户名或密码错误")
        
        if user.status != 1:
            return ApiResponse.error(401, "账号未启用")
        
        user.last_login_time = datetime.now()
        db.commit()
        
        SysLogService.add_log(db, username, "用户", "用户登录")
        
        token = create_access_token(data={"sub": user.username})
        return ApiResponse.success({
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "phone": user.phone,
                "role": user.role,
                "status": user.status
            }
        }, msg="登录成功")
    
    @staticmethod
    def get_user_info(db: Session, user: SysUser):
        return ApiResponse.success({
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "phone": user.phone,
            "role": user.role,
            "status": user.status
        })
    
    @staticmethod
    def get_user_list(db: Session, page: int = 1, page_size: int = 10, status: int = None):
        query = db.query(SysUser).filter(SysUser.is_deleted == 0)
        if status is not None:
            query = query.filter(SysUser.status == status)
        
        total = query.count()
        users = query.offset((page - 1) * page_size).limit(page_size).all()
        
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "real_name": user.real_name,
                "phone": user.phone,
                "role": user.role,
                "status": user.status,
                "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None
            })
        
        return ApiResponse.success_pagination(user_list, total, page, page_size)
    
    @staticmethod
    def get_user_detail(db: Session, user_id: int):
        user = db.query(SysUser).filter(SysUser.id == user_id, SysUser.is_deleted == 0).first()
        if not user:
            return ApiResponse.not_found("用户不存在")
        
        return ApiResponse.success({
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "phone": user.phone,
            "role": user.role,
            "status": user.status,
            "create_time": user.create_time.strftime("%Y-%m-%d %H:%M:%S") if user.create_time else None
        })
    
    @staticmethod
    def add_user(db: Session, username: str, password: str, real_name: str, role: int):
        existing_user = db.query(SysUser).filter(SysUser.username == username).first()
        if existing_user:
            return ApiResponse.error(400, "用户名已存在")
        
        hashed_password = get_password_hash(password)
        new_user = SysUser(
            username=username,
            password=hashed_password,
            real_name=real_name,
            role=role,
            status=1
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        SysLogService.add_log(db, "admin", "用户", f"添加用户: {username}")
        return ApiResponse.success(msg="添加用户成功")
    
    @staticmethod
    def update_user(db: Session, user_id: int, real_name: str = None, phone: str = None, role: int = None):
        user = db.query(SysUser).filter(SysUser.id == user_id, SysUser.is_deleted == 0).first()
        if not user:
            return ApiResponse.not_found("用户不存在")
        
        if real_name:
            user.real_name = real_name
        if phone:
            existing_phone = db.query(SysUser).filter(SysUser.phone == phone, SysUser.id != user_id).first()
            if existing_phone:
                return ApiResponse.error(400, "手机号已被使用")
            user.phone = phone
        if role is not None:
            user.role = role
        
        db.commit()
        SysLogService.add_log(db, "admin", "用户", f"更新用户: {user.username}")
        return ApiResponse.success(msg="更新用户成功")
    
    @staticmethod
    def delete_user(db: Session, user_id: int):
        user = db.query(SysUser).filter(SysUser.id == user_id, SysUser.is_deleted == 0).first()
        if not user:
            return ApiResponse.not_found("用户不存在")
        
        user.is_deleted = 1
        db.commit()
        SysLogService.add_log(db, "admin", "用户", f"删除用户: {user.username}")
        return ApiResponse.success(msg="删除用户成功")
    
    @staticmethod
    def update_user_status(db: Session, user_id: int, status: int):
        user = db.query(SysUser).filter(SysUser.id == user_id, SysUser.is_deleted == 0).first()
        if not user:
            return ApiResponse.not_found("用户不存在")
        
        user.status = status
        db.commit()
        return ApiResponse.success(msg="更新状态成功")
    
    @staticmethod
    def reset_password(db: Session, username: str, phone: str, new_password: str):
        user = db.query(SysUser).filter(SysUser.username == username, SysUser.phone == phone, SysUser.is_deleted == 0).first()
        if not user:
            return ApiResponse.error(400, "用户名或手机号错误")
        
        user.password = get_password_hash(new_password)
        db.commit()
        return ApiResponse.success(msg="密码重置成功")