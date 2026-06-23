"""
DeepSeek AI 服务模块
使用 LangChain 和 DeepSeek API 提供 AI 功能
"""
from typing import Optional, Dict, List
from datetime import datetime
from langchain_deepseek import ChatDeepSeek
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from app.config.settings import settings

class DeepSeekService:
    """DeepSeek AI 服务类"""
    
    # 智能巡检系统专业AI提示词
    SYSTEM_PROMPT = """
你是智能巡检系统的专业AI助手，精通设备监控、环境数据分析、系统运维和业务优化。

【核心能力】
1. **设备管理专家**：设备注册、状态监控、故障诊断
2. **环境监测分析师**：温度、湿度、烟雾浓度实时监控与趋势预测
3. **系统运维顾问**：资源利用率分析、性能优化建议
4. **安全告警专家**：异常检测、风险评估、应急预案
"""
    
    def __init__(self):
        """初始化 DeepSeek 服务"""
        self.llm = ChatDeepSeek(
            model=settings.DEEPSEEK_MODEL,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_API_URL,
            temperature=0.7,
            timeout=settings.DEEPSEEK_TIMEOUT,
            streaming=False
        )
        self.parser = StrOutputParser()
    
    def simple_chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """
        简单对话
        
        参数:
            message: 用户消息
            system_prompt: 系统提示词 (可选，默认使用专业提示词)
        
        返回:
            AI 回复
        """
        try:
            messages = []
            
            # 使用专业提示词或自定义提示词
            prompt = system_prompt if system_prompt else self.SYSTEM_PROMPT
            messages.append(SystemMessage(content=prompt))
            
            messages.append(HumanMessage(content=message))
            
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"调用 DeepSeek AI 服务时发生错误: {str(e)}"
    
    def analyze_environment(self, temperature: float, humidity: float, smoke_level: float) -> Dict:
        """
        环境数据分析
        
        参数:
            temperature: 温度
            humidity: 湿度
            smoke_level: 烟雾浓度
        
        返回:
            分析结果
        """
        user_message = f"""请分析以下环境监测数据：

【环境数据】
- 平均温度: {temperature}°C
- 平均湿度: {humidity}%
- 最大烟雾浓度: {smoke_level}

请提供：环境状态评估、潜在风险识别、针对当前环境状况的具体建议。"""
        
        analysis = self.simple_chat(user_message)
        
        # 判断状态
        status = "normal"
        if smoke_level > 100:
            status = "danger"
        elif smoke_level > 50:
            status = "warning"
        
        return {
            "avgTemperature": temperature,
            "avgHumidity": humidity,
            "maxSmokeLevel": smoke_level,
            "status": status,
            "analysis": analysis
        }
    
    def generate_report(self, report_type: str, data_points: int, start_time: str, end_time: str) -> Dict:
        """
        生成分析报告
        
        参数:
            report_type: 报告类型 (daily/weekly/monthly)
            data_points: 数据点数量
            start_time: 开始时间
            end_time: 结束时间
        
        返回:
            报告内容
        """
        user_message = f"""请生成一份专业的{report_type}分析报告。

【报告参数】
- 报告类型: {report_type}
- 时间范围: {start_time} 到 {end_time}
- 数据点数: {data_points}

请生成一份详细的中文报告，包括：报告概述、数据分析摘要、关键发现、建议与总结。"""
        
        summary = self.simple_chat(user_message)
        
        return {
            "type": report_type,
            "startTime": start_time,
            "endTime": end_time,
            "dataPoints": data_points,
            "summary": summary
        }
    
    def natural_language_query(self, query: str) -> Dict:
        """
        自然语言查询
        
        参数:
            query: 用户查询
        
        返回:
            查询结果
        """
        user_message = f"""用户问题: {query}

请根据您的专业知识提供准确、详细的回答。"""
        
        answer = self.simple_chat(user_message)
        
        return {
            "query": query,
            "answer": answer,
            "confidence": 0.95
        }
    
    def predict_environment(self, current_temp: float, current_humidity: float, hours: int) -> Dict:
        """
        环境数据预测
        
        参数:
            current_temp: 当前温度
            current_humidity: 当前湿度
            hours: 预测小时数
        
        返回:
            预测结果
        """
        user_message = f"""请预测未来{hours}小时的环境变化。

【当前环境数据】
- 温度: {current_temp}°C
- 湿度: {current_humidity}%

请提供：温度变化趋势、湿度变化趋势、风险等级评估。"""
        
        response = self.simple_chat(user_message)
        
        # 简化预测逻辑（实际应该解析AI返回的JSON）
        predictions = []
        from datetime import datetime, timedelta
        current_time = datetime.now()
        
        for i in range(1, hours + 1):
            predict_time = current_time + timedelta(hours=i)
            temp_trend = 0.5 if i % 2 == 0 else -0.3
            humidity_trend = 0.2
            
            predictions.append({
                "time": predict_time.isoformat(),
                "temperature": round(current_temp + temp_trend * i, 2),
                "humidity": round(current_humidity + humidity_trend * i, 2),
                "riskLevel": "low"
            })
        
        return {
            "predictions": predictions,
            "ai_analysis": response
        }
    
    def generate_inspection_plan(self, location: str, time_range: str, requirements: str) -> Dict:
        """
        生成巡检计划
        
        参数:
            location: 巡检地点
            time_range: 时间范围
            requirements: 巡检要求
        
        返回:
            巡检计划
        """
        user_message = f"""请生成一份详细的巡检计划。

【巡检信息】
- 巡检地点: {location}
- 时间范围: {time_range}
- 巡检要求: {requirements}

请生成一份详细的中文巡检计划，包括：巡检目标、巡检路线、检查要点、注意事项、应急预案。"""
        
        plan = self.simple_chat(user_message)
        
        return {
            "location": location,
            "timeRange": time_range,
            "requirements": requirements,
            "plan": plan,
            "status": "generated"
        }
    
    def analyze_equipment_health(self, equipment_name: str, operation_hours: int, 
                                 error_count: int, performance_data: Dict) -> Dict:
        """
        分析设备健康状态
        
        参数:
            equipment_name: 设备名称
            operation_hours: 运行时间
            error_count: 错误次数
            performance_data: 性能数据
        
        返回:
            健康分析结果
        """
        user_message = f"""请分析以下设备的健康状态。

【设备信息】
- 设备名称: {equipment_name}
- 运行时间: {operation_hours} 小时
- 错误次数: {error_count} 次
- 性能数据: {performance_data}

请分析：设备当前健康状态、潜在故障风险、维护建议、更换建议（如需要）。"""
        
        analysis = self.simple_chat(user_message)
        
        # 判断健康状态
        health_status = "good"
        if error_count > 10 or operation_hours > 10000:
            health_status = "poor"
        elif error_count > 5 or operation_hours > 5000:
            health_status = "fair"
        
        return {
            "equipmentName": equipment_name,
            "operationHours": operation_hours,
            "errorCount": error_count,
            "healthStatus": health_status,
            "analysis": analysis
        }
    
    def analyze_with_metrics(self, business_metrics: Dict, system_metrics: Dict, user_query: str = "") -> Dict:
        """
        使用业务指标和系统指标进行深度分析
        
        参数:
            business_metrics: 业务指标
            system_metrics: 系统指标
            user_query: 用户问题（可选）
        
        返回:
            分析结果
        """
        metrics_text = f"""【业务指标】
- 设备总数: {business_metrics.get('deviceCount', 0)}
- 活跃设备: {business_metrics.get('activeDeviceCount', 0)}
- 告警总数: {business_metrics.get('alertCount', 0)}
- 待处理告警: {business_metrics.get('pendingAlertCount', 0)}
- 传感器数据量: {business_metrics.get('sensorDataCount', 0)}
- 平均温度: {business_metrics.get('avgTemperature', 0)}°C
- 平均湿度: {business_metrics.get('avgHumidity', 0)}%
- 最大烟雾浓度: {business_metrics.get('maxSmokeLevel', 0)}

【系统资源】
- CPU使用率: {system_metrics.get('cpu', {}).get('usagePercent', 0)}%
- 内存使用率: {system_metrics.get('memory', {}).get('usagePercent', 0)}%
- 磁盘使用率: {system_metrics.get('disk', {}).get('usagePercent', 0)}%"""
        
        if user_query:
            user_message = f"""{metrics_text}

用户问题: {user_query}

请提供专业分析和可操作建议。"""
        else:
            user_message = f"""{metrics_text}

请分析以上数据，提供：业务优化建议、系统性能提升建议、潜在风险识别、具体可操作的改进措施。"""
        
        insights = self.simple_chat(user_message)
        
        return {
            "businessMetrics": business_metrics,
            "systemMetrics": system_metrics,
            "userQuery": user_query,
            "insights": insights,
            "generatedAt": datetime.now().isoformat()
        }

# 全局服务实例（延迟加载）
_deepseek_service_instance = None

def get_deepseek_service() -> DeepSeekService:
    """获取 DeepSeek 服务实例（延迟加载）"""
    global _deepseek_service_instance
    if _deepseek_service_instance is None:
        _deepseek_service_instance = DeepSeekService()
    return _deepseek_service_instance

# 保持向后兼容 - 使用延迟加载属性
class _DeepSeekServiceProxy:
    """DeepSeek 服务代理类，实现延迟加载"""
    def __getattr__(self, name):
        return getattr(get_deepseek_service(), name)

# 使用代理替代直接实例化，避免模块导入时创建实例
deepseek_service = _DeepSeekServiceProxy()