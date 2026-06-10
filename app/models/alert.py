from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid

class Alert(Base):
    __tablename__ = "t_alert"
    
    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    type = Column(String(50), nullable=False)
    level = Column(Enum("warning", "danger", "critical"), nullable=False)
    message = Column(String(500), nullable=False)
    device_id = Column(String(32), ForeignKey("t_device.id"))
    robot_id = Column(String(32), ForeignKey("t_robot.id"))
    sensor_data_id = Column(Integer, ForeignKey("t_sensor_data.id"))
    status = Column(Enum("pending", "confirmed", "ignored"), nullable=False, default="pending")
    process_remark = Column(String(500))
    process_user_id = Column(String(32), ForeignKey("t_user.id"))
    process_time = Column(DateTime)
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())
    
    device = relationship("Device", backref="alerts")
    robot = relationship("Robot", backref="alerts")
    sensor_data = relationship("SensorData", backref="alerts")
    process_user = relationship("User", backref="processed_alerts")
    
    def __repr__(self):
        return f"<Alert(id={self.id}, type={self.type}, level={self.level})>"