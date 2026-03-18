# domain/chat/services/chat_service.py
import asyncio
from domain.chat.agent.graph import build_chat_graph
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from domain.chat.repository import ChatRepository
from domain.chat.chains.summary_chain import SummaryChain
from domain.chat.chains.title_chain import TitleChain
from langchain_core.messages import HumanMessage, AIMessage
from core.db import SessionLocal

from langchain_teddynote import logging
from dotenv import load_dotenv
from core.event_bus import EventBus

# load_dotenv()
# logging.langsmith("SI_ASSISTANT")


class ChatService:

    def __init__(self, repo: ChatRepository, event_bus: EventBus):
        self.repo = repo
        self.event_bus = event_bus
        self.chat_graph = build_chat_graph()

    async def stream_chat(self, db: Session, question: str, session_id: str):
        conversation_summary = self.__get_conversation_summary(db, session_id)
        messages = self.__get_messages(db, question, session_id)

        yield "🔍 질문을 분석중입니다...\n\n"
        ai_answer = ""
        async for event in self.chat_graph.astream_events(
            {
                "messages": messages,
                "conversation_summary": conversation_summary,
                "question": question,
                "session_id": session_id,
            },
            version="v1",
        ):
            event_type = event.get("event")
            # tool 실행 안내
            if event_type == "on_tool_start":
                if event.get("name") == "get_user_information":
                    yield "👤 사용자 정보를 조회하고 있습니다...\n\n"
                if event.get("name") == "search_documents":
                    yield "📚 문서를 조회하고 있습니다...\n\n"
            # token streaming
            if event_type == "on_chat_model_stream":
                node = event.get("metadata", {}).get("langgraph_node")
                if node == "chatbot":
                    chunk = event["data"]["chunk"]
                    content = getattr(chunk, "content", None)
                    if isinstance(content, str) and content:
                        ai_answer += content
                        yield content

        # --------------------------------
        # 백그라운드에서 DB 저장 + Summary
        # --------------------------------
        turn = self.repo.get_next_turn(db, session_id)
        await self.event_bus.publish(
            {
                "type": "chat.completed",
                "data": {
                    "session_id": session_id,
                    "question": question,
                    "ai_answer": ai_answer,
                    "turn": turn,
                    "conversation_summary": conversation_summary,
                },
            }
        )
        print("submit 완료")

    def __get_conversation_summary(self, db: Session, session_id: str):
        session = self.repo.get_session(db, session_id)
        return session.summary if session and session.summary else ""

    def __get_messages(self, db: Session, question: str, session_id: str):
        recent_msgs = self.repo.get_recent_messages(db, session_id)

        messages = []
        for m in recent_msgs:
            if m.role == "user":
                messages.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                messages.append(AIMessage(content=m.content))

        messages.append(HumanMessage(content=question))
        return messages

    # async def save_chat_history(
    #     self,
    #     session_id: str,
    #     question: str,
    #     ai_answer: str,
    #     conversation_summary: str,
    # ):
    #     """
    #     스트리밍 응답 이후 백그라운드에서 실행되는 작업
    #     """
    #     print("call save_chat_history...")
    #     db = SessionLocal()

    #     try:

    #         turn = self.repo.get_next_turn(db, session_id)
    #         print(f"turn={turn}")
    #         title = None
    #         summary = conversation_summary

    #         # # ---------------------
    #         # # Title (첫 턴만)
    #         # # ---------------------
    #         if turn == 1:
    #             title_result = self.title_chain.invoke(question)
    #             title = title_result.title

    #         # -------------------
    #         # Summary (3턴 이후)
    #         # -------------------
    #         if turn % 3 == 0:
    #             summary_result = self.summary_chain.invoke(
    #                 conversation_summary,
    #                 f"User: {question}\nAssistant: {ai_answer}",
    #             )

    #             summary = summary_result.summary

    #         session = self.repo.save_session(
    #             db,
    #             session_id,
    #             "kobe",
    #             title,
    #             summary,
    #         )

    #         user_chat_message = self.repo.save_message(
    #             db, session_id, "user", question, turn
    #         )

    #         ai_chat_message = self.repo.save_message(
    #             db, session_id, "assistant", ai_answer, turn
    #         )

    #         db.commit()

    #         db.refresh(session)
    #         db.refresh(user_chat_message)
    #         db.refresh(ai_chat_message)

    #     except Exception as e:
    #         print("❌ Chat history save error:", e)

    #     finally:
    #         db.close()
