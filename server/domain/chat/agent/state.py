# domain/chat/agent/state.py

from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages


class ChatState(TypedDict):
    messages: Annotated[list, add_messages]
    route: Annotated[str, "rag 사용 유무"]
    context: Annotated[str, "rag 에서 조회된 내용"]
    conversation_summary: Annotated[str, "요약된 대화내용"]
    standalone_question: Annotated[str, "독립 질문으로 변경"]
