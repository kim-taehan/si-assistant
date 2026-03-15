from sqlalchemy import Column, BigInteger, String, Text, DateTime, func
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class ChatSession(Base):
    __tablename__ = "chat_session"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False)
    session_id = Column(String(100), nullable=False, index=True)
    title = Column(String(200), nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(BigInteger, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    turn = Column(BigInteger, nullable=False)  # 🔹 추가된 컬럼 (대화 턴)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
