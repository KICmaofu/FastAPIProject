from sqlalchemy import Column, Integer, String, DateTime, Boolean, UniqueConstraint, Index
from app.config.database import Base
from datetime import datetime

class SysUser(Base):
    __tablename__ = "sys_user"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    username = Column(String(50), nullable=False, comment="登录账号")
    password = Column(String(100), nullable=False, comment="BCrypt加密密码")
    real_name = Column(String(30), nullable=False, comment="真实姓名")
    phone = Column(String(20), nullable=True, comment="联系电话")
    role = Column(Integer, nullable=False, comment="角色：1-超级管理员 2-运维员")
    status = Column(Integer, nullable=False, default=0, comment="账号状态：0-待审核/禁用 1-正常启用")
    last_login_time = Column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip = Column(String(50), default="", comment="最后登录IP地址")
    is_deleted = Column(Integer, nullable=False, default=0, comment="逻辑删除：0-未删除 1-已删除")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    __table_args__ = (
        UniqueConstraint("username", name="uk_username"),
        UniqueConstraint("phone", name="uk_phone"),
        Index("idx_role_status", "role", "status"),
        {'extend_existing': True}
    )