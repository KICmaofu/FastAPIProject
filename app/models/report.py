from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid

class Report(Base):
    __tablename__ = "t_report"
    
    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    type = Column(Enum("daily", "weekly", "monthly"), nullable=False)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    creator_id = Column(String(32), ForeignKey("t_user.id"), nullable=False)
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    creator = relationship("User", backref="reports")
    
    def __repr__(self):
        return f"<Report(id={self.id}, type={self.type}, title={self.title})>"