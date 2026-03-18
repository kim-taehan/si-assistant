from core.event_bus import EventHandler
from core.db import SessionLocal
from domain.chat.repository import ChatRepository
from domain.chat.chains.summary_chain import SummaryChain
from domain.chat.chains.title_chain import TitleChain


class ChatCompletedHandler(EventHandler):
    def __init__(
        self, repo: ChatRepository, summary_chain: SummaryChain, title_chain: TitleChain
    ):
        self.repo = repo
        self.summary_chain = summary_chain
        self.title_chain = title_chain

    def supports(self, event_type: str) -> bool:
        return event_type == "chat.completed"

    async def handle(self, event: dict):
        data = event.get("data", {})
        print(f"data={data}")
        db = SessionLocal()
        try:
            session_id = data["session_id"]
            question = data["question"]
            ai_answer = data["ai_answer"]
            turn = data["turn"]
            summary = data.get("conversation_summary", "")

            self.repo.save_message(db, session_id, "user", question, turn)
            self.repo.save_message(db, session_id, "assistant", ai_answer, turn)
            db.flush()  # 세션 내 변경 내용을 DB에 반영 (commit 아님)

            # -------------------
            # Title (첫 턴만)
            # -------------------
            title = None
            if turn == 1:
                title_result = self.title_chain.invoke(question)
                title = title_result.title

            # -------------------
            # Summary (3턴마다)
            # -------------------
            elif turn % 3 == 0:
                recent_msgs = self.repo.get_recent_messages(db, session_id, limit=5)
                new_conversation = "\n".join(
                    [f"{m.role}: {m.content}" for m in recent_msgs]
                )
                summary_result = self.summary_chain.invoke(summary, new_conversation)
                summary = summary_result.summary

            # -------------------
            # DB 저장
            # -------------------
            self.repo.save_session(db, session_id, "kobe", title, summary)
            db.commit()

        except Exception as e:
            # 실제 에러 메시지와 traceback 확인
            import traceback

            print("❌ DB 작업 중 에러 발생:", e)
            traceback.print_exc()

        finally:
            db.close()
