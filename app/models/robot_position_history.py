from sqlalchemy import Column, String, DateTime, DECIMAL, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class RobotPositionHistory(Base):
    __tablename__ = "t_robot_position_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    robot_id = Column(String(32), ForeignKey("t_robot.id"), nullable=False)
    x = Column(DECIMAL(10, 2), nullable=False)
    y = Column(DECIMAL(10, 2), nullable=False)
    battery = Column(DECIMAL(5, 1))
    speed = Column(DECIMAL(5, 2))
    record_time = Column(DateTime, nullable=False)
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    
    robot = relationship("Robot", backref="position_history")
    
    def __repr__(self):
        return f"<RobotPositionHistory(id={self.id}, robot_id={self.robot_id})>"