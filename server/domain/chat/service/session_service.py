# domain/chat/services/session_service.py

from sqlalchemy.orm import Session
from domain.chat.repository import ChatRepository
from domain.chat.chains.summary_chain import SummaryChain


class SessionService:

    def __init__(self, repo: ChatRepository):
        self.repo = repo

    def get_sessions(self, db: Session):

        sessions = self.repo.get_sessions(db)
        result = [
            {"session_id": s.session_id, "title": s.title or "제목 없음"}
            for s in sessions
        ]
        return result

    def get_messages(self, db: Session, session_id: str):
        messages = self.repo.get_recent_messages(db, session_id)

        result = [
            {
                "turn": m.turn,
                "role": m.role,
                "content": m.content,
            }
            for m in messages
        ]

        return result
