from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.message import Message
from app.crud.base import CRUDBase

class CRUDMessage(CRUDBase[Message]):
    def __init__(self):
        super().__init__(Message)

    def get_multi_by_receiver(self, db: Session, receiver_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(Message.receiver_id == receiver_id, Message.is_deleted == False).order_by(desc(Message.create_time)).offset(skip).limit(limit).all()

    def get_multi_by_type(self, db: Session, type: str, receiver_id: str, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(Message.type == type, Message.receiver_id == receiver_id, Message.is_deleted == False).order_by(desc(Message.create_time)).offset(skip).limit(limit).all()

    def count_unread(self, db: Session, receiver_id: str) -> int:
        return db.query(Message).filter(Message.receiver_id == receiver_id, Message.is_read == False, Message.is_deleted == False).count()

    def mark_as_read(self, db: Session, message_id: str, receiver_id: str):
        message = db.query(Message).filter(Message.id == message_id, Message.receiver_id == receiver_id).first()
        if message:
            message.is_read = True
            db.commit()
            db.refresh(message)
        return message

    def mark_all_read(self, db: Session, receiver_id: str):
        db.query(Message).filter(Message.receiver_id == receiver_id, Message.is_read == False, Message.is_deleted == False).update({"is_read": True})
        db.commit()