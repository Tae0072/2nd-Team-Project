from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List
from enum import Enum
from datetime import datetime


def _camel(s: str) -> str:
    """snake_case → camelCase (OpenAPI 계약 일치)"""
    return to_camel(s)


class _CamelModel(BaseModel):
    """모든 모델 공통 베이스: JSON은 camelCase, Python은 snake_case."""
    model_config = ConfigDict(
        alias_generator=_camel,
        populate_by_name=True,   # snake_case로도 접근 가능
        from_attributes=True,
    )


class QtStage(str, Enum):
    A = "A"  # 관찰
    B = "B"  # 해석
    C = "C"  # 적용
    D = "D"  # 결단


class SessionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    ABANDONED = "ABANDONED"


# ── Request ────────────────────────────────────────────────────────
class CreateSessionRequest(_CamelModel):
    book: str = Field(..., example="JHN")
    chapter: int = Field(..., ge=1)
    verse: int = Field(..., ge=1)
    template_type: QtStage = QtStage.A   # JSON: templateType


class SendMessageRequest(_CamelModel):
    user_message: str = Field(..., max_length=2000)  # JSON: userMessage
    idempotency_key: Optional[str] = None             # JSON: idempotencyKey


class AdvanceStageRequest(_CamelModel):
    current_stage: QtStage                            # JSON: currentStage


# ── Response ───────────────────────────────────────────────────────
class SessionResponse(_CamelModel):
    session_id: int
    user_id: int
    book: str
    chapter: int
    verse: int
    current_stage: QtStage
    status: SessionStatus
    created_at: datetime
    updated_at: datetime


class TurnResponse(_CamelModel):
    turn_id: int
    role: str
    content: str
    stage: QtStage
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    created_at: datetime


class SessionDetailResponse(SessionResponse):
    turns: List[TurnResponse] = []


class SessionPageResponse(_CamelModel):
    content: List[SessionResponse]
    page: int
    size: int
    total_elements: int
    total_pages: int


class PromptTemplateResponse(_CamelModel):
    template_id: int
    stage: QtStage
    name: str
    system_prompt: str
    is_active: bool
    version: int