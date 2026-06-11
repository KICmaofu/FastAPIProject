from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.robot import Robot
from app.crud import robot as robot_crud, sensor_data as sensor_data_crud
from app.schemas.robot import RobotCreate, RobotUpdate, RobotPositionResponse

class RobotService:
    def get_robot_list(self, db: Session, page: int = 1, size: int = 10, status: Optional[str] = None) -> Dict:
        skip = (page - 1) * size
        
        if status:
            robots = robot_crud.get_multi_by_status(db, status, skip=skip, limit=size)
            total = robot_crud.count_by_status(db, status)
        else:
            robots = robot_crud.get_multi_active(db, skip=skip, limit=size)
            total = robot_crud.count(db)
        
        # 转换为字典列表
        robot_list = []
        for robot in robots:
            robot_list.append({
                "id": robot.id,
                "name": robot.name,
                "model": robot.model,
                "battery": float(robot.battery) if robot.battery else 0,
                "status": robot.status,
                "location": robot.location,
                "speed": float(robot.speed) if robot.speed else 0.0
            })
        
        return {
            "list": robot_list,
            "total": total,
            "page": page
        }

    def get_robot_by_id(self, db: Session, robot_id: str) -> Optional[Robot]:
        return robot_crud.get(db, robot_id)

    def create_robot(self, db: Session, data: RobotCreate) -> Robot:
        robot_data = data.dict()
        return robot_crud.create(db, obj_in=robot_data)

    def update_robot(self, db: Session, robot_id: str, data: RobotUpdate) -> Optional[Robot]:
        robot = robot_crud.get(db, robot_id)
        if not robot:
            return None
        update_data = data.dict(exclude_unset=True)
        return robot_crud.update(db, db_obj=robot, obj_in=update_data)

    def delete_robot(self, db: Session, robot_id: str) -> bool:
        robot = robot_crud.get(db, robot_id)
        if not robot:
            return False
        robot.is_deleted = True
        db.commit()
        return True

    def get_positions(self, db: Session, robot_id: Optional[str] = None) -> List[RobotPositionResponse]:
        if robot_id:
            robot = robot_crud.get(db, robot_id)
            if not robot:
                return []
            latest_pos = robot_crud.get_latest_position(db, robot_id)
            if latest_pos:
                return [RobotPositionResponse(
                    id=robot.id,
                    x=latest_pos.x,
                    y=latest_pos.y,
                    battery=latest_pos.battery,
                    status=robot.status,
                    speed=latest_pos.speed
                )]
            return []
        else:
            robots = robot_crud.get_multi_active(db)
            result = []
            for robot in robots:
                latest_pos = robot_crud.get_latest_position(db, robot.id)
                if latest_pos:
                    result.append(RobotPositionResponse(
                        id=robot.id,
                        x=latest_pos.x,
                        y=latest_pos.y,
                        battery=latest_pos.battery,
                        status=robot.status,
                        speed=latest_pos.speed
                    ))
            return result

    def control_robot(self, db: Session, robot_id: str, action: str, speed: float = 1, duration: Optional[float] = None) -> bool:
        robot = robot_crud.get(db, robot_id)
        if not robot:
            return False
        
        if robot.status == "offline":
            return False
        
        valid_actions = ["move", "stop", "turn_left", "turn_right"]
        if action not in valid_actions:
            return False
        
        if action == "stop":
            robot.status = "idle"
            robot.speed = 0.0
        elif action == "move":
            robot.status = "moving"
            robot.speed = speed
        elif action in ["turn_left", "turn_right"]:
            robot.status = "moving"
        
        robot.update_time = datetime.now()
        db.commit()
        return True