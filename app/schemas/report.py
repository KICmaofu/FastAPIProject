from pydantic import BaseModel, Field
from typing import Optional, List

class ReportResponse(BaseModel):
    id: str = Field(..., description="报告ID")
    type: str = Field(..., description="报告类型")
    title: str = Field(..., description="报告标题")
    content: Optional[str] = Field(None, description="报告内容")
    startTime: str = Field(..., description="统计开始")
    endTime: str = Field(..., description="统计结束")
    createTime: str = Field(..., description="创建时间")

class ReportCreate(BaseModel):
    type: str = Field(..., description="报告类型")
    startTime: str = Field(..., description="开始时间")
    endTime: str = Field(..., description="结束时间")

class ReportListRequest(BaseModel):
    type: Optional[str] = Field(None, description="报告类型")
    page: Optional[int] = Field(1, description="页码")
    size: Optional[int] = Field(20, description="每页数量")

class ReportListResponse(BaseModel):
    list: List['ReportResponse'] = Field(..., description="报告列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")

ReportListResponse.model_rebuild()