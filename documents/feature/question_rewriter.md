# Question Rewriter
> 사용자의 맥락 의존 질문 → 독립 질문으로 바꾼다.

## 예시
### 기존 대화
```text
User: 북한산 높이
AI: 836m
User: 그럼 한라산은?
```

### Rewrite 결과
```text 
그럼 한라산은?
→ "한라산의 높이는 얼마인가?"
```
## 전체 흐름 
```
                ┌───────────────┐
                │   START       │
                └──────┬────────┘
                       │
                       ▼
            ┌────────────────────┐
            │ Question Rewriter  │
            │ (rewrite_question) │
            └─────────┬──────────┘
                      │
                      ▼
              ┌───────────────┐
              │   Chatbot     │
              │ (LLM Agent)   │
              └──────┬────────┘
                     │
         tool call?  │
           ┌─────────┴─────────┐
           │                   │
           ▼                   ▼
     ┌─────────────┐     ┌─────────┐
     │  Tool Node  │     │   END   │
     │ (LangGraph) │     │         │
     └──────┬──────┘     └─────────┘
            │
            ▼
      ┌─────────────┐
      │  Chatbot    │
      │ (tool 결과) │
      └──────┬──────┘
             │
             ▼
            END
```

## 기존과 동일한 형태의 messages langchain 방식의 node

```python
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
```

