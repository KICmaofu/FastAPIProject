from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Text, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base

class SystemLog(Base):
    __tablename__ = "t_system_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    level = Column(Enum("info", "warn", "error"), nullable=False)
    module = Column(String(50))
    content = Column(Text)
    user_id = Column(String(32), ForeignKey("t_user.id"))
    ip_address = Column(String(50))
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    
    user = relationship("User", backref="system_logs")
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level={self.level}, module={self.module})>"