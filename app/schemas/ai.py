from pydantic import BaseModel, Field
from typing import Optional

class AiAlarmAnalyze(BaseModel):
    alarm_id: int = Field(..., gt=0)

class AiChat(BaseModel):
    message: str = Field(...)
    relate_alarm_id: Optional[int] = None
    relate_robot_sn: Optional[str] = None

class AiReportAnalyze(BaseModel):
    robot_sn: Optional[str] = None
    startTime: Optional[str] = None
    endTime: Optional[str] = None

class AiChatRecordResponse(BaseModel):
    id: int
    user_query: str
    ai_answer: str
    chat_type: int
    relate_alarm_id: Optional[int]
    relate_robot_sn: Optional[str]
    create_time: str