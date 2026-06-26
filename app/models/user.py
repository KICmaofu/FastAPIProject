# 用户模型
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Text
from sqlalchemy.sql import func
from app.config.database import Base


class SysUser(Base):
    """系统用户表"""
    __tablename__ = 'sys_user'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    username = Column(String(50), unique=True, nullable=False, comment='登录账号')
    password = Column(String(100), nullable=False, comment='BCrypt加密密码')
    real_name = Column(String(50), nullable=False, comment='真实姓名')
    phone = Column(String(20), comment='手机号')
    role = Column(SmallInteger, default=2, comment='角色：1-超级管理员 2-运维员')
    status = Column(SmallInteger, default=1, comment='状态：0-待审核/禁用 1-正常启用')
    last_login_time = Column(DateTime, comment='最后登录时间')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')