"""
Chat Management API
"""

from fastapi import APIRouter, Path
import uuid
from dependencies.chat import get_session_service
from sqlalchemy.orm import Session
from core.db import get_db
from fastapi import APIRouter, Depends
from domain.chat.service.session_service import SessionService

router = APIRouter(prefix="/chat/sessions", tags=["chat"])


@router.post("/")
async def create():
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}


@router.get("/")
def get_sessions(
    db: Session = Depends(get_db),
    service: SessionService = Depends(get_session_service),
):
    return service.get_sessions(db)


@router.get("/{session_id}/messages")
def list_session_messages(
    db: Session = Depends(get_db),
    service: SessionService = Depends(get_session_service),
    session_id: str = Path(..., description="조회할 세션 ID"),
):
    return service.get_messages(db, session_id)
