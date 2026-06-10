from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.crud import system_config as config_crud, system_log as log_crud
from app.schemas.system import SystemStatusResponse, SystemConfigUpdate
from app.config.settings import settings

class SystemService:
    def get_system_status(self, db: Session) -> SystemStatusResponse:
        try:
            import psutil
            cpu_usage = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
        except ImportError:
            cpu_usage = None
            memory_usage = None
        
        return SystemStatusResponse(
            status="normal",
            uptime=0,
            version=settings.APP_VERSION,
            cpuUsage=cpu_usage,
            memoryUsage=memory_usage
        )

    def get_system_logs(self, db: Session, level: Optional[str] = None, startTime: Optional[str] = None, endTime: Optional[str] = None, page: int = 1, size: int = 20) -> Dict:
        skip = (page - 1) * size
        
        query = db.query(log_crud.model)
        
        if level:
            query = query.filter(log_crud.model.level == level)
        
        if startTime:
            start = datetime.fromisoformat(startTime)
            query = query.filter(log_crud.model.create_time >= start)
        
        if endTime:
            end = datetime.fromisoformat(endTime)
            query = query.filter(log_crud.model.create_time <= end)
        
        logs = query.order_by(log_crud.model.create_time.desc()).offset(skip).limit(size).all()
        total = query.count()
        
        return {
            "list": logs,
            "total": total,
            "page": page
        }

    def update_system_config(self, db: Session, config: SystemConfigUpdate) -> bool:
        update_data = config.dict(exclude_unset=True)
        
        if "updateInterval" in update_data:
            config_crud.update_by_key(db, "update_interval", str(update_data["updateInterval"]))
        
        if "alertThreshold" in update_data:
            import json
            config_crud.update_by_key(db, "alert_threshold", json.dumps(update_data["alertThreshold"]))
        
        return True

    def add_system_log(self, db: Session, level: str, module: str, content: str, user_id: Optional[str] = None, ip_address: Optional[str] = None):
        log_crud.create_log(db, level, module, content, user_id, ip_address)