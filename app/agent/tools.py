from langchain.tools import tool
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

class DatabaseTools:
    def __init__(self, db: Session):
        self.db = db
    
    @tool("get_robot_list", return_direct=False)
    def get_robot_list(self) -> str:
        """获取所有巡检机器人列表，包含在线状态、电量、运行模式等信息"""
        from app.models.robot import Robot
        robots = self.db.query(Robot).filter(Robot.is_deleted == 0).all()
        if not robots:
            return "暂无机器人数据"
        
        result = "机器人列表:\n"
        for robot in robots:
            online = "在线" if robot.online_status == 1 else "离线"
            modes = {0: "待机", 1: "自动巡检", 2: "手动遥控", 3: "充电中", 4: "故障"}
            run_mode = modes.get(robot.run_mode, "未知")
            result += f"- SN: {robot.robot_sn}, 名称: {robot.robot_name}, 区域: {robot.area_name}, 状态: {online}, 电量: {robot.battery}%, 模式: {run_mode}\n"
        return result
    
    @tool("get_robot_statistics", return_direct=False)
    def get_robot_statistics(self) -> str:
        """获取机器人统计信息（总数、在线数、离线数）"""
        from app.models.robot import Robot
        total = self.db.query(Robot).filter(Robot.is_deleted == 0).count()
        online = self.db.query(Robot).filter(Robot.is_deleted == 0, Robot.online_status == 1).count()
        offline = total - online
        return f"机器人统计: 总数={total}, 在线={online}, 离线={offline}"
    
    @tool("get_alarm_list", return_direct=False)
    def get_alarm_list(self, alarm_level: Optional[str] = None, deal_status: Optional[int] = None, limit: int = 10) -> str:
        """获取告警列表
        Args:
            alarm_level: 告警等级过滤（RED/ORANGE/NORMAL）
            deal_status: 处置状态过滤（0-未处理/1-已处理）
            limit: 返回数量限制，默认10
        """
        from app.models.alarm import AlarmInfo
        from sqlalchemy import desc
        
        query = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0)
        if alarm_level:
            query = query.filter(AlarmInfo.alarm_level == alarm_level)
        if deal_status is not None:
            query = query.filter(AlarmInfo.deal_status == deal_status)
        
        alarms = query.order_by(desc(AlarmInfo.create_time)).limit(limit).all()
        if not alarms:
            return "暂无告警数据"
        
        result = "告警列表:\n"
        for alarm in alarms:
            status = "已处理" if alarm.deal_status == 1 else "待处理"
            result += f"- ID: {alarm.id}, 等级: {alarm.alarm_level}, 类型: {alarm.alarm_type}, 区域: {alarm.area_name}, 描述: {alarm.alarm_desc}, 状态: {status}, 时间: {alarm.create_time}\n"
        return result
    
    @tool("get_alarm_statistics", return_direct=False)
    def get_alarm_statistics(self) -> str:
        """获取告警统计信息（总数、各等级数量、待处理/已处理数量）"""
        from app.models.alarm import AlarmInfo
        total = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0).count()
        red = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.alarm_level == "RED").count()
        orange = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.alarm_level == "ORANGE").count()
        normal = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.alarm_level == "NORMAL").count()
        pending = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.deal_status == 0).count()
        dealt = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.deal_status == 1).count()
        return f"告警统计: 总数={total}, 红色={red}, 橙色={orange}, 普通={normal}, 待处理={pending}, 已处理={dealt}"
    
    @tool("get_alarm_detail", return_direct=False)
    def get_alarm_detail(self, alarm_id: int) -> str:
        """获取告警详情，包含关联的传感器数据
        Args:
            alarm_id: 告警ID
        """
        from app.models.alarm import AlarmInfo
        from app.models.robot import RobotSensorRecord
        
        alarm = self.db.query(AlarmInfo).filter(AlarmInfo.id == alarm_id, AlarmInfo.is_deleted == 0).first()
        if not alarm:
            return f"告警ID {alarm_id} 不存在"
        
        sensor_record = self.db.query(RobotSensorRecord).filter(RobotSensorRecord.id == alarm.sensor_record_id).first()
        sensor_data = ""
        if sensor_record:
            sensor_data = f"\n关联传感器数据: 温度={sensor_record.temperature}℃, 湿度={sensor_record.humidity}%, 烟雾={sensor_record.smoke_level}PPM, 最高温度={sensor_record.max_single_temp}℃"
        
        status = "已处理" if alarm.deal_status == 1 else "待处理"
        return f"告警详情:\nID: {alarm_id}\n等级: {alarm.alarm_level}\n类型: {alarm.alarm_type}\n区域: {alarm.area_name}\n描述: {alarm.alarm_desc}\n状态: {status}{sensor_data}"
    
    @tool("get_patrol_task_list", return_direct=False)
    def get_patrol_task_list(self, limit: int = 10) -> str:
        """获取巡检任务列表
        Args:
            limit: 返回数量限制，默认10
        """
        from app.models.patrol import PatrolTask
        from sqlalchemy import desc
        
        tasks = self.db.query(PatrolTask).order_by(desc(PatrolTask.create_time)).limit(limit).all()
        if not tasks:
            return "暂无巡检任务"
        
        cycles = {1: "每日", 2: "工作日", 3: "周末", 4: "单次"}
        result = "巡检任务列表:\n"
        for task in tasks:
            status = "启用" if task.status == 1 else "停用"
            cycle = cycles.get(task.cycle_type, "未知")
            result += f"- ID: {task.id}, 名称: {task.task_name}, 机器人: {task.robot_sn}, 周期: {cycle}, 开始: {task.start_time}, 结束: {task.end_time}, 状态: {status}\n"
        return result
    
    @tool("get_patrol_record_list", return_direct=False)
    def get_patrol_record_list(self, limit: int = 10) -> str:
        """获取巡检记录列表
        Args:
            limit: 返回数量限制，默认10
        """
        from app.models.patrol import PatrolRecord
        from sqlalchemy import desc
        
        records = self.db.query(PatrolRecord).order_by(desc(PatrolRecord.start_time)).limit(limit).all()
        if not records:
            return "暂无巡检记录"
        
        statuses = {1: "进行中", 2: "已完成", 3: "异常中断"}
        result = "巡检记录列表:\n"
        for record in records:
            status = statuses.get(record.patrol_status, "未知")
            end_time = record.end_time if record.end_time else "未结束"
            result += f"- ID: {record.id}, 机器人: {record.robot_sn}, 状态: {status}, 开始: {record.start_time}, 结束: {end_time}, 数据数: {record.data_count}, 告警数: {record.alarm_count}\n"
        return result
    
    @tool("get_patrol_statistics", return_direct=False)
    def get_patrol_statistics(self) -> str:
        """获取巡检统计信息（总数、进行中、已完成、异常中断数量）"""
        from app.models.patrol import PatrolRecord
        total = self.db.query(PatrolRecord).count()
        ongoing = self.db.query(PatrolRecord).filter(PatrolRecord.patrol_status == 1).count()
        completed = self.db.query(PatrolRecord).filter(PatrolRecord.patrol_status == 2).count()
        interrupted = self.db.query(PatrolRecord).filter(PatrolRecord.patrol_status == 3).count()
        return f"巡检统计: 总数={total}, 进行中={ongoing}, 已完成={completed}, 异常中断={interrupted}"
    
    @tool("get_sensor_latest", return_direct=False)
    def get_sensor_latest(self, robot_sn: Optional[str] = None) -> str:
        """获取最新传感器数据
        Args:
            robot_sn: 机器人序列号，不指定则返回所有机器人的最新数据
        """
        from app.models.robot import RobotSensorRecord
        from sqlalchemy import desc
        
        if robot_sn:
            record = self.db.query(RobotSensorRecord).filter(RobotSensorRecord.robot_sn == robot_sn).order_by(desc(RobotSensorRecord.collect_time)).first()
            if not record:
                return f"机器人 {robot_sn} 暂无传感器数据"
            records = [record]
        else:
            records = []
            robots = self.db.query(RobotSensorRecord.robot_sn).distinct().all()
            for (sn,) in robots:
                record = self.db.query(RobotSensorRecord).filter(RobotSensorRecord.robot_sn == sn).order_by(desc(RobotSensorRecord.collect_time)).first()
                if record:
                    records.append(record)
        
        if not records:
            return "暂无传感器数据"
        
        result = "最新传感器数据:\n"
        for record in records:
            human = "有人" if record.human_detected == 1 else "无人"
            result += f"- 机器人: {record.robot_sn}, 温度: {record.temperature}℃, 湿度: {record.humidity}%, 烟雾: {record.smoke_level}PPM, 最高温度: {record.max_single_temp}℃, 人体检测: {human}, 电量: {record.battery}%, 时间: {record.collect_time}\n"
        return result
    
    @tool("get_sensor_statistics", return_direct=False)
    def get_sensor_statistics(self, robot_sn: Optional[str] = None) -> str:
        """获取传感器统计信息（平均温度、湿度、烟雾浓度、最高温度）
        Args:
            robot_sn: 机器人序列号，不指定则统计所有机器人
        """
        from app.models.robot import RobotSensorRecord
        from sqlalchemy import func
        
        query = self.db.query(RobotSensorRecord)
        if robot_sn:
            query = query.filter(RobotSensorRecord.robot_sn == robot_sn)
        
        result = query.with_entities(
            func.count(RobotSensorRecord.id).label("total"),
            func.avg(RobotSensorRecord.temperature).label("avg_temp"),
            func.avg(RobotSensorRecord.humidity).label("avg_humidity"),
            func.avg(RobotSensorRecord.smoke_level).label("avg_smoke"),
            func.max(RobotSensorRecord.max_single_temp).label("max_temp")
        ).first()
        
        robot_str = f"机器人 {robot_sn}" if robot_sn else "全部机器人"
        return f"{robot_str}传感器统计: 数据总数={result.total or 0}, 平均温度={round(result.avg_temp, 2) if result.avg_temp else 0}℃, 平均湿度={round(result.avg_humidity, 2) if result.avg_humidity else 0}%, 平均烟雾={round(result.avg_smoke, 2) if result.avg_smoke else 0}PPM, 最高温度={round(result.max_temp, 2) if result.max_temp else 0}℃"
    
    @tool("get_daily_report", return_direct=False)
    def get_daily_report(self) -> str:
        """获取日报数据（巡检次数、告警数量、环境平均温度湿度）"""
        from app.models.patrol import PatrolRecord
        from app.models.alarm import AlarmInfo
        from app.models.robot import RobotSensorRecord
        from sqlalchemy import func
        
        now = datetime.now()
        start_time = now.replace(hour=0, minute=0, second=0)
        
        total_patrol = self.db.query(PatrolRecord).filter(PatrolRecord.start_time >= start_time).count()
        completed_patrol = self.db.query(PatrolRecord).filter(PatrolRecord.start_time >= start_time, PatrolRecord.patrol_status == 2).count()
        
        total_alarm = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.create_time >= start_time).count()
        processed_alarm = self.db.query(AlarmInfo).filter(AlarmInfo.is_deleted == 0, AlarmInfo.create_time >= start_time, AlarmInfo.deal_status == 1).count()
        
        sensor_result = self.db.query(RobotSensorRecord).filter(RobotSensorRecord.collect_time >= start_time).with_entities(
            func.avg(RobotSensorRecord.temperature).label("avg_temp"),
            func.avg(RobotSensorRecord.humidity).label("avg_humidity"),
            func.max(RobotSensorRecord.temperature).label("max_temp")
        ).first()
        
        return f"""日报数据({now.strftime('%Y-%m-%d')}):
巡检统计: 总次数={total_patrol}, 已完成={completed_patrol}
告警统计: 总告警={total_alarm}, 已处理={processed_alarm}
环境统计: 平均温度={round(sensor_result.avg_temp, 2) if sensor_result.avg_temp else 0}℃, 平均湿度={round(sensor_result.avg_humidity, 2) if sensor_result.avg_humidity else 0}%, 最高温度={round(sensor_result.max_temp, 2) if sensor_result.max_temp else 0}℃"""
    
    def get_tools(self):
        return [
            self.get_robot_list,
            self.get_robot_statistics,
            self.get_alarm_list,
            self.get_alarm_statistics,
            self.get_alarm_detail,
            self.get_patrol_task_list,
            self.get_patrol_record_list,
            self.get_patrol_statistics,
            self.get_sensor_latest,
            self.get_sensor_statistics,
            self.get_daily_report
        ]