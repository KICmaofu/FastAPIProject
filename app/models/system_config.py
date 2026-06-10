from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

class SystemConfig(Base):
    __tablename__ = "t_system_config"
    
    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    config_key = Column(String(100), nullable=False, unique=True)
    config_value = Column(Text)
    description = Column(String(500))
    update_time = Column(DateTime, onupdate=func.now())
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<SystemConfig(id={self.id}, config_key={self.config_key})>"