from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from app.config.database import Base
from datetime import datetime

class AiChatRecord(Base):
    __tablename__ = "ai_chat_record"
    
    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    username = Column(String(50), nullable=False, comment="提问/操作人账号")
    chat_type = Column(Integer, nullable=False, default=1, comment="对话类型：1-手动问答 2-告警自动分析 3-报表AI解读")
    sensor_record_id = Column(Integer, nullable=True, comment="关联核心表ID")
    user_query = Column(Text, nullable=False, comment="用户提问文本")
    ai_answer = Column(Text, nullable=False, comment="AI生成的分析与整改建议")
    relate_alarm_id = Column(Integer, nullable=True, comment="关联告警ID")
    relate_robot_sn = Column(String(64), nullable=True, comment="关联机器人序列号")
    tokens_used = Column(Integer, default=0, comment="消耗Token数量")
    create_time = Column(DateTime, nullable=False, default=datetime.now, comment="创建时间")
    
    __table_args__ = (
        Index("idx_user_create_time", "username", "create_time"),
        Index("idx_relate_alarm", "relate_alarm_id"),
        Index("idx_relate_sensor", "sensor_record_id"),
        {'extend_existing': True}
    )