import streamlit as st
import requests
from langchain_core.messages.chat import ChatMessage

API_URL = "http://localhost:8000/chat"
API_SESSION = "http://localhost:8000/chat/sessions"
API_HISTORY = "http://localhost:8000/chat/sessions"
# 세션 초기화
if "session_id" not in st.session_state:
    resp = requests.post(API_SESSION)
    st.session_state.session_id = resp.json()["session_id"]

if "messages" not in st.session_state:
    st.session_state["messages"] = []

st.title("SI Assistant")


def print_message():
    for chat_message in st.session_state["messages"]:
        st.chat_message(chat_message.role).write(chat_message.content)


def add_message(role, message):
    st.session_state["messages"].append(ChatMessage(role=role, content=message))


with st.sidebar:
    clear_button = st.button("🆕 new chatting")
    if clear_button:
        st.session_state.messages = []
        resp = requests.post(API_SESSION)
        st.session_state.session_id = resp.json()["session_id"]

    st.subheader("💬 이전 대화")
    try:
        resp = requests.get(f"{API_HISTORY}")
        sessions = resp.json()  # [{"id":1, "summary":"..."}]
    except:
        sessions = []

    for s in sessions:
        if st.button(s["title"], key=s["session_id"]):
            # 선택한 세션 불러오기
            # print(s["id"])
            st.session_state.session_id = s["session_id"]
            st.session_state.messages = []
            # resp = requests.get(f"{API_HISTORY}/messages?session_id={s['session_id']}")
            resp = requests.get(f"{API_HISTORY}/{s['session_id']}/messages")
            if resp.status_code == 200:
                messages_json = resp.json()
                for m in messages_json:
                    add_message(m["role"], m["content"])

# 질문 입력

print_message()
user_input = st.chat_input("You can ask me anything.")


def stream_answer(question):
    response = requests.post(
        API_URL,
        json={"question": question, "session_id": st.session_state.session_id},
        stream=True,
    )

    assistant_content = ""
    for chunk in response.iter_content(chunk_size=None):
        if chunk:
            text = chunk.decode("utf-8")
            assistant_content += text
            yield text  # 화면 스트리밍
    return assistant_content


if user_input:
    # 1️⃣ 사용자 메시지 저장
    add_message("user", user_input)
    st.chat_message("user").write(user_input)

    # 2️⃣ 어시스턴트 메시지 스트리밍
    with st.chat_message("assistant") as msg_container:
        placeholder = st.empty()
        assistant_content = ""

        # 처음 append
        add_message("assistant", "")
        for chunk in stream_answer(user_input):
            assistant_content += chunk
            placeholder.write(assistant_content)

            # messages 갱신
            st.session_state.messages[-1].content = assistant_content
