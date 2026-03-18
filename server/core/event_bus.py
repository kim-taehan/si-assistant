import asyncio
from abc import ABC, abstractmethod


# -----------------------------
# Handler ABC
# -----------------------------
class EventHandler(ABC):
    @abstractmethod
    def supports(self, event_type: str) -> bool:
        pass

    @abstractmethod
    async def handle(self, event: dict):
        pass


# -----------------------------
# EventBus
# -----------------------------
class EventBus:
    def __init__(self):
        self.queue = asyncio.Queue()

    async def publish(self, event: dict):
        await self.queue.put(event)

    async def consume(self):
        return await self.queue.get()


# -----------------------------
# Worker (ABC Handler 지원)
# -----------------------------
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


event_bus = EventBus()
worker = Worker(event_bus=event_bus)
