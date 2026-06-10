from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

class Device(Base):
    __tablename__ = "t_device"
    
    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    name = Column(String(100), nullable=False)
    type = Column(Enum("robot", "sensor", "gateway", "other"), nullable=False)
    model = Column(String(50))
    status = Column(Enum("online", "offline", "warning"), nullable=False, default="offline")
    location = Column(String(200))
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f"<Device(id={self.id}, name={self.name}, type={self.type})>"