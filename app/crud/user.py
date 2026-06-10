from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.crud.base import CRUDBase

class CRUDUser(CRUDBase[User]):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username, User.is_deleted == False).first()

    def get_by_phone(self, db: Session, phone: str) -> Optional[User]:
        return db.query(User).filter(User.phone == phone, User.is_deleted == False).first()

    def get_multi_by_role(self, db: Session, role: str, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).filter(User.role == role, User.is_deleted == False).offset(skip).limit(limit).all()

    def get_multi_active(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).filter(User.status == True, User.is_deleted == False).offset(skip).limit(limit).all()

    def count(self, db: Session) -> int:
        return db.query(User).filter(User.is_deleted == False).count()

    def count_by_role(self, db: Session, role: str) -> int:
        return db.query(User).filter(User.role == role, User.is_deleted == False).count()