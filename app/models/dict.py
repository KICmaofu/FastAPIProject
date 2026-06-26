# 系统字典模型
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger
from sqlalchemy.sql import func
from app.config.database import Base


class SysDictType(Base):
    """系统字典类型表"""
    __tablename__ = 'sys_dict_type'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    dict_code = Column(String(64), unique=True, nullable=False, comment='字典类型编码')
    dict_name = Column(String(100), nullable=False, comment='字典类型名称')
    remark = Column(String(200), default='', comment='备注说明')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class SysDictItem(Base):
    """系统字典项表"""
    __tablename__ = 'sys_dict_item'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    dict_code = Column(String(64), nullable=False, index=True, comment='所属字典类型编码')
    item_value = Column(String(64), nullable=False, comment='字典项值')
    item_label = Column(String(100), nullable=False, comment='字典项显示名称')
    sort = Column(Integer, default=0, comment='排序号')
    status = Column(SmallInteger, default=1, comment='状态：0-禁用 1-启用')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')