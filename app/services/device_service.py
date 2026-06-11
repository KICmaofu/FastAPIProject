from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.device import Device
from app.crud import device as device_crud
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceStatsResponse

class DeviceService:
    def get_device_stats(self, db: Session) -> DeviceStatsResponse:
        total = device_crud.count(db)
        online = device_crud.count_by_status(db, "online")
        offline = device_crud.count_by_status(db, "offline")
        warning = device_crud.count_by_status(db, "warning")
        
        return DeviceStatsResponse(
            total=total,
            online=online,
            offline=offline,
            warning=warning
        )

    def get_device_list(self, db: Session, page: int = 1, size: int = 20, status: Optional[str] = None) -> Dict:
        skip = (page - 1) * size
        
        if status:
            devices = device_crud.get_multi_by_status(db, status, skip=skip, limit=size)
            total = device_crud.count_by_status(db, status)
        else:
            devices = device_crud.get_multi(db, skip=skip, limit=size)
            total = device_crud.count(db)
        
        return {
            "list": devices,
            "total": total,
            "page": page
        }

    def get_device_by_id(self, db: Session, device_id: str) -> Optional[Device]:
        return device_crud.get(db, device_id)

    def create_device(self, db: Session, data: DeviceCreate) -> Device:
        device_data = data.model_dump(exclude={'password'})
        return device_crud.create(db, obj_in=device_data)

    def update_device(self, db: Session, device_id: str, data: DeviceUpdate) -> Optional[Device]:
        device = device_crud.get(db, device_id)
        if not device:
            return None
        update_data = data.model_dump(exclude={'password'}, exclude_unset=True)
        return device_crud.update(db, db_obj=device, obj_in=update_data)

    def delete_device(self, db: Session, device_id: str) -> bool:
        device = device_crud.get(db, device_id)
        if not device:
            return False
        device.is_deleted = True
        db.commit()
        return True