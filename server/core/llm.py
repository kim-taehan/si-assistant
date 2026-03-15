# core/llm.py
from langchain_ollama import ChatOllama

from domain.chat.agent.tool import search_documents, get_user_information

llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0,
)

tools = [search_documents, get_user_information]

tool_llm = llm.bind_tools(tools)
