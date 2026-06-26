# 巡检模块Schema
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class PatrolTaskInfo(BaseModel):
    """巡检任务信息"""
    id: int = Field(..., description="任务ID")
    task_name: str = Field(..., description="任务名称")
    robot_sn: str = Field(..., description="机器人序列号")
    cycle_type: int = Field(1, description="周期类型：1-每日 2-工作日 3-周末 4-单次")
    start_time: Optional[str] = Field(None, description="开始时间 HH:mm:ss")
    end_time: Optional[str] = Field(None, description="结束时间 HH:mm:ss")
    route_points: Optional[List[Any]] = Field(None, description="巡检点位列表")
    status: int = Field(1, description="状态：0-停用 1-启用")
    create_by: Optional[str] = Field(None, description="创建人")
    remark: Optional[str] = Field(None, description="备注")
    create_time: Optional[datetime] = Field(None, description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")


class PatrolTaskStatistics(BaseModel):
    """巡检任务统计"""
    total: int = Field(0, description="总数")
    enabled: int = Field(0, description="启用数")
    disabled: int = Field(0, description="停用数")


class PatrolTaskAddRequest(BaseModel):
    """添加巡检任务请求"""
    task_name: str = Field(..., max_length=100, description="任务名称")
    robot_sn: str = Field(..., description="机器人序列号")
    cycle_type: int = Field(..., ge=1, le=4, description="周期类型")
    start_time: Optional[str] = Field(None, description="开始时间 HH:mm:ss")
    end_time: Optional[str] = Field(None, description="结束时间 HH:mm:ss")
    route_points: Optional[List[Any]] = Field(None, description="巡检点位列表")


class PatrolTaskUpdateRequest(BaseModel):
    """更新巡检任务请求"""
    id: int = Field(..., description="任务ID")
    task_name: Optional[str] = Field(None, max_length=100)
    cycle_type: Optional[int] = Field(None, ge=1, le=4)
    start_time: Optional[str] = Field(None)
    end_time: Optional[str] = Field(None)
    route_points: Optional[List[Any]] = Field(None)
    status: Optional[int] = Field(None, ge=0, le=1)


class PatrolTaskDeleteRequest(BaseModel):
    """删除巡检任务请求"""
    id: int = Field(..., description="任务ID")


class PatrolTaskStatusRequest(BaseModel):
    """更新任务状态请求"""
    id: int = Field(..., description="任务ID")
    status: int = Field(..., ge=0, le=1, description="状态：0-停用 1-启用")


class PatrolRecordInfo(BaseModel):
    """巡检记录信息"""
    id: int = Field(..., description="记录ID")
    task_id: Optional[int] = Field(None, description="任务ID")
    robot_sn: str = Field(..., description="机器人序列号")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    patrol_status: int = Field(1, description="巡检状态：1-进行中 2-已完成 3-异常中断")
    data_count: int = Field(0, description="采集数据条数")
    alarm_count: int = Field(0, description="产生告警数量")
    patrol_result: Optional[str] = Field(None, description="巡检结果")
    create_by: Optional[str] = Field(None, description="创建人")
    create_time: Optional[datetime] = Field(None, description="创建时间")


class PatrolRecordStatistics(BaseModel):
    """巡检记录统计"""
    total: int = Field(0, description="总数")
    ongoing: int = Field(0, description="进行中数")
    completed: int = Field(0, description="已完成数")
    interrupted: int = Field(0, description="异常中断数")
    total_data_count: int = Field(0, description="总数据条数")
    total_alarm_count: int = Field(0, description="总告警数")


class StartPatrolRequest(BaseModel):
    """开始巡检请求"""
    robot_sn: str = Field(..., description="机器人序列号")
    task_id: Optional[int] = Field(None, description="任务ID")


class EndPatrolRequest(BaseModel):
    """结束巡检请求"""
    id: int = Field(..., description="巡检记录ID")
    patrol_result: Optional[str] = Field(None, description="巡检结果")