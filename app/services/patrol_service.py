from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.patrol import PatrolTask, PatrolRecord
from app.models.robot import Robot
from app.utils.response import ApiResponse
from datetime import datetime
import json

class PatrolService:
    @staticmethod
    def get_task_list(db: Session, page: int = 1, page_size: int = 10, robot_sn: str = None):
        query = db.query(PatrolTask)
        if robot_sn:
            query = query.filter(PatrolTask.robot_sn == robot_sn)
        
        total = query.count()
        tasks = query.order_by(desc(PatrolTask.create_time)).offset((page - 1) * page_size).limit(page_size).all()
        
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
                "task_name": task.task_name,
                "robot_sn": task.robot_sn,
                "cycle_type": task.cycle_type,
                "start_time": str(task.start_time) if task.start_time else None,
                "end_time": str(task.end_time) if task.end_time else None,
                "route_points": task.route_points,
                "status": task.status,
                "create_by": task.create_by,
                "remark": task.remark,
                "create_time": task.create_time.strftime("%Y-%m-%d %H:%M:%S") if task.create_time else None,
                "update_time": task.update_time.strftime("%Y-%m-%d %H:%M:%S") if task.update_time else None
            })
        
        return ApiResponse.success_pagination(task_list, total, page, page_size)
    
    @staticmethod
    def get_task_statistics(db: Session):
        total = db.query(PatrolTask).count()
        enabled = db.query(PatrolTask).filter(PatrolTask.status == 1).count()
        disabled = total - enabled
        
        return ApiResponse.success({
            "total": total,
            "total_task": total,
            "enabled": enabled,
            "completed_task": enabled,
            "disabled": disabled
        })
    
    @staticmethod
    def add_task(db: Session, task_name: str, robot_sn: str, cycle_type: int, start_time: str, end_time: str, route_points: list = None, create_by: str = ""):
        robot = db.query(Robot).filter(Robot.robot_sn == robot_sn, Robot.is_deleted == 0).first()
        if not robot:
            return ApiResponse.not_found("机器人不存在")
        
        route_points_json = json.dumps(route_points) if route_points else None
        
        new_task = PatrolTask(
            task_name=task_name,
            robot_sn=robot_sn,
            cycle_type=cycle_type,
            start_time=start_time,
            end_time=end_time,
            route_points=route_points_json,
            create_by=create_by
        )
        db.add(new_task)
        db.commit()
        db.refresh(new_task)
        return ApiResponse.success(msg="添加巡检任务成功")
    
    @staticmethod
    def update_task(db: Session, task_id: int, task_name: str = None, cycle_type: int = None, start_time: str = None, end_time: str = None, route_points: list = None, status: int = None):
        task = db.query(PatrolTask).filter(PatrolTask.id == task_id).first()
        if not task:
            return ApiResponse.not_found("巡检任务不存在")
        
        if task_name:
            task.task_name = task_name
        if cycle_type is not None:
            task.cycle_type = cycle_type
        if start_time:
            task.start_time = start_time
        if end_time:
            task.end_time = end_time
        if route_points is not None:
            task.route_points = json.dumps(route_points)
        if status is not None:
            task.status = status
        
        db.commit()
        return ApiResponse.success(msg="更新巡检任务成功")
    
    @staticmethod
    def update_task_status(db: Session, task_id: int, status: int):
        task = db.query(PatrolTask).filter(PatrolTask.id == task_id).first()
        if not task:
            return ApiResponse.not_found("巡检任务不存在")
        
        task.status = status
        db.commit()
        return ApiResponse.success(msg="更新任务状态成功")
    
    @staticmethod
    def delete_task(db: Session, task_id: int):
        task = db.query(PatrolTask).filter(PatrolTask.id == task_id).first()
        if not task:
            return ApiResponse.not_found("巡检任务不存在")
        
        db.delete(task)
        db.commit()
        return ApiResponse.success(msg="删除巡检任务成功")
    
    @staticmethod
    def get_record_list(db: Session, page: int = 1, page_size: int = 10, robot_sn: str = None, start_time: str = None, end_time: str = None):
        query = db.query(PatrolRecord)
        if robot_sn:
            query = query.filter(PatrolRecord.robot_sn == robot_sn)
        if start_time:
            query = query.filter(PatrolRecord.start_time >= start_time)
        if end_time:
            query = query.filter(PatrolRecord.start_time <= end_time)
        
        total = query.count()
        records = query.order_by(desc(PatrolRecord.start_time)).offset((page - 1) * page_size).limit(page_size).all()
        
        record_list = []
        for record in records:
            record_list.append({
                "id": record.id,
                "task_id": record.task_id,
                "robot_sn": record.robot_sn,
                "start_time": record.start_time.strftime("%Y-%m-%d %H:%M:%S") if record.start_time else None,
                "end_time": record.end_time.strftime("%Y-%m-%d %H:%M:%S") if record.end_time else None,
                "patrol_status": record.patrol_status,
                "data_count": record.data_count,
                "alarm_count": record.alarm_count,
                "patrol_result": record.patrol_result,
                "create_by": record.create_by,
                "create_time": record.start_time.strftime("%Y-%m-%d %H:%M:%S") if record.start_time else None
            })
        
        return ApiResponse.success_pagination(record_list, total, page, page_size)
    
    @staticmethod
    def get_record_detail(db: Session, record_id: int):
        record = db.query(PatrolRecord).filter(PatrolRecord.id == record_id).first()
        if not record:
            return ApiResponse.not_found("巡检记录不存在")
        
        return ApiResponse.success({
            "id": record.id,
            "task_id": record.task_id,
            "robot_sn": record.robot_sn,
            "start_time": record.start_time.strftime("%Y-%m-%d %H:%M:%S") if record.start_time else None,
            "end_time": record.end_time.strftime("%Y-%m-%d %H:%M:%S") if record.end_time else None,
            "patrol_status": record.patrol_status,
            "data_count": record.data_count,
            "alarm_count": record.alarm_count,
            "patrol_result": record.patrol_result,
            "create_by": record.create_by,
            "create_time": record.start_time.strftime("%Y-%m-%d %H:%M:%S") if record.start_time else None
        })
    
    @staticmethod
    def get_record_statistics(db: Session, start_time: str = None, end_time: str = None):
        query = db.query(PatrolRecord)
        if start_time:
            query = query.filter(PatrolRecord.start_time >= start_time)
        if end_time:
            query = query.filter(PatrolRecord.start_time <= end_time)
        
        total = query.count()
        ongoing = query.filter(PatrolRecord.patrol_status == 1).count()
        completed = query.filter(PatrolRecord.patrol_status == 2).count()
        interrupted = query.filter(PatrolRecord.patrol_status == 3).count()
        
        result = query.with_entities(
            func.sum(PatrolRecord.data_count).label("total_data_count"),
            func.sum(PatrolRecord.alarm_count).label("total_alarm_count")
        ).first()
        
        total_data_count = int(result.total_data_count) if result and result.total_data_count else 0
        total_alarm_count = int(result.total_alarm_count) if result and result.total_alarm_count else 0
        
        return ApiResponse.success({
            "total": total,
            "total_record": total,
            "ongoing": ongoing,
            "completed": completed,
            "completed_record": completed,
            "interrupted": interrupted,
            "total_data_count": total_data_count,
            "total_alarm_count": total_alarm_count
        })
    
    @staticmethod
    def start_patrol(db: Session, robot_sn: str, task_id: int = None, create_by: str = ""):
        robot = db.query(Robot).filter(Robot.robot_sn == robot_sn, Robot.is_deleted == 0).first()
        if not robot:
            return ApiResponse.not_found("机器人不存在")
        
        if task_id:
            task = db.query(PatrolTask).filter(PatrolTask.id == task_id).first()
            if not task:
                return ApiResponse.not_found("巡检任务不存在")
        
        new_record = PatrolRecord(
            task_id=task_id,
            robot_sn=robot_sn,
            patrol_status=1,
            start_time=datetime.now(),
            create_by=create_by
        )
        db.add(new_record)
        db.commit()
        db.refresh(new_record)
        
        return ApiResponse.success({"record_id": new_record.id}, msg="巡检开始成功")
    
    @staticmethod
    def end_patrol(db: Session, record_id: int, patrol_result: str = None):
        record = db.query(PatrolRecord).filter(PatrolRecord.id == record_id, PatrolRecord.patrol_status == 1).first()
        if not record:
            return ApiResponse.not_found("巡检记录不存在或已结束")
        
        record.patrol_status = 2
        record.end_time = datetime.now()
        if patrol_result:
            record.patrol_result = patrol_result
        
        db.commit()
        return ApiResponse.success(msg="巡检结束成功")