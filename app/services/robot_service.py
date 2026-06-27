from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.robot import Robot, RobotSensorRecord, RobotCmdRecord
from app.utils.response import ApiResponse
from app.services.sys_log_service import SysLogService
from datetime import datetime

class RobotService:
    @staticmethod
    def get_robot_list(db: Session):
        robots = db.query(Robot).filter(Robot.is_deleted == 0).all()
        
        robot_list = []
        for robot in robots:
            robot_list.append({
                "id": robot.id,
                "robot_sn": robot.robot_sn,
                "robot_name": robot.robot_name,
                "area_name": robot.area_name,
                "online_status": robot.online_status,
                "battery": robot.battery,
                "run_mode": robot.run_mode,
                "firmware_version": robot.firmware_version,
                "last_upload_time": robot.last_upload_time.strftime("%Y-%m-%d %H:%M:%S") if robot.last_upload_time else None,
                "create_by": robot.create_by,
                "remark": robot.remark,
                "create_time": robot.create_time.strftime("%Y-%m-%d %H:%M:%S") if robot.create_time else None,
                "update_time": robot.update_time.strftime("%Y-%m-%d %H:%M:%S") if robot.update_time else None
            })
        
        return ApiResponse.success(robot_list)
    
    @staticmethod
    def get_robot_detail(db: Session, robot_id: int):
        robot = db.query(Robot).filter(Robot.id == robot_id, Robot.is_deleted == 0).first()
        if not robot:
            return ApiResponse.not_found("机器人不存在")
        
        return ApiResponse.success({
            "id": robot.id,
            "robot_sn": robot.robot_sn,
            "robot_name": robot.robot_name,
            "area_name": robot.area_name,
            "online_status": robot.online_status,
            "battery": robot.battery,
            "run_mode": robot.run_mode,
            "firmware_version": robot.firmware_version,
            "last_upload_time": robot.last_upload_time.strftime("%Y-%m-%d %H:%M:%S") if robot.last_upload_time else None,
            "create_by": robot.create_by,
            "remark": robot.remark,
            "create_time": robot.create_time.strftime("%Y-%m-%d %H:%M:%S") if robot.create_time else None,
            "update_time": robot.update_time.strftime("%Y-%m-%d %H:%M:%S") if robot.update_time else None
        })
    
    @staticmethod
    def get_robot_by_sn(db: Session, robot_sn: str):
        robot = db.query(Robot).filter(Robot.robot_sn == robot_sn, Robot.is_deleted == 0).first()
        if not robot:
            return ApiResponse.not_found("机器人不存在")
        
        return ApiResponse.success({
            "id": robot.id,
            "robot_sn": robot.robot_sn,
            "robot_name": robot.robot_name,
            "area_name": robot.area_name,
            "online_status": robot.online_status,
            "battery": robot.battery,
            "run_mode": robot.run_mode,
            "firmware_version": robot.firmware_version,
            "last_upload_time": robot.last_upload_time.strftime("%Y-%m-%d %H:%M:%S") if robot.last_upload_time else None,
            "create_by": robot.create_by,
            "remark": robot.remark,
            "create_time": robot.create_time.strftime("%Y-%m-%d %H:%M:%S") if robot.create_time else None,
            "update_time": robot.update_time.strftime("%Y-%m-%d %H:%M:%S") if robot.update_time else None
        })
    
    @staticmethod
    def get_robot_statistics(db: Session):
        total = db.query(Robot).filter(Robot.is_deleted == 0).count()
        online = db.query(Robot).filter(Robot.is_deleted == 0, Robot.online_status == 1).count()
        offline = total - online
        
        return ApiResponse.success({"total": total, "online": online, "offline": offline})
    
    @staticmethod
    def add_robot(db: Session, robot_sn: str, robot_name: str, area_name: str, remark: str = None, create_by: str = ""):
        existing_robot = db.query(Robot).filter(Robot.robot_sn == robot_sn).first()
        if existing_robot:
            return ApiResponse.error(400, "机器人序列号已存在")
        
        new_robot = Robot(
            robot_sn=robot_sn,
            robot_name=robot_name,
            area_name=area_name,
            remark=remark or "",
            create_by=create_by
        )
        db.add(new_robot)
        db.commit()
        db.refresh(new_robot)
        SysLogService.add_log(db, create_by, "机器人", f"添加机器人: {robot_sn}")
        return ApiResponse.success(msg="添加机器人成功")
    
    @staticmethod
    def update_robot(db: Session, robot_id: int, robot_name: str = None, area_name: str = None, remark: str = None):
        robot = db.query(Robot).filter(Robot.id == robot_id, Robot.is_deleted == 0).first()
        if not robot:
            return ApiResponse.not_found("机器人不存在")
        
        if robot_name:
            robot.robot_name = robot_name
        if area_name:
            robot.area_name = area_name
        if remark is not None:
            robot.remark = remark
        
        db.commit()
        SysLogService.add_log(db, "admin", "机器人", f"更新机器人: {robot.robot_sn}")
        return ApiResponse.success(msg="更新机器人成功")
    
    @staticmethod
    def delete_robot(db: Session, robot_id: int):
        robot = db.query(Robot).filter(Robot.id == robot_id, Robot.is_deleted == 0).first()
        if not robot:
            return ApiResponse.not_found("机器人不存在")
        
        robot.is_deleted = 1
        db.commit()
        SysLogService.add_log(db, "admin", "机器人", f"删除机器人: {robot.robot_sn}")
        return ApiResponse.success(msg="删除机器人成功")
    
    @staticmethod
    def send_cmd(db: Session, robot_sn: str, cmd_code: str, param: str = None, operator: str = ""):
        robot = db.query(Robot).filter(Robot.robot_sn == robot_sn, Robot.is_deleted == 0).first()
        if not robot:
            return ApiResponse.not_found("机器人不存在")
        
        cmd_record = RobotCmdRecord(
            robot_sn=robot_sn,
            cmd_code=cmd_code,
            cmd_param=param or "",
            operator=operator,
            send_time=datetime.now()
        )
        db.add(cmd_record)
        db.commit()
        db.refresh(cmd_record)
        return ApiResponse.success(msg="指令下发成功")
    
    @staticmethod
    def get_cmd_list(db: Session, robot_sn: str = None, page: int = 1, page_size: int = 10, cmd_status: int = None):
        query = db.query(RobotCmdRecord)
        if robot_sn:
            query = query.filter(RobotCmdRecord.robot_sn == robot_sn)
        if cmd_status is not None:
            query = query.filter(RobotCmdRecord.cmd_status == cmd_status)
        
        total = query.count()
        records = query.order_by(desc(RobotCmdRecord.send_time)).offset((page - 1) * page_size).limit(page_size).all()
        
        record_list = []
        for record in records:
            record_list.append({
                "id": record.id,
                "robot_sn": record.robot_sn,
                "sensor_record_id": record.sensor_record_id,
                "cmd_code": record.cmd_code,
                "hardware_cmd": record.hardware_cmd,
                "cmd_param": record.cmd_param,
                "operator": record.operator,
                "send_time": record.send_time.strftime("%Y-%m-%d %H:%M:%S") if record.send_time else None,
                "response_code": record.response_code,
                "response_msg": record.response_msg,
                "finish_time": record.finish_time.strftime("%Y-%m-%d %H:%M:%S") if record.finish_time else None,
                "cmd_status": record.cmd_status
            })
        
        return ApiResponse.success_pagination(record_list, total, page, page_size)
    
    @staticmethod
    def get_sensor_history(db: Session, robot_sn: str = None, page: int = 1, page_size: int = 20, start_time: str = None, end_time: str = None):
        query = db.query(RobotSensorRecord)
        if robot_sn:
            query = query.filter(RobotSensorRecord.robot_sn == robot_sn)
        if start_time:
            query = query.filter(RobotSensorRecord.collect_time >= start_time)
        if end_time:
            query = query.filter(RobotSensorRecord.collect_time <= end_time)
        
        total = query.count()
        records = query.order_by(desc(RobotSensorRecord.collect_time)).offset((page - 1) * page_size).limit(page_size).all()
        
        record_list = []
        for record in records:
            record_list.append({
                "id": record.id,
                "robot_sn": record.robot_sn,
                "patrol_record_id": record.patrol_record_id,
                "temperature": record.temperature,
                "humidity": record.humidity,
                "smoke_level": record.smoke_level,
                "max_single_temp": record.max_single_temp,
                "human_detected": record.human_detected,
                "fire_risk": record.fire_risk,
                "thermal_matrix": record.thermal_matrix,
                "battery": record.battery,
                "collect_time": record.collect_time.strftime("%Y-%m-%d %H:%M:%S") if record.collect_time else None
            })
        
        return ApiResponse.success_pagination(record_list, total, page, page_size)
    
    @staticmethod
    def get_latest_sensor(db: Session, robot_sn: str):
        record = db.query(RobotSensorRecord).filter(
            RobotSensorRecord.robot_sn == robot_sn
        ).order_by(desc(RobotSensorRecord.collect_time)).first()
        
        if not record:
            return ApiResponse.not_found("暂无传感器数据")
        
        return ApiResponse.success({
            "id": record.id,
            "robot_sn": record.robot_sn,
            "patrol_record_id": record.patrol_record_id,
            "temperature": record.temperature,
            "humidity": record.humidity,
            "smoke_level": record.smoke_level,
            "max_single_temp": record.max_single_temp,
            "human_detected": record.human_detected,
            "fire_risk": record.fire_risk,
            "thermal_matrix": record.thermal_matrix,
            "battery": record.battery,
            "collect_time": record.collect_time.strftime("%Y-%m-%d %H:%M:%S") if record.collect_time else None
        })
    
    @staticmethod
    def get_sensor_statistics(db: Session, robot_sn: str = None, start_time: str = None, end_time: str = None):
        query = db.query(RobotSensorRecord)
        if robot_sn:
            query = query.filter(RobotSensorRecord.robot_sn == robot_sn)
        if start_time:
            query = query.filter(RobotSensorRecord.collect_time >= start_time)
        if end_time:
            query = query.filter(RobotSensorRecord.collect_time <= end_time)
        
        result = query.with_entities(
            func.count(RobotSensorRecord.id).label("total"),
            func.avg(RobotSensorRecord.temperature).label("avg_temp"),
            func.avg(RobotSensorRecord.humidity).label("avg_humidity"),
            func.avg(RobotSensorRecord.smoke_level).label("avg_smoke"),
            func.max(RobotSensorRecord.max_single_temp).label("max_temp")
        ).first()
        
        if result is None:
            return ApiResponse.success({
                "total": 0,
                "avg_temperature": 0.0,
                "avg_humidity": 0.0,
                "avg_smoke_level": 0.0,
                "max_temperature": 0.0
            })
        
        avg_temp = float(result.avg_temp) if result.avg_temp else 0.0
        avg_humidity = float(result.avg_humidity) if result.avg_humidity else 0.0
        avg_smoke = float(result.avg_smoke) if result.avg_smoke else 0.0
        max_temp = float(result.max_temp) if result.max_temp else 0.0
        
        return ApiResponse.success({
            "total": result.total or 0,
            "avg_temperature": round(avg_temp, 2),
            "avg_humidity": round(avg_humidity, 2),
            "avg_smoke_level": round(avg_smoke, 2),
            "max_temperature": round(max_temp, 2)
        })
    
    @staticmethod
    def get_thermal_matrix_latest(db: Session, robot_sn: str):
        """获取最新热力图数据"""
        record = db.query(RobotSensorRecord).filter(
            RobotSensorRecord.robot_sn == robot_sn
        ).order_by(desc(RobotSensorRecord.collect_time)).first()
        
        if not record:
            return ApiResponse.not_found("暂无热力图数据")
        
        return ApiResponse.success({
            "robot_sn": record.robot_sn,
            "thermal_matrix": record.thermal_matrix,
            "max_single_temp": record.max_single_temp,
            "collect_time": record.collect_time.strftime("%Y-%m-%d %H:%M:%S") if record.collect_time else None
        })
    
    @staticmethod
    def get_thermal_matrix_history(db: Session, robot_sn: str = None, page: int = 1, page_size: int = 20, start_time: str = None, end_time: str = None):
        """获取热力图历史记录"""
        query = db.query(RobotSensorRecord).filter(
            RobotSensorRecord.thermal_matrix.isnot(None),
            RobotSensorRecord.thermal_matrix != ''
        )
        
        if robot_sn:
            query = query.filter(RobotSensorRecord.robot_sn == robot_sn)
        if start_time:
            query = query.filter(RobotSensorRecord.collect_time >= start_time)
        if end_time:
            query = query.filter(RobotSensorRecord.collect_time <= end_time)
        
        total = query.count()
        records = query.order_by(desc(RobotSensorRecord.collect_time)).offset((page - 1) * page_size).limit(page_size).all()
        
        result_list = []
        for record in records:
            result_list.append({
                "robot_sn": record.robot_sn,
                "thermal_matrix": record.thermal_matrix,
                "max_single_temp": record.max_single_temp,
                "collect_time": record.collect_time.strftime("%Y-%m-%d %H:%M:%S") if record.collect_time else None
            })
        
        return ApiResponse.success_pagination(result_list, total, page, page_size)