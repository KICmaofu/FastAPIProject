# 巡检任务和记录模型
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Text
from sqlalchemy.sql import func
from app.config.database import Base


class PatrolTask(Base):
    """巡检任务表"""
    __tablename__ = 'patrol_task'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    task_name = Column(String(100), nullable=False, comment='任务名称')
    robot_sn = Column(String(50), nullable=False, index=True, comment='机器人序列号')
    cycle_type = Column(SmallInteger, default=1, comment='周期类型：1-每日 2-工作日 3-周末 4-单次')
    start_time = Column(String(8), comment='开始时间 HH:mm:ss')
    end_time = Column(String(8), comment='结束时间 HH:mm:ss')
    route_points = Column(Text, comment='巡检点位列表JSON')
    status = Column(SmallInteger, default=1, comment='状态：0-停用 1-启用')
    create_by = Column(String(50), comment='创建人')
    remark = Column(Text, comment='备注')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class PatrolRecord(Base):
    """巡检记录表"""
    __tablename__ = 'patrol_record'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    task_id = Column(Integer, comment='任务ID')
    robot_sn = Column(String(50), nullable=False, index=True, comment='机器人序列号')
    start_time = Column(DateTime, server_default=func.now(), comment='开始时间')
    end_time = Column(DateTime, comment='结束时间')
    patrol_status = Column(SmallInteger, default=1, comment='巡检状态：1-进行中 2-已完成 3-异常中断')
    data_count = Column(Integer, default=0, comment='采集数据条数')
    alarm_count = Column(Integer, default=0, comment='产生告警数量')
    patrol_result = Column(Text, comment='巡检结果描述')
    create_by = Column(String(50), comment='创建人')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')