# 告警模型
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Text
from sqlalchemy.sql import func
from app.config.database import Base


class PatrolAlarm(Base):
    """巡检告警表"""
    __tablename__ = 'patrol_alarm'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    robot_sn = Column(String(50), nullable=False, index=True, comment='机器人序列号')
    sensor_record_id = Column(Integer, comment='关联传感器记录ID')
    hardware_alarm_type = Column(SmallInteger, default=0, comment='板端告警类型：0-正常 1-高温无人 2-高温 3-烟雾')
    alarm_type = Column(String(50), comment='告警类型：HIGH_TEMP/SMOKE/NO_HUMAN')
    alarm_level = Column(String(20), comment='告警等级：RED/ORANGE/NORMAL')
    alarm_desc = Column(Text, comment='告警描述')
    area_name = Column(String(100), comment='区域名称')
    point_name = Column(String(100), comment='点位名称')
    deal_status = Column(SmallInteger, default=0, comment='处置状态：0-未处理 1-已处理')
    deal_user = Column(String(50), comment='处置人')
    deal_content = Column(Text, comment='处置内容')
    deal_time = Column(DateTime, comment='处置时间')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')