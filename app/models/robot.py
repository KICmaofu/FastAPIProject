from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, UniqueConstraint, Index
from app.config.database import Base
from datetime import datetime

class Robot(Base):
    __tablename__ = "robot"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    robot_sn = Column(String(64), nullable=False, comment="机器人唯一序列号")
    robot_name = Column(String(100), default="", comment="机器人名称")
    area_name = Column(String(100), nullable=False, comment="负责巡检区域")
    battery = Column(Float, default=0, comment="当前电量 0-100%")
    online_status = Column(Integer, nullable=False, default=0, comment="在线状态：0-离线 1-在线")
    run_mode = Column(Integer, nullable=False, default=0, comment="运行模式：0-待机 1-自动巡检 2-手动遥控 3-充电中 4-故障")
    firmware_version = Column(String(32), default="", comment="固件版本号")
    last_upload_time = Column(DateTime, nullable=True, comment="最后数据上报时间")
    create_by = Column(String(50), default="", comment="创建人账号")
    remark = Column(String(500), default="", comment="备注说明")
    is_deleted = Column(Integer, nullable=False, default=0, comment="逻辑删除：0-未删除 1-已删除")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="入库时间")
    update_time = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now, comment="最后更新时间")
    
    __table_args__ = (
        UniqueConstraint("robot_sn", name="uk_robot_sn"),
        Index("idx_area", "area_name"),
        Index("idx_online_status", "online_status"),
        {'extend_existing': True}
    )

class RobotSensorRecord(Base):
    __tablename__ = "robot_sensor_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    robot_sn = Column(String(64), nullable=False, comment="机器人序列号")
    patrol_record_id = Column(Integer, nullable=True, comment="关联巡检记录ID")
    temperature = Column(Float, nullable=False, comment="环境温度（℃）")
    humidity = Column(Float, nullable=False, comment="环境湿度（%RH）")
    smoke_level = Column(Float, nullable=False, comment="烟雾浓度（PPM）")
    max_single_temp = Column(Float, nullable=False, comment="热成像画面最高温度（℃）")
    human_detected = Column(Integer, nullable=False, comment="人体检测：0-无人 1-有人")
    fire_risk = Column(Integer, nullable=False, comment="板端告警类型")
    thermal_matrix = Column(String, nullable=False, comment="8×8热成像温度矩阵JSON")
    battery = Column(Float, nullable=False, comment="上报时刻机器人电量（%）")
    collect_time = Column(DateTime, nullable=False, default=datetime.now, comment="数据采集时间")
    
    __table_args__ = (
        Index("idx_robot_collect_time", "robot_sn", "collect_time"),
        Index("idx_patrol_collect_time", "patrol_record_id", "collect_time"),
        Index("idx_robot_risk_time", "robot_sn", "fire_risk", "collect_time"),
        {'extend_existing': True}
    )

class RobotCmdRecord(Base):
    __tablename__ = "robot_cmd_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    robot_sn = Column(String(64), nullable=False, comment="目标机器人序列号")
    sensor_record_id = Column(Integer, nullable=True, comment="关联核心表ID")
    cmd_code = Column(String(32), nullable=False, comment="业务指令编码")
    hardware_cmd = Column(String(1), default="", comment="下发硬件单字符指令")
    cmd_param = Column(String(500), default="", comment="指令附加参数JSON")
    operator = Column(String(50), nullable=False, comment="下发操作人账号")
    send_time = Column(DateTime, nullable=False, default=datetime.now, comment="指令下发时间")
    response_code = Column(Integer, nullable=True, comment="机器人回执码")
    response_msg = Column(String(200), default="", comment="回执描述")
    finish_time = Column(DateTime, nullable=True, comment="指令执行完成时间")
    cmd_status = Column(Integer, nullable=False, default=1, comment="指令状态：1-已下发 2-执行成功 3-执行失败 4-超时")
    
    __table_args__ = (
        Index("idx_robot_sn", "robot_sn"),
        Index("idx_send_time", "send_time"),
        Index("idx_sensor_record_id", "sensor_record_id"),
        {'extend_existing': True}
    )