# 传感器数据模型
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Float, Text
from sqlalchemy.sql import func
from app.config.database import Base


class PatrolSensorData(Base):
    """巡检传感器数据表"""
    __tablename__ = 'patrol_sensor_data'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    robot_sn = Column(String(50), nullable=False, index=True, comment='机器人序列号')
    patrol_record_id = Column(Integer, comment='巡检记录ID')
    temperature = Column(Float, comment='环境温度')
    humidity = Column(Float, comment='湿度')
    smoke_level = Column(SmallInteger, default=0, comment='烟雾等级')
    max_single_temp = Column(Float, comment='最大单点温度')
    human_detected = Column(SmallInteger, default=0, comment='是否检测到人员：0-无 1-有')
    fire_risk = Column(SmallInteger, default=0, comment='板端火险判断：0-正常 1-高温无人 2-高温 3-烟雾')
    thermal_matrix = Column(Text, comment='热成像矩阵数据JSON')
    battery = Column(Float, comment='电池电量')
    collect_time = Column(DateTime, server_default=func.now(), comment='数据采集时间')


class PatrolThermalData(Base):
    """巡检热成像数据表"""
    __tablename__ = 'patrol_thermal_data'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    robot_sn = Column(String(50), nullable=False, index=True, comment='机器人序列号')
    patrol_record_id = Column(Integer, comment='巡检记录ID')
    thermal_image = Column(Text, comment='热成像图像数据')
    thermal_matrix = Column(Text, comment='热成像矩阵数据')
    max_temp = Column(Float, comment='最高温度')
    avg_temp = Column(Float, comment='平均温度')
    min_temp = Column(Float, comment='最低温度')
    collect_time = Column(DateTime, server_default=func.now(), comment='采集时间')