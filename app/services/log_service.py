from datetime import datetime
from sqlalchemy.orm import Session
from app.models.system_log import SystemLog

def log_operation(
    db: Session,
    level: str,
    module: str,
    content: str,
    user_id: str = None,
    ip_address: str = None
):
    log = SystemLog(
        level=level,
        module=module,
        content=content,
        user_id=user_id,
        ip_address=ip_address,
        create_time=datetime.now()
    )
    db.add(log)
    db.commit()
    return log

def log_robot_operation(
    db: Session,
    operation: str,
    robot_id: str,
    user_id: str,
    username: str,
    success: bool,
    details: str = None,
    ip_address: str = None
):
    content = f"机器人{operation} - 机器人ID:{robot_id}, 操作者:{username}"
    if details:
        content += f", 详情:{details}"
    content += f", 结果:{'成功' if success else '失败'}"
    
    return log_operation(
        db=db,
        level="info" if success else "warn",
        module="robot_management",
        content=content,
        user_id=user_id,
        ip_address=ip_address
    )
