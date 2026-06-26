from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.alarm import AlarmInfo
from app.models.robot import RobotSensorRecord
from app.utils.response import ApiResponse
from datetime import datetime, timedelta

class AlarmService:
    @staticmethod
    def get_alarm_list(db: Session, page: int = 1, page_size: int = 10, alarm_level: str = None, deal_status: int = None, robot_sn: str = None, start_time: str = None, end_time: str = None):
        query = db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0)
        if alarm_level:
            query = query.filter(AlarmInfo.alarm_level == alarm_level)
        if deal_status is not None:
            query = query.filter(AlarmInfo.deal_status == deal_status)
        if robot_sn:
            query = query.filter(AlarmInfo.robot_sn == robot_sn)
        if start_time:
            query = query.filter(AlarmInfo.create_time >= start_time)
        if end_time:
            query = query.filter(AlarmInfo.create_time <= end_time)
        
        total = query.count()
        alarms = query.order_by(desc(AlarmInfo.create_time)).offset((page - 1) * page_size).limit(page_size).all()
        
        alarm_list = []
        for alarm in alarms:
            alarm_list.append({
                "id": alarm.id,
                "robot_sn": alarm.robot_sn,
                "sensor_record_id": alarm.sensor_record_id,
                "hardware_alarm_type": alarm.hardware_alarm_type,
                "alarm_type": alarm.alarm_type,
                "alarm_level": alarm.alarm_level,
                "alarm_desc": alarm.alarm_desc,
                "area_name": alarm.area_name,
                "point_name": alarm.point_name,
                "deal_status": alarm.deal_status,
                "deal_user": alarm.deal_user,
                "deal_content": alarm.deal_content,
                "deal_time": alarm.deal_time.strftime("%Y-%m-%d %H:%M:%S") if alarm.deal_time else None,
                "create_time": alarm.create_time.strftime("%Y-%m-%d %H:%M:%S") if alarm.create_time else None
            })
        
        return ApiResponse.success_pagination(alarm_list, total, page, page_size)
    
    @staticmethod
    def get_alarm_detail(db: Session, alarm_id: int):
        alarm = db.query(AlarmInfo).filter(AlarmInfo.id == alarm_id, AlarmInfo.is_deleted == 0).first()
        if not alarm:
            return ApiResponse.not_found("告警不存在")
        
        sensor_record = db.query(RobotSensorRecord).filter(RobotSensorRecord.id == alarm.sensor_record_id).first()
        
        sensor_data = {}
        if sensor_record:
            sensor_data = {
                "temperature": sensor_record.temperature,
                "humidity": sensor_record.humidity,
                "smoke_level": sensor_record.smoke_level,
                "max_single_temp": sensor_record.max_single_temp,
                "collect_time": sensor_record.collect_time.strftime("%Y-%m-%d %H:%M:%S") if sensor_record.collect_time else None
            }
        
        return ApiResponse.success({
            "id": alarm.id,
            "robot_sn": alarm.robot_sn,
            "alarm_level": alarm.alarm_level,
            "alarm_desc": alarm.alarm_desc,
            "sensor_data": sensor_data
        })
    
    @staticmethod
    def deal_alarm(db: Session, alarm_id: int, deal_content: str, deal_user: str = ""):
        alarm = db.query(AlarmInfo).filter(AlarmInfo.id == alarm_id, AlarmInfo.is_deleted == 0).first()
        if not alarm:
            return ApiResponse.not_found("告警不存在")
        
        alarm.deal_status = 1
        alarm.deal_user = deal_user
        alarm.deal_content = deal_content
        alarm.deal_time = datetime.now()
        
        db.commit()
        return ApiResponse.success(msg="告警处置成功")
    
    @staticmethod
    def delete_alarm(db: Session, alarm_id: int):
        alarm = db.query(AlarmInfo).filter(AlarmInfo.id == alarm_id, AlarmInfo.is_deleted == 0).first()
        if not alarm:
            return ApiResponse.not_found("告警不存在")
        
        alarm.is_deleted = 1
        db.commit()
        return ApiResponse.success(msg="删除告警成功")
    
    @staticmethod
    def get_alarm_statistics(db: Session):
        total = db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0).count()
        red = db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.alarm_level == "RED").count()
        orange = db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.alarm_level == "ORANGE").count()
        normal = db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.alarm_level == "NORMAL").count()
        pending = db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.deal_status == 0).count()
        dealt = db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.deal_status == 1).count()
        
        return ApiResponse.success({
            "total": total,
            "red": red,
            "orange": orange,
            "normal": normal,
            "pending": pending,
            "dealt": dealt
        })
    
    @staticmethod
    def get_recent_alarm(db: Session, limit: int = 10):
        alarms = db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0).order_by(desc(AlarmInfo.create_time)).limit(limit).all()
        
        alarm_list = []
        for alarm in alarms:
            alarm_list.append({
                "id": alarm.id,
                "robot_sn": alarm.robot_sn,
                "alarm_level": alarm.alarm_level,
                "alarm_desc": alarm.alarm_desc,
                "area_name": alarm.area_name,
                "deal_status": alarm.deal_status,
                "create_time": alarm.create_time.strftime("%Y-%m-%d %H:%M:%S") if alarm.create_time else None
            })
        
        return ApiResponse.success(alarm_list)
    
    @staticmethod
    def get_alarm_trend(db: Session, days: int = 7):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        labels = []
        level1 = []
        level2 = []
        level3 = []
        
        for i in range(days):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime("%m/%d")
            labels.append(date_str)
            
            day_start = current_date.replace(hour=0, minute=0, second=0)
            day_end = current_date.replace(hour=23, minute=59, second=59)
            
            red_count = db.query(AlarmInfo).filter(
                AlarmInfo.is_deleted == 0,
                AlarmInfo.alarm_level == "RED",
                AlarmInfo.create_time >= day_start,
                AlarmInfo.create_time <= day_end
            ).count()
            orange_count = db.query(AlarmInfo).filter(
                AlarmInfo.is_deleted == 0,
                AlarmInfo.alarm_level == "ORANGE",
                AlarmInfo.create_time >= day_start,
                AlarmInfo.create_time <= day_end
            ).count()
            normal_count = db.query(AlarmInfo).filter(
                AlarmInfo.is_deleted == 0,
                AlarmInfo.alarm_level == "NORMAL",
                AlarmInfo.create_time >= day_start,
                AlarmInfo.create_time <= day_end
            ).count()
            
            level1.append(red_count)
            level2.append(orange_count)
            level3.append(normal_count)
        
        return ApiResponse.success({
            "labels": labels,
            "level1": level1,
            "level2": level2,
            "level3": level3
        })