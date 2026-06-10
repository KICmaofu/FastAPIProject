from sqlalchemy import Column, DateTime, DECIMAL, String, Integer
from sqlalchemy.sql import func
from app.config.database import Base

class EnvironmentData(Base):
    __tablename__ = "t_environment_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    record_time = Column(DateTime, nullable=False)
    temperature = Column(DECIMAL(5, 2))
    humidity = Column(DECIMAL(5, 2))
    gas = Column(DECIMAL(5, 2))
    pm25 = Column(DECIMAL(5, 2))
    max_thermal_temp = Column(DECIMAL(6, 2))
    data_interval = Column(String(10), nullable=False, default="1m")
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    
    def __repr__(self):
        return f"<EnvironmentData(id={self.id}, record_time={self.record_time})>"