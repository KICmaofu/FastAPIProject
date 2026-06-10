from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, between
from datetime import datetime
from app.models.system_log import SystemLog
from app.crud.base import CRUDBase

class CRUDSystemLog(CRUDBase[SystemLog]):
    def __init__(self):
        super().__init__(SystemLog)

    def get_multi_by_level(self, db: Session, level: str, skip: int = 0, limit: int = 100) -> List[SystemLog]:
        return db.query(SystemLog).filter(SystemLog.level == level).order_by(desc(SystemLog.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_module(self, db: Session, module: str, skip: int = 0, limit: int = 100) -> List[SystemLog]:
        return db.query(SystemLog).filter(SystemLog.module == module).order_by(desc(SystemLog.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_user(self, db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[SystemLog]:
        return db.query(SystemLog).filter(SystemLog.user_id == user_id).order_by(desc(SystemLog.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_time_range(self, db: Session, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 100) -> List[SystemLog]:
        return db.query(SystemLog).filter(between(SystemLog.create_time, start_time, end_time)).order_by(desc(SystemLog.create_time)).offset(skip).limit(limit).all()

    def create_log(self, db: Session, level: str, module: str, content: str, user_id: Optional[str] = None, ip_address: Optional[str] = None):
        log = SystemLog(
            level=level,
            module=module,
            content=content,
            user_id=user_id,
            ip_address=ip_address
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log