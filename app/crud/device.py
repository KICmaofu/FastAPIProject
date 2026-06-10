from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.device import Device
from app.crud.base import CRUDBase

class CRUDDevice(CRUDBase[Device]):
    def __init__(self):
        super().__init__(Device)

    def get_multi_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Device]:
        return db.query(Device).filter(Device.status == status, Device.is_deleted == False).offset(skip).limit(limit).all()

    def get_multi_by_type(self, db: Session, type: str, skip: int = 0, limit: int = 100) -> List[Device]:
        return db.query(Device).filter(Device.type == type, Device.is_deleted == False).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(Device).filter(Device.is_deleted == False).count()

    def count_by_status(self, db: Session, status: str) -> int:
        return db.query(Device).filter(Device.status == status, Device.is_deleted == False).count()