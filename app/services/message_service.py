from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.message import Message
from app.crud import message as message_crud

class MessageService:
    def get_message_list(self, db: Session, user_id: str, type: Optional[str] = None, page: int = 1, size: int = 20) -> Dict:
        skip = (page - 1) * size
        
        if type:
            messages = message_crud.get_multi_by_type(db, type, user_id, skip=skip, limit=size)
            total = db.query(Message).filter(Message.type == type, Message.receiver_id == user_id, Message.is_deleted == False).count()
        else:
            messages = message_crud.get_multi_by_receiver(db, user_id, skip=skip, limit=size)
            total = db.query(Message).filter(Message.receiver_id == user_id, Message.is_deleted == False).count()
        
        return {
            "list": messages,
            "total": total,
            "page": page
        }

    def get_message_by_id(self, db: Session, message_id: str, user_id: str) -> Optional[Message]:
        message = message_crud.get(db, message_id)
        if message and message.receiver_id == user_id and not message.is_deleted:
            return message
        return None

    def mark_as_read(self, db: Session, message_id: str, user_id: str) -> bool:
        message = message_crud.mark_as_read(db, message_id, user_id)
        return message is not None

    def mark_all_read(self, db: Session, user_id: str) -> None:
        message_crud.mark_all_read(db, user_id)

    def delete_message(self, db: Session, message_id: str, user_id: str) -> bool:
        message = message_crud.get(db, message_id)
        if message and message.receiver_id == user_id:
            message.is_deleted = True
            db.commit()
            return True
        return False

    def create_message(self, db: Session, title: str, content: Optional[str] = None, type: Optional[str] = None, receiver_id: str = "0") -> Message:
        message_data = {
            "title": title,
            "content": content,
            "type": type,
            "receiver_id": receiver_id
        }
        return message_crud.create(db, obj_in=message_data)