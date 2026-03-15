"""
Chat Management API
"""

from fastapi import APIRouter
from domain.chat.schemas import ChatRequest
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Depends
from domain.chat.service.chat_service import ChatService
from dependencies.chat import get_chat_service
from sqlalchemy.orm import Session
from core.db import get_db

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/")
async def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    service: ChatService = Depends(get_chat_service),
):
    async def event_generator():
        async for token in service.stream_chat(db, req.question, req.session_id):
            yield token

    return StreamingResponse(event_generator(), media_type="text/plain")
