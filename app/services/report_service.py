from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.report import Report
from app.crud import report as report_crud
from app.schemas.report import ReportCreate

class ReportService:
    def get_report_list(self, db: Session, type: Optional[str] = None, page: int = 1, size: int = 20) -> Dict:
        skip = (page - 1) * size
        
        if type:
            reports = report_crud.get_multi_by_type(db, type, skip=skip, limit=size)
            total = report_crud.count_by_type(db, type)
        else:
            reports = report_crud.get_multi(db, skip=skip, limit=size)
            total = report_crud.count(db)
        
        return {
            "list": reports,
            "total": total,
            "page": page
        }

    def get_report_by_id(self, db: Session, report_id: str) -> Optional[Report]:
        return report_crud.get(db, report_id)

    def generate_report(self, db: Session, data: ReportCreate, user_id: str) -> Report:
        start = datetime.fromisoformat(data.startTime)
        end = datetime.fromisoformat(data.endTime)
        
        report_data = {
            "type": data.type,
            "title": f"{data.type}报告 - {data.startTime} 至 {data.endTime}",
            "content": f"报告内容将在此处生成，包含统计时间范围内的数据分析。",
            "start_time": start,
            "end_time": end,
            "creator_id": user_id
        }
        
        return report_crud.create(db, obj_in=report_data)

    def delete_report(self, db: Session, report_id: str) -> bool:
        report = report_crud.get(db, report_id)
        if not report:
            return False
        report.is_deleted = True
        db.commit()
        return True