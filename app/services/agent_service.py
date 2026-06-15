"""
智能体服务模块
提供数据库查询分析、状态监控和AI分析功能
"""
from typing import Optional, Dict, List, Any
from datetime import datetime
import psutil
import time
from sqlalchemy import text, create_engine, inspect
from sqlalchemy.exc import SQLAlchemyError
from app.config.settings import settings
from app.services.deepseek_service import deepseek_service
from app.config.database import get_db
from sqlalchemy.orm import Session

class AgentService:
    """智能体服务类"""
    
    def __init__(self):
        """初始化智能体服务"""
        self.db_connection_status = False
        self.last_connection_time = None
        self.task_queue = []
        self.processing_progress = {}
        self.system_metrics = {}
        self.alarms = []
        
    def get_database_connection_status(self) -> Dict:
        """获取数据库连接状态"""
        try:
            # 测试数据库连接
            connection_string = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
            engine = create_engine(connection_string)
            
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.db_connection_status = True
            self.last_connection_time = datetime.now()
            
            return {
                "status": "connected",
                "connected": True,
                "lastConnectedTime": self.last_connection_time.isoformat(),
                "database": settings.DB_NAME,
                "host": settings.DB_HOST,
                "port": settings.DB_PORT
            }
        except SQLAlchemyError as e:
            self.db_connection_status = False
            return {
                "status": "disconnected",
                "connected": False,
                "error": str(e),
                "lastConnectedTime": self.last_connection_time.isoformat() if self.last_connection_time else None
            }
    
    def get_system_metrics(self) -> Dict:
        """获取系统资源占用情况"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        self.system_metrics = {
            "cpu": {
                "usagePercent": cpu_percent,
                "cores": psutil.cpu_count(logical=True),
                "status": "normal" if cpu_percent < 80 else "warning" if cpu_percent < 95 else "critical"
            },
            "memory": {
                "total": round(memory.total / (1024**3), 2),
                "used": round(memory.used / (1024**3), 2),
                "available": round(memory.available / (1024**3), 2),
                "usagePercent": memory.percent,
                "status": "normal" if memory.percent < 80 else "warning" if memory.percent < 95 else "critical"
            },
            "disk": {
                "total": round(disk.total / (1024**3), 2),
                "used": round(disk.used / (1024**3), 2),
                "free": round(disk.free / (1024**3), 2),
                "usagePercent": disk.percent,
                "status": "normal" if disk.percent < 80 else "warning" if disk.percent < 95 else "critical"
            },
            "network": {
                "bytesSent": round(network.bytes_sent / (1024**2), 2),
                "bytesReceived": round(network.bytes_recv / (1024**2), 2),
                "packetsSent": network.packets_sent,
                "packetsReceived": network.packets_recv
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return self.system_metrics
    
    def get_task_queue(self) -> Dict:
        """获取当前任务队列"""
        return {
            "pending": [t for t in self.task_queue if t["status"] == "pending"],
            "processing": [t for t in self.task_queue if t["status"] == "processing"],
            "completed": [t for t in self.task_queue if t["status"] == "completed"],
            "failed": [t for t in self.task_queue if t["status"] == "failed"],
            "total": len(self.task_queue)
        }
    
    def add_task(self, task_type: str, parameters: Dict) -> str:
        """添加新任务到队列"""
        task_id = f"task_{int(time.time())}_{len(self.task_queue)}"
        task = {
            "id": task_id,
            "type": task_type,
            "parameters": parameters,
            "status": "pending",
            "createdAt": datetime.now().isoformat(),
            "startedAt": None,
            "completedAt": None,
            "progress": 0,
            "result": None,
            "error": None
        }
        self.task_queue.append(task)
        return task_id
    
    def execute_task(self, task_id: str, db: Session) -> Optional[Dict]:
        """执行指定任务"""
        for task in self.task_queue:
            if task["id"] == task_id:
                task["status"] = "processing"
                task["startedAt"] = datetime.now().isoformat()
                task["progress"] = 20
                
                try:
                    if task["type"] == "query_analysis":
                        result = self.execute_query_analysis(db, task["parameters"])
                    elif task["type"] == "business_metrics":
                        result = self.get_business_metrics(db)
                    elif task["type"] == "trend_analysis":
                        result = self.get_trend_analysis(db, task["parameters"])
                    elif task["type"] == "ai_insights":
                        result = self.generate_ai_insights(db, task["parameters"])
                    else:
                        result = {"error": "Unknown task type"}
                    
                    task["status"] = "completed"
                    task["progress"] = 100
                    task["completedAt"] = datetime.now().isoformat()
                    task["result"] = result
                    return result
                except Exception as e:
                    task["status"] = "failed"
                    task["progress"] = 0
                    task["completedAt"] = datetime.now().isoformat()
                    task["error"] = str(e)
                    self.add_alarm("task_failed", f"任务 {task_id} 执行失败: {str(e)}")
                    return None
        
        return None
    
    def execute_query_analysis(self, db: Session, parameters: Dict) -> Dict:
        """执行数据库查询分析"""
        task_progress = 30
        self.processing_progress["query_analysis"] = task_progress
        
        try:
            query = parameters.get("query", "")
            if not query:
                return {"error": "查询语句不能为空"}
            
            task_progress = 50
            self.processing_progress["query_analysis"] = task_progress
            
            # 安全检查：只允许 SELECT 查询
            if not query.strip().upper().startswith("SELECT"):
                return {"error": "只允许执行 SELECT 查询"}
            
            task_progress = 70
            self.processing_progress["query_analysis"] = task_progress
            
            result = db.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            
            task_progress = 90
            self.processing_progress["query_analysis"] = task_progress
            
            data = []
            for row in rows:
                data.append(dict(zip(columns, row)))
            
            task_progress = 100
            self.processing_progress["query_analysis"] = task_progress
            
            return {
                "query": query,
                "rowCount": len(data),
                "columns": list(columns),
                "data": data[:100],  # 限制返回数量
                "truncated": len(data) > 100
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_business_metrics(self, db: Session) -> Dict:
        """获取关键业务指标"""
        metrics = {}
        
        # 获取设备数量统计
        try:
            result = db.execute(text("SELECT COUNT(*) FROM t_device"))
            metrics["deviceCount"] = result.scalar()
            
            result = db.execute(text("SELECT COUNT(*) FROM t_device WHERE status = 'active'"))
            metrics["activeDeviceCount"] = result.scalar()
        except Exception as e:
            metrics["deviceError"] = str(e)
        
        # 获取告警统计
        try:
            result = db.execute(text("SELECT COUNT(*) FROM t_alert"))
            metrics["alertCount"] = result.scalar()
            
            result = db.execute(text("SELECT COUNT(*) FROM t_alert WHERE status = 'pending'"))
            metrics["pendingAlertCount"] = result.scalar()
        except Exception as e:
            metrics["alertError"] = str(e)
        
        # 获取传感器数据统计
        try:
            result = db.execute(text("SELECT COUNT(*) FROM t_sensor_data"))
            metrics["sensorDataCount"] = result.scalar()
            
            result = db.execute(text("SELECT AVG(temperature), AVG(humidity), MAX(smoke_level) FROM t_sensor_data ORDER BY receive_time DESC LIMIT 100"))
            row = result.fetchone()
            if row:
                metrics["avgTemperature"] = float(row[0]) if row[0] else None
                metrics["avgHumidity"] = float(row[1]) if row[1] else None
                metrics["maxSmokeLevel"] = float(row[2]) if row[2] else None
        except Exception as e:
            metrics["sensorError"] = str(e)
        
        # 获取用户统计
        try:
            result = db.execute(text("SELECT COUNT(*) FROM t_user"))
            metrics["userCount"] = result.scalar()
            
            result = db.execute(text("SELECT COUNT(*) FROM t_user WHERE role = 'admin'"))
            metrics["adminCount"] = result.scalar()
        except Exception as e:
            metrics["userError"] = str(e)
        
        metrics["timestamp"] = datetime.now().isoformat()
        return metrics
    
    def get_trend_analysis(self, db: Session, parameters: Dict) -> Dict:
        """获取趋势数据分析"""
        start_time = parameters.get("start_time")
        end_time = parameters.get("end_time")
        interval = parameters.get("interval", "1h")
        
        if not start_time or not end_time:
            return {"error": "需要提供时间范围"}
        
        try:
            query = f"""
                SELECT 
                    DATE_FORMAT(receive_time, '%Y-%m-%d %H:00:00') as hour,
                    AVG(temperature) as avg_temp,
                    AVG(humidity) as avg_humidity,
                    MAX(smoke_level) as max_smoke,
                    COUNT(*) as data_points
                FROM t_sensor_data
                WHERE receive_time BETWEEN '{start_time}' AND '{end_time}'
                GROUP BY hour
                ORDER BY hour
            """
            
            result = db.execute(text(query))
            rows = result.fetchall()
            columns = result.keys()
            
            trend_data = []
            for row in rows:
                trend_data.append({
                    "time": row[0],
                    "temperature": float(row[1]) if row[1] else None,
                    "humidity": float(row[2]) if row[2] else None,
                    "smokeLevel": float(row[3]) if row[3] else None,
                    "dataPoints": row[4]
                })
            
            return {
                "startTime": start_time,
                "endTime": end_time,
                "interval": interval,
                "trendData": trend_data,
                "dataPointCount": len(trend_data)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def generate_ai_insights(self, db: Session, parameters: Dict) -> Dict:
        """生成AI分析洞察"""
        # 获取业务指标
        metrics = self.get_business_metrics(db)
        
        # 获取系统指标
        system_metrics = self.get_system_metrics()
        
        # 构建分析请求
        analysis_prompt = f"""
        智能巡检系统数据分析报告
        
        业务指标:
        - 设备总数: {metrics.get('deviceCount', 0)}
        - 活跃设备数: {metrics.get('activeDeviceCount', 0)}
        - 告警总数: {metrics.get('alertCount', 0)}
        - 待处理告警: {metrics.get('pendingAlertCount', 0)}
        - 传感器数据总量: {metrics.get('sensorDataCount', 0)}
        - 平均温度: {metrics.get('avgTemperature', 0)}°C
        - 平均湿度: {metrics.get('avgHumidity', 0)}%
        - 最大烟雾浓度: {metrics.get('maxSmokeLevel', 0)}
        
        系统资源:
        - CPU使用率: {system_metrics['cpu']['usagePercent']}%
        - 内存使用率: {system_metrics['memory']['usagePercent']}%
        - 磁盘使用率: {system_metrics['disk']['usagePercent']}%
        
        请分析以上数据，提供：
        1. 业务优化建议
        2. 系统性能提升建议
        3. 潜在风险识别
        4. 具体可操作的改进措施
        
        请用中文输出，格式清晰，建议具体可行。
        """
        
        # 调用DeepSeek API进行分析
        insights = deepseek_service.simple_chat(analysis_prompt)
        
        return {
            "businessMetrics": metrics,
            "systemMetrics": system_metrics,
            "aiInsights": insights,
            "generatedAt": datetime.now().isoformat()
        }
    
    def natural_language_query(self, query: str, db: Session) -> Dict:
        """自然语言查询"""
        # 先尝试理解用户意图
        intent_prompt = f"""
        用户查询: {query}
        
        请判断用户的查询意图，并输出JSON格式的分析结果：
        {{
            "intent": "查询类型，可选值：device_stats, alert_stats, sensor_data, trend_analysis, system_status, ai_analysis, general",
            "parameters": {{相关参数对象}}
        }}
        
        示例：
        - 用户问"有多少设备" -> {{\"intent\": \"device_stats\", \"parameters\": {{}}}}
        - 用户问"最近24小时温度趋势" -> {{\"intent\": \"trend_analysis\", \"parameters\": {{\"period\": \"24h\"}}}}
        """
        
        # 简化处理：直接根据关键词判断意图
        intent = "general"
        parameters = {}
        
        if any(keyword in query for keyword in ["设备", "device", "Device"]):
            intent = "device_stats"
        elif any(keyword in query for keyword in ["告警", "alert", "Alert"]):
            intent = "alert_stats"
        elif any(keyword in query for keyword in ["温度", "湿度", "传感器", "sensor"]):
            intent = "sensor_data"
        elif any(keyword in query for keyword in ["趋势", "趋势分析", "trend"]):
            intent = "trend_analysis"
            parameters["period"] = "24h"
        elif any(keyword in query for keyword in ["系统", "状态", "status", "资源"]):
            intent = "system_status"
        elif any(keyword in query for keyword in ["分析", "建议", "优化", "insight"]):
            intent = "ai_analysis"
        
        # 执行对应的查询
        if intent == "device_stats":
            result = self.get_business_metrics(db)
            result = {k: v for k, v in result.items() if "device" in k.lower() or k in ["deviceCount", "activeDeviceCount"]}
        elif intent == "alert_stats":
            result = self.get_business_metrics(db)
            result = {k: v for k, v in result.items() if "alert" in k.lower()}
        elif intent == "sensor_data":
            result = self.get_business_metrics(db)
            result = {k: v for k, v in result.items() if any(x in k.lower() for x in ["temperature", "humidity", "smoke", "sensor"])}
        elif intent == "trend_analysis":
            end_time = datetime.now()
            start_time = end_time - (parameters.get("period") == "24h" and timedelta(hours=24) or timedelta(hours=72))
            result = self.get_trend_analysis(db, {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "interval": "1h"
            })
        elif intent == "system_status":
            result = self.get_system_metrics()
        elif intent == "ai_analysis":
            result = self.generate_ai_insights(db, {})
        else:
            # 通用查询，调用AI回答
            result = {"answer": deepseek_service.simple_chat(query)}
        
        # 生成自然语言回复
        response_prompt = f"""
        用户查询: {query}
        查询结果: {result}
        
        请用自然、友好的中文将查询结果总结给用户。
        """
        
        natural_response = deepseek_service.simple_chat(response_prompt)
        
        return {
            "originalQuery": query,
            "intent": intent,
            "parameters": parameters,
            "data": result,
            "naturalResponse": natural_response
        }
    
    def add_alarm(self, alarm_type: str, message: str):
        """添加告警"""
        alarm = {
            "id": f"alarm_{int(time.time())}",
            "type": alarm_type,
            "message": message,
            "level": "warning" if alarm_type == "task_failed" else "info",
            "createdAt": datetime.now().isoformat(),
            "acknowledged": False
        }
        self.alarms.append(alarm)
        # 保留最近100条告警
        if len(self.alarms) > 100:
            self.alarms = self.alarms[-100:]
    
    def get_alarms(self, acknowledged: Optional[bool] = None) -> List[Dict]:
        """获取告警列表"""
        if acknowledged is not None:
            return [a for a in self.alarms if a["acknowledged"] == acknowledged]
        return self.alarms
    
    def acknowledge_alarm(self, alarm_id: str) -> bool:
        """确认告警"""
        for alarm in self.alarms:
            if alarm["id"] == alarm_id:
                alarm["acknowledged"] = True
                return True
        return False
    
    def get_agent_status(self) -> Dict:
        """获取智能体综合状态"""
        return {
            "database": self.get_database_connection_status(),
            "systemMetrics": self.get_system_metrics(),
            "taskQueue": self.get_task_queue(),
            "processingProgress": self.processing_progress,
            "alarms": self.get_alarms(acknowledged=False),
            "alarmCount": len(self.get_alarms(acknowledged=False)),
            "timestamp": datetime.now().isoformat()
        }

# 创建全局智能体服务实例
agent_service = AgentService()