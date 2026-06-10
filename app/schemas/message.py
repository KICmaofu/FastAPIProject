from pydantic import BaseModel, Field
from typing import Optional, List

class MessageResponse(BaseModel):
    id: str = Field(..., description="消息ID")
    title: str = Field(..., description="标题")
    content: Optional[str] = Field(None, description="内容")
    type: Optional[str] = Field(None, description="类型")
    time: str = Field(..., description="时间")
    unread: bool = Field(..., description="是否已读")

class MessageListRequest(BaseModel):
    type: Optional[str] = Field(None, description="消息类型")
    page: Optional[int] = Field(1, description="页码")
    size: Optional[int] = Field(20, description="每页数量")

class MessageListResponse(BaseModel):
    list: List['MessageResponse'] = Field(..., description="消息列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")

MessageListResponse.model_rebuild()