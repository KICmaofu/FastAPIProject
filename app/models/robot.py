# 机器人模型
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Float, Text
from sqlalchemy.sql import func
from app.config.database import Base


class PatrolRobot(Base):
    """巡检机器人表"""
    __tablename__ = 'patrol_robot'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    robot_sn = Column(String(50), unique=True, nullable=False, comment='机器人序列号')
    robot_name = Column(String(100), nullable=False, comment='机器人名称')
    area_name = Column(String(100), comment='负责区域')
    online_status = Column(SmallInteger, default=0, comment='在线状态：0-离线 1-在线')
    battery = Column(Float, default=0, comment='电池电量百分比')
    run_mode = Column(SmallInteger, default=0, comment='运行模式：0-待机 1-自动巡检 2-手动遥控 3-充电中 4-故障')
    firmware_version = Column(String(50), comment='固件版本')
    last_upload_time = Column(DateTime, comment='最后上报时间')
    create_by = Column(String(50), comment='创建人')
    remark = Column(Text, comment='备注')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, server_default=func.now(), onupdate=func.now(), comment='更新时间')


class RobotPositionHistory(Base):
    """机器人位置历史表"""
    __tablename__ = 'robot_position_history'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    robot_sn = Column(String(50), nullable=False, index=True, comment='机器人序列号')
    patrol_record_id = Column(Integer, comment='巡检记录ID')
    position_x = Column(Float, comment='X坐标')
    position_y = Column(Float, comment='Y坐标')
    heading = Column(Float, comment='航向角度')
    map_name = Column(String(100), comment='当前地图名称')
    collect_time = Column(DateTime, server_default=func.now(), comment='采集时间')


class RobotCmdRecord(Base):
    """机器人指令记录表"""
    __tablename__ = 'robot_cmd_record'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    robot_sn = Column(String(50), nullable=False, index=True, comment='机器人序列号')
    sensor_record_id = Column(Integer, comment='关联传感器记录ID')
    cmd_code = Column(String(50), nullable=False, comment='指令编码')
    hardware_cmd = Column(String(100), comment='硬件指令')
    cmd_param = Column(String(200), comment='指令参数')
    operator = Column(String(50), comment='操作人')
    send_time = Column(DateTime, server_default=func.now(), comment='下发时间')
    response_code = Column(String(50), comment='响应码')
    response_msg = Column(Text, comment='响应消息')
    finish_time = Column(DateTime, comment='完成时间')
    cmd_status = Column(SmallInteger, default=1, comment='指令状态：1-已下发 2-执行成功 3-执行失败 4-超时')