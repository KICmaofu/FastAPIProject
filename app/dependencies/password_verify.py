from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.user import User
from app.models.system_log import SystemLog
from app.utils.security import verify_password

MAX_VERIFY_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15
ATTEMPT_WINDOW_MINUTES = 30

_password_verify_cache: dict = {}

class PasswordVerifyCache:
    def __init__(self):
        self.attempts = 0
        self.locked_until: Optional[datetime] = None
        self.attempt_times: list = []
    
    def is_locked(self) -> bool:
        if self.locked_until and datetime.now() < self.locked_until:
            return True
        if self.locked_until and datetime.now() >= self.locked_until:
            self.locked_until = None
            self.attempts = 0
            self.attempt_times = []
        return False
    
    def add_attempt(self, success: bool):
        now = datetime.now()
        if not success:
            self.attempts += 1
            self.attempt_times.append(now)
            
            self.attempt_times = [
                t for t in self.attempt_times 
                if now - t < timedelta(minutes=ATTEMPT_WINDOW_MINUTES)
            ]
            
            if len(self.attempt_times) >= MAX_VERIFY_ATTEMPTS:
                self.locked_until = now + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                self.attempts = 0
                self.attempt_times = []
        else:
            self.attempts = 0
            self.attempt_times = []
            self.locked_until = None
    
    def get_remaining_lock_time(self) -> int:
        if self.locked_until and datetime.now() < self.locked_until:
            return int((self.locked_until - datetime.now()).total_seconds() / 60) + 1
        return 0

def get_password_verify_cache(user_id: str) -> PasswordVerifyCache:
    cache_key = f"verify:{user_id}"
    if cache_key not in _password_verify_cache:
        _password_verify_cache[cache_key] = PasswordVerifyCache()
    return _password_verify_cache[cache_key]

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"

def log_password_verify(
    db: Session,
    user_id: str,
    username: str,
    operation: str,
    success: bool,
    reason: str = None,
    ip_address: str = "unknown"
):
    log = SystemLog(
        level="warn" if not success else "info",
        module="password_verify",
        content=f"密码验证 - 操作:{operation}, 用户:{username}, 结果:{'成功' if success else '失败'}, 原因:{reason or '无'}",
        user_id=user_id,
        ip_address=ip_address
    )
    db.add(log)
    db.commit()

def verify_user_password(
    db: Session,
    current_user: User,
    password: str,
    operation: str,
    request: Request = None
) -> bool:
    cache = get_password_verify_cache(current_user.id)
    
    if cache.is_locked():
        remaining = cache.get_remaining_lock_time()
        ip_address = get_client_ip(request) if request else "unknown"
        log_password_verify(
            db, current_user.id, current_user.username,
            operation, False, f"账户已被锁定，剩余{remaining}分钟",
            ip_address
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"验证失败次数过多，账户已被锁定，请在{remaining}分钟后重试"
        )
    
    ip_address = get_client_ip(request) if request else "unknown"
    
    if not verify_password(password, current_user.password_hash):
        cache.add_attempt(False)
        
        log_password_verify(
            db, current_user.id, current_user.username,
            operation, False, "密码错误", ip_address
        )
        
        remaining_attempts = MAX_VERIFY_ATTEMPTS - len(cache.attempt_times)
        if remaining_attempts > 0:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"密码错误，剩余{remaining_attempts}次尝试机会"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="验证失败次数过多，账户已被临时锁定"
            )
    
    cache.add_attempt(True)
    
    log_password_verify(
        db, current_user.id, current_user.username,
        operation, True, "验证通过", ip_address
    )
    
    return True

class PasswordVerified:
    pass

async def require_password_verified(
    password: str,
    operation: str,
    request: Request = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(lambda: None)
) -> PasswordVerified:
    from app.dependencies.auth import get_current_active_user
    
    user = await get_current_active_user()
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="密码不能为空"
        )
    
    verify_user_password(db, user, password, operation, request)
    
    return PasswordVerified()
