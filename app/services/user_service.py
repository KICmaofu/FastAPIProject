from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.user import User
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    def get_user_list(self, db: Session, page: int = 1, size: int = 20, role: Optional[str] = None) -> Dict:
        skip = (page - 1) * size
        
        if role:
            users = user_crud.get_multi_by_role(db, role, skip=skip, limit=size)
            total = user_crud.count_by_role(db, role)
        else:
            users = user_crud.get_multi_active(db, skip=skip, limit=size)
            total = user_crud.count(db)
        
        return {
            "list": users,
            "total": total,
            "page": page
        }

    def get_user_by_id(self, db: Session, user_id: str) -> Optional[User]:
        return user_crud.get(db, user_id)

    def get_current_user(self, db: Session, user_id: str) -> Optional[User]:
        return user_crud.get(db, user_id)

    def create_user(self, db: Session, data: UserCreate) -> Optional[User]:
        if user_crud.get_by_username(db, data.username):
            return None
        
        if user_crud.get_by_phone(db, data.phone):
            return None
        
        from app.utils.security import get_password_hash
        hashed_password = get_password_hash(data.password)
        
        user_data = {
            "username": data.username,
            "phone": data.phone,
            "password_hash": hashed_password,
            "role": data.role
        }
        
        return user_crud.create(db, obj_in=user_data)

    def update_user(self, db: Session, user_id: str, data: UserUpdate, current_user: User) -> Optional[User]:
        user = user_crud.get(db, user_id)
        if not user:
            return None
        
        update_data = data.dict(exclude_unset=True)
        
        if "role" in update_data and current_user.role != "admin":
            del update_data["role"]
        
        if "username" in update_data and user_crud.get_by_username(db, update_data["username"]):
            return None
        
        return user_crud.update(db, db_obj=user, obj_in=update_data)

    def delete_user(self, db: Session, user_id: str) -> bool:
        user = user_crud.get(db, user_id)
        if not user:
            return False
        user.is_deleted = True
        db.commit()
        return True