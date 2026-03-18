# 멀티턴 대화 고도화 설계

## 목표
멀티턴 대화 품질과 비용 효율을 개선하기 위해 다음과 같이 설계한다.

- **Title 생성은 최초 1회만 수행**
- **Summary는 대화가 3턴 이상 누적되었을 때부터 생성/갱신**

---

## 전체 대화 흐름

```mermaid
graph TD
    A[사용자 질문] --> B[Question Rewriter]

    %% Rewrite Fast Path
    B --> B1[History + Question → 단일 Prompt 생성]
    B1 --> B2[LLM 호출 (단일 HumanMessage)]
    B2 --> B3[Standalone Question 생성]

    %% 메인 응답 생성
    B3 --> F[LLM 호출 (최소 Prompt)]

    %% Tool 분기
    F --> G{Tool 호출 필요}

    G -->|Yes| H[RAG Tool 호출]
    H --> I[검색 결과 반환]

    I --> J[LLM 최종 답변 생성 (단일 Prompt)]

    G -->|No| J

    %% Event 발행 (여기서 모든 후처리 분리)
    J --> N[Event Payload 구성]

    N --> O[Event Publish: chat.completed]

    %% Event Bus
    O --> P[Event Bus]
    P --> Q[비동기 Worker]

    %% Handler 진입
    Q --> R[ChatCompletedHandler]

    %% Title 조건 (1턴만)
    R --> T{턴 == 1}
    T -->|Yes| T1[Title 생성]
    T -->|No| T2[Title 생략]

    %% Summary 조건 (3턴마다)
    R --> S{턴 % 3 == 0}
    S -->|Yes| S1[Summary 생성 또는 업데이트]
    S -->|No| S2[Summary 생략]

    %% 후처리
    T1 --> U[DB 저장 및 후처리]
    T2 --> U
    S1 --> U
    S2 --> U

    U --> V[응답 반환]
```

## 구성 요소

### 1. Question Rewriter
- 이전 대화 문맥을 활용하여 **독립적인 질문(standalone question)**으로 재작성한다.
- 목적
  - 검색 품질 향상
  - 멀티턴 문맥 반영
- 예시
```
사용자: 그럼 높이는?
→ Rewrite: 백두산의 높이는 얼마인가?
```

### 2. Title Generator
- 대화의 주제를 나타내는 짧은 제목을 생성한다.
- 실행 조건
  - turn_count == 1
- 예시
```
사용자: 백두산 높이는 얼마야?
Title: 백두산 높이 질문
```

### 3. Conversation Summary Generator
- 3턴 마다 호출 대화가 누적되었을 때부터 실행
- 조건
  - turn_count % 3 == 0
- 역할
  - 이전 대화 핵심 내용 압축
  - 장기 메모리 역할
  - 이후 Question Rewrite 품질 향상
- 예시 Summary
```
사용자는 백두산의 높이와 위치에 대해 질문하였다.
어시스턴트는 백두산의 높이와 중국-북한 국경에 위치한다는 정보를 설명하였다.
```

## 실행 규칙 

| 기능               | 실행 조건             | 실행 빈도  | 실행 방식|
| ---------------- | ----------------- | ------ | --|
| Title 생성         | `turn_count == 1` | 1회     | event bus|
| Summary 생성       | `turn_count % 3 == 0` | 3 턴 마다 |event bus|
| Question Rewrite | 모든 질문             | 매 턴    |lang graph|


