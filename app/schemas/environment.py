from pydantic import BaseModel, Field
from typing import Optional

class EnvironmentDataResponse(BaseModel):
    temperature: Optional[float] = Field(None, description="温度(°C)")
    humidity: Optional[float] = Field(None, description="湿度(%)")
    gas: Optional[float] = Field(None, description="可燃气体浓度(ppm)")
    pm25: Optional[float] = Field(None, description="PM2.5(μg/m³)")
    maxThermalTemp: Optional[float] = Field(None, description="热成像最高温度(°C)")
    updateTime: Optional[str] = Field(None, description="更新时间")

class EnvironmentHistoryRequest(BaseModel):
    startTime: str = Field(..., description="开始时间")
    endTime: str = Field(..., description="结束时间")
    interval: Optional[str] = Field("1m", description="时间间隔：1m/5m/15m/1h")