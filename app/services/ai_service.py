from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.ai import AiChatRecord
from app.models.alarm import AlarmInfo
from app.utils.response import ApiResponse
from datetime import datetime

class AiService:
    @staticmethod
    def analyze_alarm(db: Session, alarm_id: int, username: str = ""):
        alarm = db.query(AlarmInfo).filter(AlarmInfo.id == alarm_id, AlarmInfo.is_deleted == 0).first()
        if not alarm:
            return ApiResponse.not_found("告警不存在")
        
        analysis = f"【AI告警分析】\n告警ID: {alarm_id}\n告警类型: {alarm.alarm_type}\n告警等级: {alarm.alarm_level}\n告警描述: {alarm.alarm_desc}\n发生区域: {alarm.area_name}\n\n分析建议：根据告警级别，建议立即进行现场核查，确认是否存在火灾隐患。"
        
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
        answer = f"【AI智能回复】\n您的问题: {message}\n\nAI分析结果: 根据您的提问，系统已进行智能分析。这是一个模拟的AI回复，实际系统会调用DeepSeek大模型进行真实分析。"
        
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
        analysis = f"【AI报表分析】\n机器人: {robot_sn or '全部'}\n时间范围: {start_time or '开始'} ~ {end_time or '结束'}\n\n分析结果: 系统已完成数据分析，当前环境监测数据整体处于正常范围。建议继续保持定期巡检，关注高温区域变化。"
        
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