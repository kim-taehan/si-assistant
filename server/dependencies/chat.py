from fastapi import Depends

from domain.chat.repository import ChatRepository
from domain.chat.service.chat_service import ChatService
from domain.chat.service.session_service import SessionService
from domain.chat.chains.summary_chain import SummaryChain
from core.llm import llm


def get_chat_repository() -> ChatRepository:
    return ChatRepository()


def get_summary_chain() -> SummaryChain:
    return SummaryChain(llm)


def get_chat_service(
    repo: ChatRepository = Depends(get_chat_repository),
    summary_chain: SummaryChain = Depends(get_summary_chain),
) -> ChatService:
    return ChatService(repo, summary_chain)


def get_session_service(
    repo: ChatRepository = Depends(get_chat_repository),
) -> SessionService:
    return SessionService(repo=repo)
