from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.chat_history import BaseChatMessageHistory
from app.config.settings import settings
from app.agent.tools import DatabaseTools
from sqlalchemy.orm import Session
import logging
import json

logger = logging.getLogger("inspection_system")

class InMemoryChatMessageHistory(BaseChatMessageHistory):
    def __init__(self):
        self.messages = []
    
    def add_message(self, message):
        self.messages.append(message)
    
    def clear(self):
        self.messages = []

class InspectionAgent:
    def __init__(self, db: Session):
        self.db = db
        self._memory_store = {}
    
    def _get_llm(self):
        return ChatOpenAI(
            model=settings.DEEPSEEK_MODEL,
            base_url=settings.DEEPSEEK_BASE_URL,
            api_key=settings.DEEPSEEK_API_KEY,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS
        )
    
    def _get_tool_map(self):
        db_tools = DatabaseTools(self.db)
        tools = db_tools.get_tools()
        tool_map = {}
        for tool in tools:
            tool_map[tool.name] = tool.func
        return tool_map
    
    def _build_tool_descriptions(self):
        db_tools = DatabaseTools(self.db)
        tools = db_tools.get_tools()
        descriptions = []
        
        for tool in tools:
            func = tool.func
            params = []
            if func.__code__.co_argcount > 1:
                args = func.__code__.co_varnames[1:]
                defaults = func.__defaults__ or ()
                for i, arg in enumerate(args):
                    default_val = defaults[i] if i < len(defaults) else None
                    if default_val is None:
                        params.append(arg)
                    else:
                        params.append(f"{arg}(可选)")
            
            param_str = ", ".join(params)
            descriptions.append(f"- {tool.name}({param_str}): {tool.description}")
        
        return "\n".join(descriptions)
    
    def _execute_tool(self, tool_name, params):
        tool_map = self._get_tool_map()
        if tool_name not in tool_map:
            return f"工具 {tool_name} 不存在"
        
        func = tool_map[tool_name]
        try:
            result = func(**params)
            return str(result)
        except Exception as e:
            return f"工具执行失败: {str(e)}"
    
    def chat(self, message: str, session_id: str = "default") -> str:
        if not settings.DEEPSEEK_API_KEY:
            return self._mock_chat(message)
        
        try:
            llm = self._get_llm()
            tool_descriptions = self._build_tool_descriptions()
            
            chat_history = self.get_session_history(session_id)
            
            system_prompt = f"""你是一个智能巡检系统的AI助手，负责帮助用户查询和分析巡检机器人的各项数据。

你的任务：
1. 根据用户的问题，判断是否需要调用工具获取数据
2. 如果需要调用工具，使用JSON格式输出工具调用指令，格式为：{{"tool_call": [{{"name": "工具名", "params": {{"参数名": "值"}}}}]}}
3. 如果不需要调用工具，可以直接回答用户的问题

可用工具：
{tool_descriptions}

告警等级说明：
- RED: 红色高危，需要立即处理
- ORANGE: 橙色预警，需要关注
- NORMAL: 一般提示，正常监控

机器人运行模式：
- 0: 待机
- 1: 自动巡检
- 2: 手动遥控
- 3: 充电中
- 4: 故障

巡检状态：
- 1: 进行中
- 2: 已完成
- 3: 异常中断

注意：
- 如果需要调用多个工具，请在tool_call数组中列出所有调用
- 如果不需要调用工具，请直接给出回答，不要输出JSON格式"""
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            for msg in chat_history.messages:
                if isinstance(msg, HumanMessage):
                    messages.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    messages.append({"role": "assistant", "content": msg.content})
            
            messages.append({"role": "user", "content": message})
            
            response = llm.invoke(messages)
            response_text = response.content
            
            try:
                json_data = json.loads(response_text)
                if "tool_call" in json_data:
                    tool_results = []
                    for call in json_data["tool_call"]:
                        tool_name = call["name"]
                        params = call.get("params", {})
                        result = self._execute_tool(tool_name, params)
                        tool_results.append(f"工具 {tool_name} 执行结果:\n{result}")
                    
                    tool_result_text = "\n\n".join(tool_results)
                    
                    analysis_prompt = f"""根据以下工具执行结果，为用户的问题提供详细的分析和回答：

用户问题：{message}

工具执行结果：
{tool_result_text}

请用中文进行总结分析，给出专业的建议。"""
                    
                    analysis_messages = [
                        {"role": "system", "content": "你是一个专业的巡检系统分析助手，请根据提供的数据进行分析回答。"},
                        {"role": "user", "content": analysis_prompt}
                    ]
                    
                    final_response = llm.invoke(analysis_messages)
                    answer = final_response.content
                else:
                    answer = response_text
            except json.JSONDecodeError:
                answer = response_text
            
            chat_history.add_message(HumanMessage(content=message))
            chat_history.add_message(AIMessage(content=answer))
            
            return answer
        except Exception as e:
            logger.error(f"Agent调用失败: {e}", exc_info=True)
            return self._mock_chat(message)
    
    def get_session_history(self, session_id: str) -> BaseChatMessageHistory:
        if session_id not in self._memory_store:
            self._memory_store[session_id] = InMemoryChatMessageHistory()
        return self._memory_store[session_id]
    
    def analyze_alarm(self, alarm_id: int) -> str:
        if not settings.DEEPSEEK_API_KEY:
            return self._mock_analyze_alarm(alarm_id)
        
        try:
            tool_map = self._get_tool_map()
            
            if "get_alarm_detail" in tool_map:
                alarm_data = tool_map["get_alarm_detail"](alarm_id)
            else:
                return self._mock_analyze_alarm(alarm_id)
            
            llm = self._get_llm()
            
            analysis_prompt = f"""请分析以下告警信息并给出专业的处理建议：

告警详情：
{alarm_data}

分析要求：
1. 评估告警的严重程度和潜在风险
2. 根据告警类型和等级，给出具体的处理步骤
3. 如果有传感器数据，请结合数据进行分析
4. 给出预防措施和改进建议
5. 使用中文回答，语气专业"""
            
            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            return response.content
        except Exception as e:
            logger.error(f"告警分析失败: {e}", exc_info=True)
            return self._mock_analyze_alarm(alarm_id)
    
    def analyze_report(self, robot_sn: str = None, start_time: str = None, end_time: str = None) -> str:
        if not settings.DEEPSEEK_API_KEY:
            return self._mock_analyze_report(robot_sn, start_time, end_time)
        
        try:
            tool_map = self._get_tool_map()
            
            report_data = ""
            if "get_daily_report" in tool_map:
                report_data += tool_map["get_daily_report"]() + "\n\n"
            if "get_sensor_statistics" in tool_map:
                report_data += tool_map["get_sensor_statistics"](robot_sn) + "\n\n"
            if "get_robot_statistics" in tool_map:
                report_data += tool_map["get_robot_statistics"]()
            
            llm = self._get_llm()
            
            analysis_prompt = f"""请分析以下巡检系统报表数据并给出专业的总结和建议：

报表数据：
{report_data}

分析要求：
1. 总结系统运行状态和环境监测情况
2. 分析温度、湿度、烟雾等环境指标的变化趋势
3. 评估巡检任务执行情况和机器人运行状态
4. 识别潜在风险和需要关注的问题
5. 给出优化建议和改进措施
6. 使用中文回答，结构清晰，专业详细"""
            
            response = llm.invoke([HumanMessage(content=analysis_prompt)])
            return response.content
        except Exception as e:
            logger.error(f"报表分析失败: {e}", exc_info=True)
            return self._mock_analyze_report(robot_sn, start_time, end_time)
    
    def _mock_chat(self, message: str) -> str:
        return f"【AI智能回复】\n您的问题: {message}\n\n提示: 当前未配置DEEPSEEK_API_KEY，智能体使用模拟模式。请在.env文件中配置DEEPSEEK_API_KEY以启用真实AI能力。"
    
    def _mock_analyze_alarm(self, alarm_id: int) -> str:
        return f"【AI告警分析】\n告警ID: {alarm_id}\n\n提示: 当前未配置DEEPSEEK_API_KEY，智能体使用模拟模式。请在.env文件中配置DEEPSEEK_API_KEY以启用真实AI分析能力。\n\n模拟分析建议：根据告警级别，建议立即进行现场核查，确认是否存在火灾隐患。"
    
    def _mock_analyze_report(self, robot_sn: str = None, start_time: str = None, end_time: str = None) -> str:
        return f"【AI报表分析】\n机器人: {robot_sn or '全部'}\n时间范围: {start_time or '开始'} ~ {end_time or '结束'}\n\n提示: 当前未配置DEEPSEEK_API_KEY，智能体使用模拟模式。请在.env文件中配置DEEPSEEK_API_KEY以启用真实AI分析能力。\n\n模拟分析结果: 系统已完成数据分析，当前环境监测数据整体处于正常范围。建议继续保持定期巡检，关注高温区域变化。"