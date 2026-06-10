from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.alert import Alert
from app.crud import alert as alert_crud
from app.schemas.alert import AlertProcessRequest

class AlertService:
    def get_alert_list(self, db: Session, level: Optional[str] = None, status: Optional[str] = None, page: int = 1, size: int = 20) -> Dict:
        skip = (page - 1) * size
        
        if level and status:
            alerts = db.query(Alert).filter(Alert.level == level, Alert.status == status).order_by(Alert.create_time.desc()).offset(skip).limit(size).all()
            total = db.query(Alert).filter(Alert.level == level, Alert.status == status).count()
        elif level:
            alerts = alert_crud.get_multi_by_level(db, level, skip=skip, limit=size)
            total = alert_crud.count_by_level(db, level)
        elif status:
            if status == "processed":
                alerts = db.query(Alert).filter(Alert.status != "pending").order_by(Alert.create_time.desc()).offset(skip).limit(size).all()
                total = db.query(Alert).filter(Alert.status != "pending").count()
            else:
                alerts = alert_crud.get_multi_by_status(db, status, skip=skip, limit=size)
                total = alert_crud.count_by_status(db, status)
        else:
            alerts = alert_crud.get_multi(db, skip=skip, limit=size)
            total = alert_crud.count(db)
        
        return {
            "list": alerts,
            "total": total,
            "page": page
        }

    def get_alert_by_id(self, db: Session, alert_id: str) -> Optional[Alert]:
        return alert_crud.get(db, alert_id)

    def process_alert(self, db: Session, alert_id: str, request: AlertProcessRequest, user_id: str) -> bool:
        alert = alert_crud.get(db, alert_id)
        if not alert:
            return False
        
        if request.action == "confirm":
            alert.status = "confirmed"
        elif request.action == "ignore":
            alert.status = "ignored"
        else:
            return False
        
        alert.process_remark = request.remark
        alert.process_user_id = user_id
        alert.process_time = datetime.now()
        alert.update_time = datetime.now()
        
        db.commit()
        return True

    def create_alert(self, db: Session, alert_type: str, level: str, message: str, device_id: Optional[str] = None, robot_id: Optional[str] = None, sensor_data_id: Optional[int] = None) -> Alert:
        alert_data = {
            "type": alert_type,
            "level": level,
            "message": message,
            "device_id": device_id,
            "robot_id": robot_id,
            "sensor_data_id": sensor_data_id
        }
        return alert_crud.create(db, obj_in=alert_data)