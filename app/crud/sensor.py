from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.sensor import Sensor
from app.crud.base import CRUDBase

class CRUDSensor(CRUDBase[Sensor]):
    def __init__(self):
        super().__init__(Sensor)

    def get_multi_by_type(self, db: Session, type: str, skip: int = 0, limit: int = 100) -> List[Sensor]:
        return db.query(Sensor).filter(Sensor.type == type, Sensor.is_deleted == False).offset(skip).limit(limit).all()

    def get_multi_by_device(self, db: Session, device_id: str, skip: int = 0, limit: int = 100) -> List[Sensor]:
        return db.query(Sensor).filter(Sensor.device_id == device_id, Sensor.is_deleted == False).offset(skip).limit(limit).all()

    def get_multi_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Sensor]:
        return db.query(Sensor).filter(Sensor.status == status, Sensor.is_deleted == False).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(Sensor).filter(Sensor.is_deleted == False).count()