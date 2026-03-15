from fastapi import FastAPI
from domain.document import router as document
from domain.chat.router import chat_router, session_router

app = FastAPI()

app.include_router(document.router)
app.include_router(chat_router.router)
app.include_router(session_router.router)
