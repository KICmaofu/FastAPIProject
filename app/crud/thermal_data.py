from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, between, func
from datetime import datetime
from app.models.thermal_data import ThermalData
from app.models.sensor_data import SensorData
from app.crud.base import CRUDBase

class CRUDThermalData(CRUDBase[ThermalData]):
    def __init__(self):
        super().__init__(ThermalData)

    def get_by_sensor_data_id(self, db: Session, sensor_data_id: int) -> Optional[ThermalData]:
        return db.query(ThermalData).filter(ThermalData.sensor_data_id == sensor_data_id).first()

    def get_latest(self, db: Session) -> Optional[ThermalData]:
        latest_sensor = db.query(
            SensorData.id
        ).join(
            ThermalData,
            SensorData.id == ThermalData.sensor_data_id
        ).order_by(
            SensorData.robot_id, desc(SensorData.receive_time)
        ).first()

        if latest_sensor:
            return db.query(ThermalData).filter(ThermalData.sensor_data_id == latest_sensor.id).first()
        return None

    def get_multi_by_time_range(self, db: Session, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 100) -> List[ThermalData]:
        latest_per_robot = db.query(
            SensorData.robot_id,
            func.max(SensorData.receive_time).label('max_time')
        ).filter(
            between(SensorData.receive_time, start_time, end_time)
        ).group_by(SensorData.robot_id).subquery()

        latest_sensor_ids = db.query(SensorData.id).join(
            latest_per_robot,
            (SensorData.robot_id == latest_per_robot.c.robot_id) &
            (SensorData.receive_time == latest_per_robot.c.max_time)
        ).subquery()

        return db.query(ThermalData).join(
            latest_sensor_ids,
            ThermalData.sensor_data_id == latest_sensor_ids.c.id
        ).all()
