# domain/chat/services/chat_service.py
import asyncio
from domain.chat.agent.graph import build_chat_graph
from sqlalchemy.orm import Session
from langchain_core.messages import HumanMessage, AIMessage
from domain.chat.repository import ChatRepository
from domain.chat.chains.summary_chain import SummaryChain
from langchain_core.messages import HumanMessage, AIMessage
from core.db import SessionLocal

from langchain_teddynote import logging
from dotenv import load_dotenv

load_dotenv()

logging.langsmith("SI_ASSISTANT")


class ChatService:
    def __init__(self, repo: ChatRepository, summary_chain: SummaryChain):
        self.repo = repo
        self.summary_chain = summary_chain
        self.chat_graph = build_chat_graph()

    async def stream_chat(self, db: Session, question: str, session_id: str):

        session = self.repo.get_session(db, session_id)
        conversation_summary = session.summary if session and session.summary else ""

        recent_msgs = self.repo.get_recent_messages(db, session_id)

        messages = []

        for m in recent_msgs:
            print(f"role = {m.role}")
            print(f"content = {m.content}")
            if m.role == "user":
                messages.append(HumanMessage(content=m.content))
            elif m.role == "assistant":
                messages.append(AIMessage(content=m.content))

        messages.append(HumanMessage(content=question))

        ai_answer = ""

        yield "🔍 질문을 분석중입니다...\n\n"

        async for event in self.chat_graph.astream_events(
            {"messages": messages, "conversation_summary": conversation_summary},
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
                    # chunk = event["data"]["chunk"]

                    # if chunk.content:
                    #     ai_answer += chunk.content
                    #     yield chunk.content

        # --------------------------------
        # 백그라운드에서 DB 저장 + Summary
        # --------------------------------

        print("call save_chat_history")
        asyncio.create_task(
            self.save_chat_history(
                session_id=session_id,
                question=question,
                ai_answer=ai_answer,
                conversation_summary=conversation_summary,
            )
        )
        # # ------------------------
        # # Summary 생성
        # # ------------------------

        # summary = self.summary_chain.invoke(
        #     conversation_summary, [HumanMessage(question), AIMessage(ai_answer)]
        # )

        # session = self.repo.save_session(
        #     db,
        #     session_id,
        #     "kobe",
        #     summary.title,
        #     summary.summary,
        # )

        # # ------------------------
        # # 메시지 저장
        # # ------------------------

        # turn = self.repo.get_next_turn(db, session_id)

        # user_chat_message = self.repo.save_message(
        #     db, session_id, "user", question, turn
        # )

        # ai_chat_message = self.repo.save_message(
        #     db, session_id, "assistant", ai_answer, turn
        # )

        # db.commit()

        # db.refresh(session)
        # db.refresh(user_chat_message)
        # db.refresh(ai_chat_message)

    async def save_chat_history(
        self,
        session_id: str,
        question: str,
        ai_answer: str,
        conversation_summary: str,
    ):
        """
        스트리밍 응답 이후 백그라운드에서 실행되는 작업
        """
        print("call save_chat_history...")
        db = SessionLocal()

        try:
            summary = self.summary_chain.invoke(
                conversation_summary,
                [HumanMessage(question), AIMessage(ai_answer)],
            )

            session = self.repo.save_session(
                db,
                session_id,
                "kobe",
                summary.title,
                summary.summary,
            )

            turn = self.repo.get_next_turn(db, session_id)

            user_chat_message = self.repo.save_message(
                db, session_id, "user", question, turn
            )

            ai_chat_message = self.repo.save_message(
                db, session_id, "assistant", ai_answer, turn
            )

            db.commit()

            db.refresh(session)
            db.refresh(user_chat_message)
            db.refresh(ai_chat_message)

        except Exception as e:
            print("❌ Chat history save error:", e)

        finally:
            db.close()
