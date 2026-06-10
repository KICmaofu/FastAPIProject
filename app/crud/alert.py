from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, between
from datetime import datetime
from app.models.alert import Alert
from app.crud.base import CRUDBase

class CRUDAlert(CRUDBase[Alert]):
    def __init__(self):
        super().__init__(Alert)

    def get_multi_by_level(self, db: Session, level: str, skip: int = 0, limit: int = 100) -> List[Alert]:
        return db.query(Alert).filter(Alert.level == level).order_by(desc(Alert.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Alert]:
        return db.query(Alert).filter(Alert.status == status).order_by(desc(Alert.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_device(self, db: Session, device_id: str, skip: int = 0, limit: int = 100) -> List[Alert]:
        return db.query(Alert).filter(Alert.device_id == device_id).order_by(desc(Alert.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_time_range(self, db: Session, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 100) -> List[Alert]:
        return db.query(Alert).filter(between(Alert.create_time, start_time, end_time)).order_by(desc(Alert.create_time)).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(Alert).count()

    def count_by_status(self, db: Session, status: str) -> int:
        return db.query(Alert).filter(Alert.status == status).count()

    def count_by_level(self, db: Session, level: str) -> int:
        return db.query(Alert).filter(Alert.level == level).count()