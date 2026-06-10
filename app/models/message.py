from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.config.database import Base
import uuid

class Message(Base):
    __tablename__ = "t_message"
    
    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    title = Column(String(200), nullable=False)
    content = Column(Text)
    type = Column(String(50))
    receiver_id = Column(String(32), ForeignKey("t_user.id"), nullable=False)
    is_read = Column(Boolean, nullable=False, default=False)
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    receiver = relationship("User", backref="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, title={self.title})>"