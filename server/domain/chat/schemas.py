from pydantic import BaseModel, ConfigDict
from datetime import date


class ChatRequest(BaseModel):
    question: str
    session_id: str
