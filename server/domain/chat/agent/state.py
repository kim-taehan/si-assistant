# domain/chat/agent/state.py

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    context: Annotated[str, "RAG 검색을 통해 조회된 참고 문서 내용"]
    conversation_summary: Annotated[str, "이전 대화를 요약한 내용 (context 유지용)"]
    question: Annotated[str, "현재 사용자가 입력한 원본 질문"]
    standalone_question: Annotated[str, "대화 맥락을 반영해 재작성된 독립적인 질문"]
