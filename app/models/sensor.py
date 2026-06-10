from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid

class Sensor(Base):
    __tablename__ = "t_sensor"
    
    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    name = Column(String(100), nullable=False)
    type = Column(Enum("temperature", "humidity", "gas", "pm25", "thermal"), nullable=False)
    unit = Column(String(20), nullable=False)
    status = Column(Enum("normal", "warning", "danger"), nullable=False, default="normal")
    device_id = Column(String(32), ForeignKey("t_device.id"))
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    device = relationship("Device", backref="sensors")
    
    def __repr__(self):
        return f"<Sensor(id={self.id}, name={self.name}, type={self.type})>"