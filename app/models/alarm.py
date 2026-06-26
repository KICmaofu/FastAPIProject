from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, UniqueConstraint, Index
from app.config.database import Base
from datetime import datetime

class AlarmInfo(Base):
    __tablename__ = "alarm_info"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    robot_sn = Column(String(64), nullable=False, comment="产生告警的机器人")
    sensor_record_id = Column(Integer, nullable=False, comment="关联核心表ID")
    hardware_alarm_type = Column(Integer, nullable=False, comment="硬件原始告警类型")
    alarm_type = Column(String(30), nullable=False, comment="告警类型")
    alarm_level = Column(String(16), nullable=False, comment="告警等级")
    alarm_desc = Column(String(500), nullable=False, comment="告警描述")
    area_name = Column(String(100), nullable=False, comment="发生区域")
    point_name = Column(String(100), default="", comment="点位名称")
    deal_status = Column(Integer, nullable=False, default=0, comment="处置状态：0-未处理 1-已处理")
    deal_user = Column(String(30), default="", comment="处置人账号")
    deal_content = Column(Text, nullable=True, comment="处置说明")
    deal_time = Column(DateTime, nullable=True, comment="处置完成时间")
    is_deleted = Column(Integer, nullable=False, default=0, comment="逻辑删除")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="告警产生时间")
    
    __table_args__ = (
        UniqueConstraint("sensor_record_id", name="uk_sensor_record_id"),
        Index("idx_deal_level_create", "deal_status", "alarm_level", "create_time"),
        Index("idx_robot_create_time", "robot_sn", "create_time"),
        {'extend_existing': True}
    )