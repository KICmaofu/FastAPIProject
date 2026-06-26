from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.sys_log import SysLog
from app.utils.response import ApiResponse

class SysLogService:
    @staticmethod
    def add_log(db: Session, username: str, module: str, operation: str, ip_address: str = "127.0.0.1", detail: str = None):
        new_log = SysLog(
            username=username,
            module=module,
            operation=operation,
            ip_address=ip_address,
            detail=detail
        )
        db.add(new_log)
        db.commit()
    
    @staticmethod
    def get_log_list(db: Session, page: int = 1, page_size: int = 10, username: str = None, start_time: str = None, end_time: str = None):
        query = db.query(SysLog)
        if username:
            query = query.filter(SysLog.username == username)
        if start_time:
            query = query.filter(SysLog.create_time >= start_time)
        if end_time:
            query = query.filter(SysLog.create_time <= end_time)
        
        total = query.count()
        logs = query.order_by(desc(SysLog.create_time)).offset((page - 1) * page_size).limit(page_size).all()
        
        log_list = []
        for log in logs:
            log_list.append({
                "id": log.id,
                "username": log.username,
                "module": log.module,
                "operation": log.operation,
                "ip_address": log.ip_address,
                "detail": log.detail,
                "create_time": log.create_time.strftime("%Y-%m-%d %H:%M:%S") if log.create_time else None
            })
        
        return ApiResponse.success_pagination(log_list, total, page, page_size)