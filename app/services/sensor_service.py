from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.sensor import Sensor
from app.crud import sensor as sensor_crud, sensor_data as sensor_data_crud, thermal_data as thermal_data_crud
from app.schemas.environment import EnvironmentDataResponse

class SensorService:
    def get_sensor_list(self, db: Session) -> List[Sensor]:
        return sensor_crud.get_multi(db)

    def get_sensor_by_id(self, db: Session, sensor_id: str) -> Optional[Sensor]:
        return sensor_crud.get(db, sensor_id)

    def get_latest_temperature(self, db: Session) -> Dict:
        latest_data = sensor_data_crud.get_latest_all(db)
        
        if not latest_data:
            return {"value": 0, "unit": "°C", "updateTime": datetime.now().isoformat()}
        
        avg_temp = sum(d.temperature for d in latest_data) / len(latest_data)
        
        return {
            "value": round(avg_temp, 2),
            "unit": "°C",
            "updateTime": datetime.now().isoformat()
        }

    def get_latest_humidity(self, db: Session) -> Dict:
        latest_data = sensor_data_crud.get_latest_all(db)
        
        if not latest_data:
            return {"value": 0, "unit": "%", "updateTime": datetime.now().isoformat()}
        
        avg_humidity = sum(d.humidity for d in latest_data) / len(latest_data)
        
        return {
            "value": round(avg_humidity, 2),
            "unit": "%",
            "updateTime": datetime.now().isoformat()
        }

    def get_latest_gas(self, db: Session) -> Dict:
        latest_data = sensor_data_crud.get_latest_all(db)
        
        if not latest_data:
            return {"value": 0, "unit": "ppm", "updateTime": datetime.now().isoformat()}
        
        max_gas = max(d.smoke_level for d in latest_data)
        
        return {
            "value": round(max_gas, 2),
            "unit": "ppm",
            "updateTime": datetime.now().isoformat()
        }

    def get_latest_environment_data(self, db: Session) -> EnvironmentDataResponse:
        latest_data = sensor_data_crud.get_latest_all(db)
        
        if not latest_data:
            return EnvironmentDataResponse()
        
        avg_temp = sum(d.temperature for d in latest_data) / len(latest_data)
        avg_humidity = sum(d.humidity for d in latest_data) / len(latest_data)
        max_smoke = max(d.smoke_level for d in latest_data)
        
        latest_thermal = thermal_data_crud.get_latest(db)
        max_thermal_temp = latest_thermal.max_temp_value if latest_thermal else None
        
        return EnvironmentDataResponse(
            temperature=round(avg_temp, 2),
            humidity=round(avg_humidity, 2),
            gas=max_smoke,
            updateTime=datetime.now().isoformat()
        )

    def get_environment_history(self, db: Session, start_time: str, end_time: str, interval: str = "1m") -> List[Dict]:
        from datetime import datetime as dt, timedelta
        start = dt.fromisoformat(start_time)
        end = dt.fromisoformat(end_time)
        
        data = sensor_data_crud.get_multi_by_time_range(db, start, end)
        
        result = []
        current_interval = start
        interval_minutes = {"1m": 1, "5m": 5, "15m": 15, "1h": 60}[interval]
        
        while current_interval < end:
            next_interval = current_interval + timedelta(minutes=interval_minutes)
            interval_data = [d for d in data if current_interval <= d.receive_time < next_interval]
            
            if interval_data:
                result.append({
                    "time": current_interval.isoformat(),
                    "temperature": round(sum(d.temperature for d in interval_data) / len(interval_data), 2),
                    "humidity": round(sum(d.humidity for d in interval_data) / len(interval_data), 2),
                    "gas": max(d.smoke_level for d in interval_data)
                })
            
            current_interval = next_interval
        
        return result