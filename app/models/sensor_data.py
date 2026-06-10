from sqlalchemy import Column, String, DateTime, Boolean, DECIMAL, JSON, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class SensorData(Base):
    __tablename__ = "t_sensor_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    robot_id = Column(String(32), ForeignKey("t_robot.id"), nullable=False)
    temperature = Column(DECIMAL(5, 2), nullable=False)
    humidity = Column(DECIMAL(5, 2), nullable=False)
    smoke_level = Column(DECIMAL(5, 2), nullable=False)
    battery = Column(DECIMAL(5, 1))
    human_detected = Column(Boolean, nullable=False, default=False)
    fire_risk = Column(Integer, nullable=False, default=0)
    env_status = Column(String(50))
    raw_json = Column(JSON)
    receive_time = Column(DateTime, nullable=False)
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    
    robot = relationship("Robot", backref="sensor_data")
    
    def __repr__(self):
        return f"<SensorData(id={self.id}, robot_id={self.robot_id}, temperature={self.temperature})>"