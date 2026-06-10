from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc, between
from datetime import datetime
from app.models.report import Report
from app.crud.base import CRUDBase

class CRUDReport(CRUDBase[Report]):
    def __init__(self):
        super().__init__(Report)

    def get_multi_by_type(self, db: Session, type: str, skip: int = 0, limit: int = 100) -> List[Report]:
        return db.query(Report).filter(Report.type == type, Report.is_deleted == False).order_by(desc(Report.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_creator(self, db: Session, creator_id: str, skip: int = 0, limit: int = 100) -> List[Report]:
        return db.query(Report).filter(Report.creator_id == creator_id, Report.is_deleted == False).order_by(desc(Report.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_time_range(self, db: Session, start_time: datetime, end_time: datetime, skip: int = 0, limit: int = 100) -> List[Report]:
        return db.query(Report).filter(between(Report.start_time, start_time, end_time)).order_by(desc(Report.create_time)).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(Report).filter(Report.is_deleted == False).count()

    def count_by_type(self, db: Session, type: str) -> int:
        return db.query(Report).filter(Report.type == type, Report.is_deleted == False).count()