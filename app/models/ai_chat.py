# AI对话记录模型
from sqlalchemy import Column, Integer, String, DateTime, SmallInteger, Text
from sqlalchemy.sql import func
from app.config.database import Base


class AiChatRecord(Base):
    """AI对话记录表"""
    __tablename__ = 'ai_chat_record'

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    user_id = Column(Integer, nullable=False, index=True, comment='用户ID')
    user_query = Column(Text, nullable=False, comment='用户提问')
    ai_answer = Column(Text, comment='AI回答')
    chat_type = Column(SmallInteger, default=1, comment='对话类型：1-手动问答 2-告警自动分析 3-报表AI解读')
    relate_alarm_id = Column(Integer, comment='关联告警ID')
    relate_robot_sn = Column(String(50), comment='关联机器人序列号')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')