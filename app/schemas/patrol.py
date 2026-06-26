from pydantic import BaseModel, Field
from typing import Optional, List

class PatrolTaskAdd(BaseModel):
    task_name: str = Field(..., max_length=100)
    robot_sn: str = Field(..., max_length=64)
    cycle_type: int = Field(..., ge=1, le=4)
    start_time: str = Field(..., max_length=8)
    end_time: str = Field(..., max_length=8)
    route_points: Optional[List] = None

class PatrolTaskUpdate(BaseModel):
    id: int = Field(..., gt=0)
    task_name: Optional[str] = Field(None, max_length=100)
    cycle_type: Optional[int] = Field(None, ge=1, le=4)
    start_time: Optional[str] = Field(None, max_length=8)
    end_time: Optional[str] = Field(None, max_length=8)
    route_points: Optional[List] = None
    status: Optional[int] = Field(None, ge=0, le=1)

class PatrolTaskUpdateStatus(BaseModel):
    id: int = Field(..., gt=0)
    status: int = Field(..., ge=0, le=1)

class PatrolTaskDelete(BaseModel):
    id: int = Field(..., gt=0)

class PatrolTaskResponse(BaseModel):
    id: int
    task_name: str
    robot_sn: str
    cycle_type: int
    start_time: str
    end_time: str
    route_points: Optional[str]
    status: int
    create_by: str
    remark: str
    create_time: str
    update_time: str

class PatrolTaskStatisticsResponse(BaseModel):
    total: int
    enabled: int
    disabled: int

class PatrolRecordResponse(BaseModel):
    id: int
    task_id: Optional[int]
    robot_sn: str
    start_time: str
    end_time: Optional[str]
    patrol_status: int
    data_count: int
    alarm_count: int
    patrol_result: Optional[str]
    create_by: str
    create_time: str

class PatrolRecordStatisticsResponse(BaseModel):
    total: int
    ongoing: int
    completed: int
    interrupted: int
    total_data_count: int
    total_alarm_count: int

class PatrolStart(BaseModel):
    robot_sn: str = Field(..., max_length=64)
    task_id: Optional[int] = None

class PatrolEnd(BaseModel):
    id: int = Field(..., gt=0)
    patrol_result: Optional[str] = None