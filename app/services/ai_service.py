from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.crud import sensor_data as sensor_data_crud
from app.schemas.ai import AIPredictionRequest, AIPredictionResponse, AIDetectRequest, AIQueryRequest, AIReportRequest
from app.config.settings import settings
import ollama
import os

class AIService:
    def __init__(self):
        os.environ['OLLAMA_HOST'] = settings.OLLAMA_HOST
    
    def _call_ollama(self, prompt: str) -> str:
        try:
            response = ollama.generate(
                model=settings.OLLAMA_MODEL,
                prompt=prompt,
                options={"timeout": settings.OLLAMA_TIMEOUT}
            )
            return response.get("response", "")
        except Exception as e:
            return f"调用AI模型时发生错误: {str(e)}"
    def predict_environment(self, db: Session, hours: int) -> AIPredictionResponse:
        latest_data = sensor_data_crud.get_latest_all(db)
        
        if not latest_data:
            return AIPredictionResponse(predictions=[])
        
        avg_temp = sum(d.temperature for d in latest_data) / len(latest_data)
        avg_humidity = sum(d.humidity for d in latest_data) / len(latest_data)
        
        predictions = []
        current_time = datetime.now()
        
        for i in range(1, hours + 1):
            predict_time = current_time + timedelta(hours=i)
            temp_trend = 0.5 if i % 2 == 0 else -0.3
            humidity_trend = 0.2
            
            predictions.append({
                "time": predict_time.isoformat(),
                "temperature": round(avg_temp + temp_trend * i, 2),
                "humidity": round(avg_humidity + humidity_trend * i, 2),
                "riskLevel": "low"
            })
        
        return AIPredictionResponse(predictions=predictions)

    def predict_device_failure(self, db: Session, device_id: str) -> Dict:
        return {
            "deviceId": device_id,
            "riskLevel": "low",
            "predictTime": (datetime.now() + timedelta(hours=24)).isoformat(),
            "confidence": 0.85
        }

    def detect_anomalies(self, db: Session, data: List[Dict]) -> Dict:
        anomalies = []
        
        for i, item in enumerate(data):
            if "value" in item and item["value"] > 100:
                anomalies.append({
                    "index": i,
                    "type": "high_value",
                    "message": f"检测到异常高值: {item['value']}"
                })
        
        return {
            "anomalies": anomalies,
            "total": len(anomalies)
        }

    def query_natural_language(self, db: Session, query: str) -> Dict:
        prompt = f"""你是一个智能巡检系统的AI助手。请根据用户的问题提供专业、准确的回答。

用户问题: {query}

请用中文详细回答这个问题。"""
        
        answer = self._call_ollama(prompt)
        
        return {
            "query": query,
            "answer": answer,
            "confidence": 0.95
        }

    def generate_report(self, db: Session, report_type: str, startTime: Optional[str] = None, endTime: Optional[str] = None) -> Dict:
        if not startTime:
            start = datetime.now() - timedelta(days=1)
        else:
            start = datetime.fromisoformat(startTime)
        
        if not endTime:
            end = datetime.now()
        else:
            end = datetime.fromisoformat(endTime)
        
        data_count = sensor_data_crud.get_multi_by_time_range(db, start, end)
        
        prompt = f"""你是一个智能巡检系统的报告生成助手。请根据以下信息生成一份专业的{report_type}报告。

报告类型: {report_type}
时间范围: {start} 到 {end}
数据点数: {len(data_count)}

请生成一份详细的中文报告，包括：
1. 报告概述
2. 数据分析摘要
3. 关键发现
4. 建议与总结

报告风格要专业、简洁、易懂。"""
        
        summary = self._call_ollama(prompt)
        
        return {
            "type": report_type,
            "startTime": start.isoformat(),
            "endTime": end.isoformat(),
            "dataPoints": len(data_count),
            "summary": summary
        }

    def analyze_environment(self, db: Session) -> Dict:
        latest_data = sensor_data_crud.get_latest_all(db)
        
        if not latest_data:
            return {"status": "no_data"}
        
        avg_temp = sum(d.temperature for d in latest_data) / len(latest_data)
        avg_humidity = sum(d.humidity for d in latest_data) / len(latest_data)
        max_smoke = max(d.smoke_level for d in latest_data)
        
        prompt = f"""你是一个智能环境分析助手。请根据以下环境监测数据进行专业分析并给出建议。

环境数据:
- 平均温度: {round(avg_temp, 2)}°C
- 平均湿度: {round(avg_humidity, 2)}%
- 最大烟雾浓度: {max_smoke}

请分析：
1. 当前环境状态评估
2. 潜在风险识别
3. 针对当前环境状况的具体建议

请用中文给出专业、简洁的分析报告。"""
        
        analysis = self._call_ollama(prompt)
        
        return {
            "avgTemperature": round(avg_temp, 2),
            "avgHumidity": round(avg_humidity, 2),
            "maxSmokeLevel": max_smoke,
            "status": "normal" if max_smoke < 50 else "warning",
            "analysis": analysis
        }