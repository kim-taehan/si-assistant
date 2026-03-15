# repository/document_repository.py

from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
from domain.chat.models import ChatMessage, ChatSession


class ChatRepository:

    def get_sessions(self, db: Session):
        """Get all sessions."""
        msgs = db.query(ChatSession).order_by(ChatSession.created_at.asc()).all()
        # 메시지를 오래된 순으로 정렬
        return list(reversed(msgs))

    def get_session(self, db: Session, session_id: str):
        """Get a session by ID."""
        session_data = (
            db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        )
        return session_data

    def save_session(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        title: Optional[str] = None,
        summary: Optional[str] = None,
    ):
        """Save or update a session."""
        session_data = (
            db.query(ChatSession).filter(ChatSession.session_id == session_id).first()
        )

        if session_data:
            # 존재하면 업데이트
            if title is not None:
                session_data.title = title
            if summary is not None:
                session_data.summary = summary
        else:
            # 없으면 새로 삽입
            session_data = ChatSession(
                session_id=session_id, user_id=user_id, title=title, summary=summary
            )
            db.add(session_data)
        return session_data

    def get_recent_messages(self, db: Session, session_id: str, limit: int = 3):
        msgs = (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit * 2)
            .all()
        )

        return list(reversed(msgs))

    def get_next_turn(self, db: Session, session_id: str) -> int:
        """다음 turn 계산"""
        max_turn = (
            db.query(func.max(ChatMessage.turn))
            .filter(ChatMessage.session_id == session_id)
            .scalar()
        )

        return (max_turn or 0) + 1

    def save_message(
        self,
        db: Session,
        session_id: str,
        role: str,
        content: str,
        turn: int,
    ):
        """메시지 저장"""
        message = ChatMessage(
            session_id=session_id,
            turn=turn,
            role=role,
            content=content,
            created_at=datetime.utcnow(),
        )

        db.add(message)
        return message
