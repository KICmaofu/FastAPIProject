from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.robot import Robot
from app.models.robot_position_history import RobotPositionHistory
from app.crud.base import CRUDBase

class CRUDRobot(CRUDBase[Robot]):
    def __init__(self):
        super().__init__(Robot)

    def get_multi_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Robot]:
        return db.query(Robot).filter(Robot.status == status, Robot.is_deleted == False).offset(skip).limit(limit).all()

    def get_multi_active(self, db: Session, skip: int = 0, limit: int = 100) -> List[Robot]:
        return db.query(Robot).filter(Robot.is_deleted == False).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(Robot).filter(Robot.is_deleted == False).count()

    def count_by_status(self, db: Session, status: str) -> int:
        return db.query(Robot).filter(Robot.status == status, Robot.is_deleted == False).count()

    def get_latest_position(self, db: Session, robot_id: str) -> Optional[RobotPositionHistory]:
        return db.query(RobotPositionHistory).filter(RobotPositionHistory.robot_id == robot_id).order_by(desc(RobotPositionHistory.record_time)).first()

    def create_position_history(self, db: Session, robot_id: str, x: float, y: float, battery: Optional[float] = None, speed: Optional[float] = None):
        from datetime import datetime
        position = RobotPositionHistory(
            robot_id=robot_id,
            x=x,
            y=y,
            battery=battery,
            speed=speed,
            record_time=datetime.now()
        )
        db.add(position)
        db.commit()
        db.refresh(position)
        return position