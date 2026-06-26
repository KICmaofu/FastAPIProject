# 系统日志模型
from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from app.config.database import Base


class SysLog(Base):
    """系统操作审计日志表"""
    __tablename__ = 'sys_log'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    username = Column(String(50), index=True, comment='操作用户')
    module = Column(String(50), comment='操作模块')
    operation = Column(String(100), comment='操作类型')
    ip_address = Column(String(50), comment='IP地址')
    detail = Column(Text, comment='操作详情')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')