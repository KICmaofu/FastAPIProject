from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.robot import RobotSensorRecord
from app.models.alarm import AlarmInfo
from app.models.patrol import PatrolRecord
from app.utils.response import ApiResponse
from datetime import datetime, timedelta

class ReportService:
    @staticmethod
    def get_env_trend(db: Session, robot_sn: str = None, start_time: str = None, end_time: str = None):
        query = db.query(RobotSensorRecord)
        if robot_sn:
            query = query.filter(RobotSensorRecord.robot_sn == robot_sn)
        if start_time:
            query = query.filter(RobotSensorRecord.collect_time >= start_time)
        if end_time:
            query = query.filter(RobotSensorRecord.collect_time <= end_time)
        
        records = query.order_by(RobotSensorRecord.collect_time).all()
        
        trend_list = []
        for record in records:
            trend_list.append({
                "time": record.collect_time.strftime("%Y-%m-%d %H:%M:%S") if record.collect_time else None,
                "temperature": record.temperature,
                "humidity": record.humidity,
                "smoke_level": record.smoke_level,
                "max_single_temp": record.max_single_temp
            })
        
        return ApiResponse.success(trend_list)
    
    @staticmethod
    def get_alarm_trend(db: Session, trend_type: str = "day"):
        if trend_type == "day":
            now = datetime.now()
            start_time = now.replace(hour=0, minute=0, second=0)
            
            labels = []
            level1 = []
            level2 = []
            level3 = []
            
            for hour in range(24):
                hour_start = start_time + timedelta(hours=hour)
                hour_end = hour_start + timedelta(hours=1)
                
                labels.append(f"{hour:02d}:00")
                
                red_count = db.query(AlarmInfo).filter(
                    AlarmInfo.is_deleted == 0,
                    AlarmInfo.alarm_level == "RED",
                    AlarmInfo.create_time >= hour_start,
                    AlarmInfo.create_time < hour_end
                ).count()
                orange_count = db.query(AlarmInfo).filter(
                    AlarmInfo.is_deleted == 0,
                    AlarmInfo.alarm_level == "ORANGE",
                    AlarmInfo.create_time >= hour_start,
                    AlarmInfo.create_time < hour_end
                ).count()
                normal_count = db.query(AlarmInfo).filter(
                    AlarmInfo.is_deleted == 0,
                    AlarmInfo.alarm_level == "NORMAL",
                    AlarmInfo.create_time >= hour_start,
                    AlarmInfo.create_time < hour_end
                ).count()
                
                level1.append(red_count)
                level2.append(orange_count)
                level3.append(normal_count)
        
        else:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=6)
            
            labels = []
            level1 = []
            level2 = []
            level3 = []
            
            for i in range(7):
                current_date = start_date + timedelta(days=i)
                labels.append(current_date.strftime("%m/%d"))
                
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
    
    @staticmethod
    def get_daily_report(db: Session, start_time: str = None, end_time: str = None):
        if not start_time:
            start_time = datetime.now().replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
        if not end_time:
            end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        total_patrol = db.query(PatrolRecord).filter(
            PatrolRecord.start_time >= start_time,
            PatrolRecord.start_time <= end_time
        ).count()
        
        completed_patrol = db.query(PatrolRecord).filter(
            PatrolRecord.start_time >= start_time,
            PatrolRecord.start_time <= end_time,
            PatrolRecord.patrol_status == 2
        ).count()
        
        total_alarm = db.query(AlarmInfo).filter(
            AlarmInfo.is_deleted == 0,
            AlarmInfo.create_time >= start_time,
            AlarmInfo.create_time <= end_time
        ).count()
        
        processed_alarm = db.query(AlarmInfo).filter(
            AlarmInfo.is_deleted == 0,
            AlarmInfo.create_time >= start_time,
            AlarmInfo.create_time <= end_time,
            AlarmInfo.deal_status == 1
        ).count()
        
        sensor_result = db.query(RobotSensorRecord).filter(
            RobotSensorRecord.collect_time >= start_time,
            RobotSensorRecord.collect_time <= end_time
        ).with_entities(
            func.avg(RobotSensorRecord.temperature).label("avg_temp"),
            func.avg(RobotSensorRecord.humidity).label("avg_humidity"),
            func.max(RobotSensorRecord.temperature).label("max_temp")
        ).first()
        
        avg_temp = 0.0
        avg_humidity = 0.0
        max_temp = 0.0
        
        if sensor_result:
            avg_temp = round(float(sensor_result.avg_temp), 2) if sensor_result.avg_temp else 0.0
            avg_humidity = round(float(sensor_result.avg_humidity), 2) if sensor_result.avg_humidity else 0.0
            max_temp = round(float(sensor_result.max_temp), 2) if sensor_result.max_temp else 0.0
        
        return ApiResponse.success({
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_patrol": total_patrol,
            "completed_patrol": completed_patrol,
            "total_alarm": total_alarm,
            "processed_alarm": processed_alarm,
            "avg_temperature": avg_temp,
            "avg_humidity": avg_humidity,
            "max_temperature": max_temp
        })