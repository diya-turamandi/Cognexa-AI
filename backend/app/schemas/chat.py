
from datetime import datetime
from typing import Optional, Literal

from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# CREATE SESSION
# ==========================================

class SessionCreate(BaseModel):

    title: str = Field(
        default="New Chat",
        max_length=255
    )

    document_id: Optional[str] = None


# ==========================================
# SESSION RESPONSE
# ==========================================

class SessionResponse(BaseModel):

    id: str
    title: str
    document_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# MESSAGE RESPONSE
# ==========================================

class MessageResponse(BaseModel):

    id: int

    session_id: str

    role: Literal["user", "assistant"]

    content: str

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==========================================
# SESSION DETAIL RESPONSE
# ==========================================

class SessionDetailResponse(SessionResponse):

    messages: list[MessageResponse] = []


# ==========================================
# CHAT REQUEST
# ==========================================

class ChatRequest(BaseModel):

    session_id: str

    question: str = Field(
        min_length=2,
        max_length=2000
    )

    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )


# ==========================================
# CHAT RESPONSE
# ==========================================

class ChatResponse(BaseModel):

    success: bool

    session_id: str

    question: str

    answer: str

    sources: list[dict] = []
