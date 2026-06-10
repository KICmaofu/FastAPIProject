from typing import Optional
from sqlalchemy.orm import Session
from app.models.system_config import SystemConfig
from app.crud.base import CRUDBase

class CRUDSystemConfig(CRUDBase[SystemConfig]):
    def __init__(self):
        super().__init__(SystemConfig)

    def get_by_key(self, db: Session, config_key: str) -> Optional[SystemConfig]:
        return db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()

    def update_by_key(self, db: Session, config_key: str, config_value: str):
        config = db.query(SystemConfig).filter(SystemConfig.config_key == config_key).first()
        if config:
            config.config_value = config_value
            db.commit()
            db.refresh(config)
            return config
        return None