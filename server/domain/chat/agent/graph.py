# domain/chat/agent/graph.py
from langgraph.graph import StateGraph, END

from domain.chat.agent.state import ChatState
from domain.chat.agent.node import chatbot_node, tool_node, rewrite_question_node
from langgraph.prebuilt import ToolNode

from domain.chat.agent.tool import get_user_information
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import tools_condition


def build_chat_graph():

    builder = StateGraph(ChatState)

    builder.add_node("rewrite_question", rewrite_question_node)
    builder.add_node("chatbot", chatbot_node)
    builder.add_node("tools", tool_node)

    # builder.add_edge(START, "chatbot")
    builder.set_entry_point("rewrite_question")

    builder.add_edge("rewrite_question", "chatbot")
    # builder.add_conditional_edges("chatbot", tools_condition)
    builder.add_conditional_edges(
        "chatbot",
        tools_condition,
        {
            "tools": "tools",
            "__end__": END,
        },
    )

    builder.add_edge("tools", "chatbot")

    # builder.add_edge("chatbot", END)

    return builder.compile()


# def build_chat_graph_old():
#     builder = StateGraph(ChatState)

#     builder.add_node("router", router_node)
#     builder.add_node("rag", rag_node)
#     builder.add_node("tools", ToolNode([get_user_information]))
#     builder.add_node("answer", answer_node)
#     builder.add_node("rag_answer", rag_answer_node)

#     builder.set_entry_point("router")

#     builder.add_conditional_edges(
#         "router",
#         lambda state: state["route"],
#         {
#             "rag": "rag",
#             "normal": "answer",
#         },
#     )

#     builder.add_edge("rag", "rag_answer")
#     builder.add_edge("rag_answer", END)
#     builder.add_edge("answer", END)

#     return builder.compile()
