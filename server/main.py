from fastapi import FastAPI, Depends
from domain.document import router as document
from domain.chat.router import chat_router, session_router
from domain.chat.factories import create_chat_completed_handler
import asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.event_bus import worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    worker.register_handler(create_chat_completed_handler())
    task = asyncio.create_task(worker.start())
    print("Worker started")

    yield

    # shutdown
    worker.running = False
    task.cancel()
    print("Worker stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(document.router)
app.include_router(chat_router.router)
app.include_router(session_router.router)
