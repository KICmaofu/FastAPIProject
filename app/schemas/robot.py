# 机器人模块Schema
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RobotInfo(BaseModel):
    """机器人信息"""
    id: int = Field(..., description="机器人ID")
    robot_sn: str = Field(..., description="机器人序列号")
    robot_name: str = Field(..., description="机器人名称")
    area_name: Optional[str] = Field(None, description="负责区域")
    online_status: int = Field(0, description="在线状态：0-离线 1-在线")
    battery: float = Field(0, description="电池电量")
    run_mode: int = Field(0, description="运行模式")
    firmware_version: Optional[str] = Field(None, description="固件版本")
    last_upload_time: Optional[datetime] = Field(None, description="最后上报时间")
    create_by: Optional[str] = Field(None, description="创建人")
    remark: Optional[str] = Field(None, description="备注")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")


class RobotStatistics(BaseModel):
    """机器人统计"""
    total: int = Field(0, description="总数")
    online: int = Field(0, description="在线数")
    offline: int = Field(0, description="离线数")


class RobotAddRequest(BaseModel):
    """添加机器人请求"""
    robot_sn: str = Field(..., max_length=50, description="机器人序列号")
    robot_name: str = Field(..., max_length=100, description="机器人名称")
    area_name: Optional[str] = Field(None, max_length=100, description="负责区域")
    remark: Optional[str] = Field(None, description="备注")


class RobotUpdateRequest(BaseModel):
    """更新机器人请求"""
    id: int = Field(..., description="机器人ID")
    robot_name: Optional[str] = Field(None, max_length=100)
    area_name: Optional[str] = Field(None, max_length=100)
    remark: Optional[str] = Field(None)


class RobotDeleteRequest(BaseModel):
    """删除机器人请求"""
    id: int = Field(..., description="机器人ID")


class SendCmdRequest(BaseModel):
    """发送控制命令请求"""
    robot_sn: str = Field(..., description="机器人序列号")
    cmd_code: str = Field(..., description="指令编码")
    param: Optional[str] = Field(None, description="指令参数")


class CmdRecordInfo(BaseModel):
    """指令记录信息"""
    id: int = Field(..., description="记录ID")
    robot_sn: str = Field(..., description="机器人序列号")
    sensor_record_id: Optional[int] = Field(None, description="关联传感器记录ID")
    cmd_code: str = Field(..., description="指令编码")
    hardware_cmd: Optional[str] = Field(None, description="硬件指令")
    cmd_param: Optional[str] = Field(None, description="指令参数")
    operator: Optional[str] = Field(None, description="操作人")
    send_time: Optional[datetime] = Field(None, description="下发时间")
    response_code: Optional[str] = Field(None, description="响应码")
    response_msg: Optional[str] = Field(None, description="响应消息")
    finish_time: Optional[datetime] = Field(None, description="完成时间")
    cmd_status: int = Field(1, description="指令状态")


class SensorDataInfo(BaseModel):
    """传感器数据信息"""
    id: int = Field(..., description="数据ID")
    robot_sn: str = Field(..., description="机器人序列号")
    patrol_record_id: Optional[int] = Field(None, description="巡检记录ID")
    temperature: Optional[float] = Field(None, description="环境温度")
    humidity: Optional[float] = Field(None, description="环境湿度")
    smoke_level: Optional[float] = Field(None, description="烟雾浓度")
    max_single_temp: Optional[float] = Field(None, description="最高单点温度")
    human_detected: int = Field(0, description="是否检测到人员")
    fire_risk: int = Field(0, description="板端告警类型")
    thermal_matrix: Optional[str] = Field(None, description="热成像矩阵")
    battery: Optional[float] = Field(None, description="电池电量")
    collect_time: Optional[datetime] = Field(None, description="采集时间")