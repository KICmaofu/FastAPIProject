from sqlalchemy import Column, String, DateTime, Boolean, Enum, DECIMAL
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

class Robot(Base):
    __tablename__ = "t_robot"
    
    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    name = Column(String(100), nullable=False)
    model = Column(String(50), nullable=False)
    battery = Column(DECIMAL(5, 1), nullable=False, default=0)
    status = Column(Enum("idle", "moving", "charging", "offline"), nullable=False, default="idle")
    location = Column(String(200))
    speed = Column(DECIMAL(5, 2), default=0.00)
    last_online_time = Column(DateTime)
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f"<Robot(id={self.id}, name={self.name}, status={self.status})>"