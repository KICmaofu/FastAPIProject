from typing import Optional, Tuple
from sqlalchemy.orm import Session
from datetime import timedelta
from app.models.user import User
from app.crud import user as user_crud
from app.utils.security import verify_password, get_password_hash, create_access_token
from app.config.settings import settings

class AuthService:
    def login(self, db: Session, username: Optional[str] = None, phone: Optional[str] = None, password: str = None) -> Tuple[Optional[str], Optional[User]]:
        if not password:
            return None, None
            
        db_user = None
        if username:
            db_user = user_crud.get_by_username(db, username)
        elif phone:
            db_user = user_crud.get_by_phone(db, phone)
        
        if not db_user:
            return None, None
        
        if not verify_password(password, db_user.password_hash):
            return None, None
        
        access_token_expires = timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": db_user.id}, expires_delta=access_token_expires
        )
        
        return access_token, db_user

    def register(self, db: Session, username: str, phone: str, password: str) -> Optional[User]:
        if user_crud.get_by_username(db, username):
            return None
        
        if user_crud.get_by_phone(db, phone):
            return None
        
        hashed_password = get_password_hash(password)
        user_data = {
            "username": username,
            "phone": phone,
            "password_hash": hashed_password,
            "role": "viewer"
        }
        
        return user_crud.create(db, obj_in=user_data)

    def reset_password(self, db: Session, phone: str, new_password: str) -> bool:
        db_user = user_crud.get_by_phone(db, phone)
        if not db_user:
            return False
        
        hashed_password = get_password_hash(new_password)
        user_crud.update(db, db_obj=db_user, obj_in={"password_hash": hashed_password})
        return True

    def get_user_permissions(self, user: User) -> list:
        permissions = []
        if user.role == "admin":
            permissions = ["view", "edit", "delete", "control", "manage"]
        elif user.role == "operator":
            permissions = ["view", "edit", "control"]
        else:
            permissions = ["view"]
        return permissions