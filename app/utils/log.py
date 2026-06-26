from sqlalchemy.orm import Session
from app.models.sys_log import SysLog
from datetime import datetime
from typing import Optional

def add_audit_log(
    db: Session,
    username: str,
    module: str,
    operation: str,
    ip_address: str = "",
    detail: Optional[dict] = None
):
    log = SysLog(
        username=username,
        module=module,
        operation=operation,
        ip_address=ip_address,
        detail=detail if detail else {}
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log