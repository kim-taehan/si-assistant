# core/llm.py
from langchain_ollama import ChatOllama

from domain.chat.agent.tool import search_documents, get_user_information

from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="exaone", base_url="http://10.250.121.100/exaone/v1")
tools = [search_documents, get_user_information]

tool_llm = llm.bind_tools(tools)
