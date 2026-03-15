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
    1. 필요한 경우 반드시 tool을 사용한다.
    2. 사용자 정보를 확인해야 하면 get_user_information tool을 사용한다.
    3. 프로젝트, 문서, 정책, 내부 정보 관련 질문이면 search_documents tool을 사용한다.
    4. tool 결과를 바탕으로 답변한다.
    5. 반드시 "사용자의 질문"을 기준으로 답변한다.
    6. 문서 전체를 요약하지 말고 질문에 필요한 부분만 사용한다
    """

    # messages = [SystemMessage(content=system_prompt)] + state["messages"]
    messages = [SystemMessage(content=system_prompt), *state["messages"]]

    response = await tool_llm.ainvoke(messages)

    return {"messages": [response]}


# async def router_node(state: ChatState):
#     """
#     라우터 노드: 사용자 질문을 분석하여 경로 결정
#     """
#     messages = state.get("messages", [])
#     question = messages[-1]["content"] if messages else ""

#     chain = load_prompt("prompt/route.yaml") | llm

#     result = await chain.ainvoke({"question": question})

#     route_raw = result.content.strip().lower()

#     # route normalization
#     if "rag" in route_raw:
#         route = "rag"
#     else:
#         route = "normal"

#     return {"route": route}


# async def rag_node(state: ChatState):
#     """
#     RAG 기반 문서 검색 및 컨텍스트 생성 노드
#     """
#     print("rag_node call - 검색 시작")
#     query = state["messages"][-1]["content"] if state["messages"] else ""
#     search_results = search(query, k=3)

#     return {"context": search_results}


# async def rag_answer_node(state: ChatState):
#     chain = load_prompt("prompt/chat_context.yaml") | llm

#     formatted_messages = "\n".join(
#         [f'{m["role"]}: {m["content"]}' for m in state.get("messages", [])]
#     )

#     # 🔹 2. 입력 데이터 구성
#     input_data = {
#         "conversation_summary": state.get("conversation_summary"),
#         "recent_messages": formatted_messages,
#         "context": state.get("context"),
#     }
#     response = await chain.ainvoke(input_data)
#     return {"final": response.content}


# # 🔹 노드 정의 (토큰 스트리밍)
# async def answer_node(state: ChatState):
#     chain = load_prompt("prompt/chat.yaml") | tool_llm

#     formatted_messages = "\n".join(
#         [f'{m["role"]}: {m["content"]}' for m in state.get("messages", [])]
#     )

#     # 🔹 2. 입력 데이터 구성
#     input_data = {
#         "conversation_summary": state.get("conversation_summary"),
#         "recent_messages": formatted_messages,
#     }
#     response = await chain.ainvoke(input_data)

#     if hasattr(response, "tool_calls") and response.tool_calls:
#         tool_call = response.tool_calls[0]

#         if tool_call["name"] == "get_user_information":
#             result = get_user_information.invoke(tool_call["args"])

#             # tool 결과 다시 LLM에게 전달
#             followup = await llm.ainvoke(
#                 f"다음 사용자 정보를 참고해서 답변해줘:\n{result}"
#             )

#             return {"final": followup.content}

#     return {"final": response.content}
