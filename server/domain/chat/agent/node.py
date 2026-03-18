# domain/chat/agent/nodes.py
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import load_prompt
from domain.chat.agent.state import ChatState
from core.llm import small_token_llm, tool_llm, tools
from domain.chat.agent.tool import get_user_information, search_documents
from rag.search_service import search
from core.event_bus import worker
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools=tools)


async def chatbot_node(state: ChatState):

    print(">>>> chatbot_node start")
    summary = state.get("conversation_summary", "")

    system_prompt = f"""
    너는 회사 AI Assistant다.

    이전 대화 요약:
    {summary}

    규칙:
    1. 일반 상식 질문은 tool을 사용하지 말고 직접 답변한다.
    2. 회사 내부 문서, 프로젝트 정보, 정책 질문일 때만 search_documents tool을 사용한다.
    2. 사용자 정보를 확인해야 하면 get_user_information tool을 사용한다.
    4. tool 결과를 바탕으로 답변한다.
    5. 반드시 "사용자의 질문"을 기준으로 답변한다.
    6. 문서 전체를 요약하지 말고 질문에 필요한 부분만 사용한다
    7. 특별한 언급이 없는 경우 반드시 한국어로 답변한다.
    """

    messages = [SystemMessage(content=system_prompt), *state["messages"]]

    response = await tool_llm.ainvoke(messages)

    print(">>>> chatbot_node end")
    return {"messages": [response]}


async def rewrite_question_node(state: ChatState):

    print(">>>> rewrite question start")
    messages = state["messages"]

    # if len(messages) == 1:
    #     return {"messages": messages}
    summary = state.get("conversation_summary", "")
    prompt = load_prompt("prompt/rewrite_question.yaml")

    system_message = prompt.format(summary=summary)
    recent_human = [m.content for m in messages][-2:]

    rewrite_messages = [SystemMessage(content=system_message), *recent_human]

    result = await small_token_llm.ainvoke(rewrite_messages)

    rewritten_question = result.content
    messages[-1] = HumanMessage(content=rewritten_question)
    print(f"rewrite question = {rewritten_question}")
    print("<<<< rewrite question end")
    return {"messages": messages, "standalone_question": rewritten_question}


async def title_node(state: ChatState):
    """
    첫 턴일 경우 Title 생성 이벤트 발행
    LLM 호출 X
    """
    turn = state.get("turn", 1)
    if turn != 1:
        return {}

    question = state.get("question", "제목없음")
    session_id = state.get("session_id")

    # Worker 이벤트 발행
    await worker.submit(
        {
            "type": "title.completed",
            "data": {"session_id": session_id, "question": question},
        }
    )

    return {}
