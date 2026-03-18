# dependencies/chat/factories.py
from domain.chat.repository import ChatRepository
from domain.chat.service.chat_completed_handler import ChatCompletedHandler
from domain.chat.chains.summary_chain import SummaryChain
from domain.chat.chains.title_chain import TitleChain
from core.llm import llm


def create_chat_completed_handler() -> ChatCompletedHandler:
    repo = ChatRepository()
    summary_chain = SummaryChain(llm)
    title_chain = TitleChain(llm)
    return ChatCompletedHandler(
        repo=repo, summary_chain=summary_chain, title_chain=title_chain
    )
