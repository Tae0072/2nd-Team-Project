from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from datetime import datetime


class QtStage(str, Enum):
    A = "A"  # 관찰
    B = "B"  # 해석
    C = "C"  # 적용
    D = "D"  # 결단


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


class CreateSessionRequest(BaseModel):
    book: str = Field(..., example="JHN")
    chapter: int = Field(..., ge=1)
    verse: int = Field(..., ge=1)
    template_type: QtStage = QtStage.A


class SendMessageRequest(BaseModel):
    user_message: str = Field(..., max_length=2000)
    idempotency_key: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: int
    user_id: int
    book: str
    chapter: int
    verse: int
    current_stage: QtStage
    status: SessionStatus
    created_at: datetime
    updated_at: datetime


class SessionPageResponse(BaseModel):
    content: List[SessionResponse]
    page: int
    size: int
    total_elements: int
    total_pages: int