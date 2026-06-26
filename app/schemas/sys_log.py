from pydantic import BaseModel
from typing import Optional

class SysLogResponse(BaseModel):
    id: int
    username: str
    module: str
    operation: str
    ip_address: str
    detail: Optional[str]
    create_time: str