from pydantic import BaseModel, Field
from typing import Optional

class AlarmDeal(BaseModel):
    id: int = Field(..., gt=0)
    deal_content: str = Field(...)

class AlarmDelete(BaseModel):
    id: int = Field(..., gt=0)

class AlarmResponse(BaseModel):
    id: int
    robot_sn: str
    sensor_record_id: int
    hardware_alarm_type: int
    alarm_type: str
    alarm_level: str
    alarm_desc: str
    area_name: str
    point_name: str
    deal_status: int
    deal_user: str
    deal_content: Optional[str]
    deal_time: Optional[str]
    create_time: str

class AlarmDetailResponse(BaseModel):
    id: int
    robot_sn: str
    alarm_level: str
    alarm_desc: str
    sensor_data: dict

class AlarmStatisticsResponse(BaseModel):
    total: int
    red: int
    orange: int
    normal: int
    pending: int
    dealt: int

class AlarmTrendResponse(BaseModel):
    labels: list
    level1: list
    level2: list
    level3: list