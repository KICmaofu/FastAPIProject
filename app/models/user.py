from sqlalchemy import Column, String, DateTime, Boolean, Enum
from sqlalchemy.sql import func
from app.config.database import Base
import uuid

class User(Base):
    __tablename__ = "t_user"
    
    id = Column(String(32), primary_key=True, default=lambda: str(uuid.uuid4()).replace("-", ""))
    username = Column(String(50), nullable=False, unique=True)
    phone = Column(String(20), unique=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum("admin", "operator", "viewer"), nullable=False)
    status = Column(Boolean, nullable=False, default=True)
    create_time = Column(DateTime, nullable=False, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"