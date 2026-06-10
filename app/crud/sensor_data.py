from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, between, func
from datetime import datetime
from app.models.sensor_data import SensorData
from app.crud.base import CRUDBase

class CRUDSensorData(CRUDBase[SensorData]):
    def __init__(self):
        super().__init__(SensorData)

    def get_latest_by_robot(self, db: Session, robot_id: str) -> Optional[SensorData]:
        return db.query(SensorData).filter(SensorData.robot_id == robot_id).order_by(desc(SensorData.receive_time)).first()

    def get_multi_by_robot(self, db: Session, robot_id: str, skip: int = 0, limit: int = 100) -> List[SensorData]:
        return db.query(SensorData).filter(SensorData.robot_id == robot_id).order_by(desc(SensorData.receive_time)).offset(skip).limit(limit).all()

    def get_multi_by_time_range(self, db: Session, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 100) -> List[SensorData]:
        return db.query(SensorData).filter(between(SensorData.receive_time, start_time, end_time)).order_by(desc(SensorData.receive_time)).offset(skip).limit(limit).all()

    def get_latest_all(self, db: Session) -> List[SensorData]:
        latest_per_robot = db.query(
            SensorData.robot_id,
            func.max(SensorData.receive_time).label('max_time')
        ).group_by(SensorData.robot_id).subquery()

        return db.query(SensorData).join(
            latest_per_robot,
            (SensorData.robot_id == latest_per_robot.c.robot_id) & (SensorData.receive_time == latest_per_robot.c.max_time)
        ).all()
