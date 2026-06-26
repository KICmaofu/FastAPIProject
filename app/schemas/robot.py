from pydantic import BaseModel, Field
from typing import Optional, List

class RobotAdd(BaseModel):
    robot_sn: str = Field(..., max_length=64)
    robot_name: str = Field(..., max_length=100)
    area_name: str = Field(..., max_length=100)
    remark: Optional[str] = None

class RobotUpdate(BaseModel):
    id: int = Field(..., gt=0)
    robot_name: Optional[str] = Field(None, max_length=100)
    area_name: Optional[str] = Field(None, max_length=100)
    remark: Optional[str] = None

class RobotDelete(BaseModel):
    id: int = Field(..., gt=0)

class RobotSendCmd(BaseModel):
    robot_sn: str = Field(..., max_length=64)
    cmd_code: str = Field(..., max_length=32)
    param: Optional[str] = None

class RobotResponse(BaseModel):
    id: int
    robot_sn: str
    robot_name: str
    area_name: str
    online_status: int
    battery: float
    run_mode: int
    firmware_version: str
    last_upload_time: Optional[str]
    create_by: str
    remark: str
    create_time: str
    update_time: str

class RobotStatisticsResponse(BaseModel):
    total: int
    online: int
    offline: int

class RobotCmdRecordResponse(BaseModel):
    id: int
    robot_sn: str
    sensor_record_id: Optional[int]
    cmd_code: str
    hardware_cmd: str
    cmd_param: str
    operator: str
    send_time: str
    response_code: Optional[int]
    response_msg: str
    finish_time: Optional[str]
    cmd_status: int

class RobotSensorRecordResponse(BaseModel):
    id: int
    robot_sn: str
    patrol_record_id: Optional[int]
    temperature: float
    humidity: float
    smoke_level: float
    max_single_temp: float
    human_detected: int
    fire_risk: int
    thermal_matrix: str
    battery: float
    collect_time: str