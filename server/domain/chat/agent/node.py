# domain/chat/agent/nodes.py
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import load_prompt
from domain.chat.agent.state import ChatState
from core.llm import llm, tool_llm, tools
from domain.chat.agent.tool import get_user_information, search_documents
from rag.search_service import search


from langchain_core.messages import SystemMessage

from langgraph.prebuilt import ToolNode

tool_node = ToolNode(tools=tools)


async def chatbot_node(state: ChatState):

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
    """

    messages = [SystemMessage(content=system_prompt), *state["messages"]]

    response = await tool_llm.ainvoke(messages)

    return {"messages": [response]}


async def rewrite_question_node(state: ChatState):

    messages = state["messages"]

    if len(messages) == 1:
        return {"messages": messages}

    summary = state.get("conversation_summary", "")

    recent_human = [m.content for m in messages if isinstance(m, HumanMessage)][-2:]

    system_prompt = f"""
너는 사용자의 질문을 standalone question으로 재작성하는 AI다.

이전 대화 요약:
{summary}

규칙
1. 질문 의미를 바꾸지 않는다
2. standalone question으로 만든다
3. 질문만 반환한다
"""

    rewrite_messages = [SystemMessage(content=system_prompt), *recent_human]

    result = await llm.ainvoke(rewrite_messages)

    rewritten_question = result.content

    messages[-1] = HumanMessage(content=rewritten_question)

    return {"messages": messages, "standalone_question": rewritten_question}
