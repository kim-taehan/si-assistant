# core/llm.py
from langchain_ollama import ChatOllama

from domain.chat.agent.tool import search_documents, get_user_information

from langchain_openai import ChatOpenAI

# http://10.250.121.100/exaone

ollam_model_name = "qwen2.5:14b"

llm = ChatOllama(
    model=ollam_model_name,
    temperature=0,
)

# llm = ChatOpenAI(model="exaone", base_url="http://10.250.121.100/exaone/v1")
tools = [search_documents, get_user_information]
tool_llm = llm.bind_tools(tools)


small_token_llm = ChatOllama(model=ollam_model_name, temperature=0, max_tokens=20)
# small_token_llm = ChatOpenAI(
#     model="exaone", base_url="http://10.250.121.100/exaone/v1", max_tokens=100
# )
