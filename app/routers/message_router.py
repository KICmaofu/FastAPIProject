from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.config.database import get_db
from app.dependencies.auth import get_current_active_user
from app.models.user import User
from app.services import message_service
from app.schemas.message import MessageResponse, MessageListResponse
from app.utils.response import success_response

router = APIRouter(prefix="/api/messages", tags=["消息模块"])

@router.get("", summary="获取消息列表")
async def get_message_list(
    type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    result = message_service.get_message_list(db, current_user.id, type, page, size)

    message_list = []
    for msg in result["list"]:
        message_list.append(MessageResponse(
            id=msg.id,
            title=msg.title,
            content=msg.content,
            type=msg.type,
            time=msg.create_time.isoformat(),
            unread=not msg.is_read
        ))

    return success_response(data={
        "list": message_list,
        "total": result["total"],
        "page": result["page"]
    })

@router.put("/{messageId}/read", summary="标记消息已读")
async def mark_message_read(
    messageId: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    success = message_service.mark_as_read(db, messageId, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    return success_response(message="标记成功")

@router.put("/read-all", summary="标记所有消息已读")
async def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    message_service.mark_all_read(db, current_user.id)
    return success_response(message="全部标记成功")

@router.delete("/{messageId}", summary="删除消息")
async def delete_message(
    messageId: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    success = message_service.delete_message(db, messageId, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="消息不存在")
    return success_response(message="删除成功")
