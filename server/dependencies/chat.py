from fastapi import Depends

from domain.chat.repository import ChatRepository
from domain.chat.service.chat_service import ChatService
from domain.chat.service.session_service import SessionService
from domain.chat.service.chat_completed_handler import ChatCompletedHandler
from domain.chat.chains.summary_chain import SummaryChain
from domain.chat.chains.title_chain import TitleChain
from core.llm import llm
from core.event_bus import event_bus


def get_chat_repository() -> ChatRepository:
    return ChatRepository()


def get_summary_chain() -> SummaryChain:
    return SummaryChain(llm)


def get_title_chain() -> TitleChain:
    return TitleChain(llm)


def get_chat_completed_handler(
    repo: ChatRepository = Depends(get_chat_repository),
    summary_chain: SummaryChain = Depends(get_summary_chain),
    title_chain: TitleChain = Depends(get_title_chain),
) -> ChatCompletedHandler:
    return ChatCompletedHandler(
        repo=repo, summary_chain=summary_chain, title_chain=title_chain
    )


def get_chat_service(
    repo: ChatRepository = Depends(get_chat_repository),
) -> ChatService:
    return ChatService(repo, event_bus)


def get_session_service(
    repo: ChatRepository = Depends(get_chat_repository),
) -> SessionService:
    return SessionService(repo=repo)
