from pydantic import BaseModel, Field
from typing import Optional, List

class ThermalDataResponse(BaseModel):
    maxTemp: List[List[float]] = Field(..., description="8x8温度矩阵")
    temperature: float = Field(..., description="环境温度(°C)")
    humidity: float = Field(..., description="湿度(%)")
    gas: float = Field(..., description="可燃气体浓度(ppm)")
    battery: float = Field(..., description="电量(%)")
    humanDetected: bool = Field(..., description="是否检测到人")

class ThermalDataHistoryRequest(BaseModel):
    startTime: str = Field(..., description="开始时间(ISO格式)")
    endTime: str = Field(..., description="结束时间(ISO格式)")
    page: Optional[int] = Field(1, description="页码")
    size: Optional[int] = Field(100, description="每页数量")