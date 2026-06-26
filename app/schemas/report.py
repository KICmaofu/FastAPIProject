from pydantic import BaseModel
from typing import Optional

class EnvTrendResponse(BaseModel):
    time: str
    temperature: float
    humidity: float
    smoke_level: float
    max_single_temp: float

class AlarmTrendResponse(BaseModel):
    labels: list
    level1: list
    level2: list
    level3: list

class DailyReportResponse(BaseModel):
    date: str
    total_patrol: int
    completed_patrol: int
    total_alarm: int
    processed_alarm: int
    avg_temperature: float
    avg_humidity: float
    max_temperature: float