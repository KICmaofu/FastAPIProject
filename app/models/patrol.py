from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from app.config.database import Base
from datetime import datetime

class PatrolTask(Base):
    __tablename__ = "patrol_task"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    robot_sn = Column(String(64), nullable=False, comment="绑定机器人序列号")
    task_name = Column(String(100), nullable=False, comment="任务名称")
    cycle_type = Column(Integer, nullable=False, comment="执行周期：1-每日 2-工作日 3-周末 4-单次")
    start_time = Column(String(8), nullable=False, comment="任务开始时间 HH:mm:ss")
    end_time = Column(String(8), nullable=False, comment="任务结束时间 HH:mm:ss")
    route_points = Column(String, nullable=True, comment="巡检点位列表JSON")
    status = Column(Integer, nullable=False, default=1, comment="启用状态：0-停用 1-启用")
    create_by = Column(String(50), default="", comment="创建人账号")
    remark = Column(String(500), default="", comment="任务备注")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    
    __table_args__ = (
        Index("idx_robot_status", "robot_sn", "status"),
        {'extend_existing': True}
    )

class PatrolRecord(Base):
    __tablename__ = "patrol_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    task_id = Column(Integer, nullable=True, comment="关联定时任务ID")
    robot_sn = Column(String(64), nullable=False, comment="机器人序列号")
    patrol_status = Column(Integer, nullable=False, default=1, comment="巡检状态：1-进行中 2-已完成 3-异常中断")
    start_time = Column(DateTime, nullable=False, comment="巡检开始时间")
    end_time = Column(DateTime, nullable=True, comment="巡检结束时间")
    data_count = Column(Integer, nullable=False, default=0, comment="本次采集传感器数据条数")
    alarm_count = Column(Integer, nullable=False, default=0, comment="本次巡检产生告警数量")
    patrol_result = Column(Text, nullable=True, comment="巡检总结描述")
    create_by = Column(String(50), default="", comment="触发人")
    
    __table_args__ = (
        Index("idx_robot_start_time", "robot_sn", "start_time"),
        Index("idx_patrol_status", "patrol_status"),
        {'extend_existing': True}
    )