from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.ai import AiChatRecord
from app.models.alarm import AlarmInfo
from app.utils.response import ApiResponse
from app.agent.agent import InspectionAgent
from datetime import datetime

class AiService:
    @staticmethod
    def analyze_alarm(db: Session, alarm_id: int, username: str = ""):
        alarm = db.query(AlarmInfo).filter(AlarmInfo.id == alarm_id, AlarmInfo.is_deleted == 0).first()
        if not alarm:
            return ApiResponse.not_found("告警不存在")
        
        agent = InspectionAgent(db)
        analysis = agent.analyze_alarm(alarm_id)
        
        chat_record = AiChatRecord(
            username=username,
            chat_type=2,
            user_query=f"自动分析告警ID:{alarm_id}",
            ai_answer=analysis,
            relate_alarm_id=alarm_id,
            relate_robot_sn=alarm.robot_sn
        )
        db.add(chat_record)
        db.commit()
        
        return ApiResponse.success({"analysis": analysis})
    
    @staticmethod
    def chat(db: Session, message: str, relate_alarm_id: int = None, relate_robot_sn: str = None, username: str = ""):
        agent = InspectionAgent(db)
        session_id = f"{username}_{datetime.now().strftime('%Y%m%d')}"
        answer = agent.chat(message, session_id)
        
        chat_record = AiChatRecord(
            username=username,
            chat_type=1,
            user_query=message,
            ai_answer=answer,
            relate_alarm_id=relate_alarm_id,
            relate_robot_sn=relate_robot_sn
        )
        db.add(chat_record)
        db.commit()
        
        return ApiResponse.success({"answer": answer})
    
    @staticmethod
    def get_chat_list(db: Session, username: str = "", page: int = 1, page_size: int = 20):
        query = db.query(AiChatRecord)
        if username:
            query = query.filter(AiChatRecord.username == username)
        
        total = query.count()
        records = query.order_by(desc(AiChatRecord.create_time)).offset((page - 1) * page_size).limit(page_size).all()
        
        chat_list = []
        for record in records:
            chat_list.append({
                "id": record.id,
                "user_query": record.user_query,
                "ai_answer": record.ai_answer,
                "chat_type": record.chat_type,
                "relate_alarm_id": record.relate_alarm_id,
                "relate_robot_sn": record.relate_robot_sn,
                "create_time": record.create_time.strftime("%Y-%m-%d %H:%M:%S") if record.create_time else None
            })
        
        return ApiResponse.success_pagination(chat_list, total, page, page_size)
    
    @staticmethod
    def analyze_report(db: Session, robot_sn: str = None, start_time: str = None, end_time: str = None, username: str = ""):
        agent = InspectionAgent(db)
        analysis = agent.analyze_report(robot_sn, start_time, end_time)
        
        chat_record = AiChatRecord(
            username=username,
            chat_type=3,
            user_query=f"分析报表: robot_sn={robot_sn}, startTime={start_time}, endTime={end_time}",
            ai_answer=analysis,
            relate_robot_sn=robot_sn
        )
        db.add(chat_record)
        db.commit()
        
        return ApiResponse.success({"analysis": analysis})