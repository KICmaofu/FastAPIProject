from sqlalchemy import Column, DateTime, DECIMAL, JSON, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class ThermalData(Base):
    __tablename__ = "t_thermal_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    sensor_data_id = Column(Integer, ForeignKey("t_sensor_data.id"), nullable=False, unique=True)
    max_temp_matrix = Column(JSON, nullable=False)
    max_temp_value = Column(DECIMAL(6, 2))
    min_temp_value = Column(DECIMAL(6, 2))
    avg_temp_value = Column(DECIMAL(6, 2))
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    
    sensor_data = relationship("SensorData", backref="thermal_data")
    
    def __repr__(self):
        return f"<ThermalData(id={self.id}, sensor_data_id={self.sensor_data_id})>"