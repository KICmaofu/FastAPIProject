from pydantic import BaseModel, Field
from typing import Optional, List, Any

class AIPredictionRequest(BaseModel):
    hours: int = Field(..., description="预测时长(小时)")

class AIPredictionItem(BaseModel):
    time: str = Field(..., description="预测时间")
    temperature: Optional[float] = Field(None, description="预测温度")
    humidity: Optional[float] = Field(None, description="预测湿度")
    riskLevel: str = Field(..., description="风险等级")

class AIPredictionResponse(BaseModel):
    predictions: List[AIPredictionItem] = Field(..., description="预测数据列表")

class AIDeviceFailureRequest(BaseModel):
    deviceId: str = Field(..., description="设备ID")

class AIDetectRequest(BaseModel):
    data: List[dict] = Field(..., description="待检测数据")

class AIQueryRequest(BaseModel):
    query: str = Field(..., description="查询语句")

class AIReportRequest(BaseModel):
    type: str = Field(..., description="报告类型：daily/weekly/monthly")
    startTime: Optional[str] = Field(None, description="开始时间")
    endTime: Optional[str] = Field(None, description="结束时间")