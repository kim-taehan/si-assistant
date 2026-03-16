from langchain_core.tools import tool

from langchain_core.tools import tool
from rag.search_service import search


# 문서 포맷팅 함수
def format_docs(docs):
    print(f"docs {len(docs)}")

    return "\n\n".join(
        [
            f"<document>"
            f"<content>{doc.page_content}</content>"
            f'<source>{doc.metadata.get("source","unknown")}</source>'
            f'<page>{doc.metadata.get("page",0)+1}</page>'
            f"</document>"
            for doc in docs
        ]
    )


@tool
def search_documents(query: str) -> str:
    """
    회사 문서나 프로젝트 문서에 대한 질문에 답하기 위해 사용한다.

    다음과 같은 경우 반드시 사용한다:
    - 프로젝트 정보
    - 프로젝트, 악사손해보험 이라는 단어가 있는 경우
    - 회사 정책
    - 내부 문서
    - 기술 문서
    """

    docs = search(query, k=3)

    if not docs:
        return "관련 문서를 찾을 수 없습니다."

    context = format_docs(docs)

    return f"""
다음은 검색된 회사 문서 내용이다.
{context}
위 문서를 참고해서 사용자의 질문에 답하라.
"""


@tool
def get_user_information(name: str) -> dict:
    """
    Retrieve a user's contact information by their name.

    Args:
        name (str): The name of the user.

    Returns:
        dict: A dictionary containing the user's phone number and email address.
    """

    # 예시 데이터
    users = {
        "심상준": {
            "phone": "010-1234-5678",
            "email": "sim@example.com",
            "직급": "팀장",
        },
        "조용준": {
            "phone": "010-1234-5678",
            "email": "jo@example.com",
            "직급": "파트장",
        },
        "박동진": {
            "phone": "010-9876-5432",
            "email": "pack@example.com",
            "직급": "파트원",
        },
    }

    return users.get(name, {"phone": None, "email": None})
