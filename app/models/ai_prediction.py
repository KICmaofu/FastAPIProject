from sqlalchemy import Column, DateTime, JSON, Enum, ForeignKey, Integer, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class AIPrediction(Base):
    __tablename__ = "t_ai_prediction"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(Enum("environment", "device_failure", "anomaly"), nullable=False)
    device_id = Column(String(32), ForeignKey("t_device.id"))
    predict_time = Column(DateTime, nullable=False)
    result_json = Column(JSON, nullable=False)
    risk_level = Column(Enum("low", "medium", "high"))
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    
    device = relationship("Device", backref="ai_predictions")
    
    def __repr__(self):
        return f"<AIPrediction(id={self.id}, type={self.type})>"