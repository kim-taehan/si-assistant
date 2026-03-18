# Event Bus 기반 멀티턴 대화 구조 설계

## 1 개요
- 기존 LangChain의 메시지 리스트 기반 멀티턴 구조 대신, Event Bus 패턴을 활용하여 멀티턴 대화를 구성한다.
- 채팅 처리 이후(Post-processing) 작업을 비동기 이벤트 기반으로 분리
- 주요 목적:
  - API 응답 속도 개선 (후처리 비동기화)
  - 핸들러 기반 확장성 확보
  - 이벤트 중심 아키텍처 도입

--- 
## 2 전체 아키텍처
```text
[Chat API]
    ↓ (event publish)
[EventBus]
    ↓
[Worker]
    ↓
[EventHandler (ChatCompletedHandler)]
    ↓
[DB 저장 / 요약 / 타이틀 생성]
```

--- 
## 3 핵심 컴포넌트
### 3.1 EventHandler (추상 클래스)
- 전략 패턴방식을 사용하기 위한 event handler
```python
class EventHandler(ABC):
    @abstractmethod
    def supports(self, event_type: str) -> bool:
        pass

    @abstractmethod
    async def handle(self, event: dict):
        pass
```
- 역할
- 특정 이벤트 타입 처리 여부 판단 (supports)
- 실제 이벤트 처리 (handle)

### 3.2 EventBus
- 비동기 이벤트 큐 관리 
```python 
class EventBus:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def publish(self, event: dict):
        await self.queue.put(event)

    async def consume(self):
        return await self.queue.get()
```

#### 주요 기능
| 메서드              | 설명     |
| ---------------- | ------ |
| `publish(event)` | 이벤트 발행 |
| `consume()`      | 이벤트 소비 |

#### 특징
- asyncio.Queue 기반
- Producer / Consumer 구조


### 3.3 Worker
- 이벤트를 소비하고 적절한 핸들러에 위임
```python

class Worker:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.handlers = []  # EventHandler 리스트
        self.running = True

    def register_handler(self, handler):
        self.handlers.append(handler)

    async def start(self):
        while self.running:
            event = await self.event_bus.consume()
            event_type = event.get("type")
            handled = False
            for handler in self.handlers:
                if handler.supports(event_type):
                    await handler.handle(event)
                    handled = True
                    break
            if not handled:
                print(f"처리할 수 있는 핸들러가 없습니다. {event_type}")
```

#### 주요 동작
- 이벤트 수신
- 이벤트 타입 추출
- 등록된 핸들러 순회
- 처리 가능한 핸들러 실행
  
#### 특징
- Handler Registry 패턴
- 단일 이벤트 → 단일 핸들러 처리 (break)
- 미처리 이벤트 로그 출력


--- 
## 4 주요 장점
- 응답 속도 개선 : api 요청과 후처리 로직 분리 
- 확장성 : hander 추가만으로 기능 확장 가능함 
- 관심사 분리 
  | 영역       | 역할      |
| -------- | ------- |
| API      | 요청 처리   |
| EventBus | 이벤트 전달  |
| Worker   | 분배      |
| Handler  | 비즈니스 로직 |

--- 
## 5 고려사항 
- 단일 worker 구조 : 병렬처리 안됨
- 이벤트 유실 가능성 (메모리큐 사용)
- 트랜잭션 분리로 인한 데이터 오류 발생
