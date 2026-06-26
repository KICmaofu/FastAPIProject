from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from app.config.database import Base
from datetime import datetime

class SysLog(Base):
    __tablename__ = "sys_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    username = Column(String(50), nullable=False, comment="操作人账号")
    module = Column(String(50), default="", comment="操作模块")
    operation = Column(String(200), nullable=False, comment="操作内容简述")
    ip_address = Column(String(50), nullable=False, comment="操作IP地址")
    detail = Column(Text, nullable=True, comment="操作详情JSON")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="操作时间")
    
    __table_args__ = (
        Index("idx_user_create_time", "username", "create_time"),
        Index("idx_module", "module"),
        {'extend_existing': True}
    )