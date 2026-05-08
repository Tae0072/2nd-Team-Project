from fastapi import APIRouter, Depends, HTTPException, status
from app.domain.schemas import (
    CreateSessionRequest, SessionResponse,
    SessionDetailResponse, SessionPageResponse, AdvanceStageRequest
)
from app.usecase.session_usecase import SessionUseCase

router = APIRouter()


def get_session_usecase() -> SessionUseCase:
    return SessionUseCase()


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    usecase: SessionUseCase = Depends(get_session_usecase),
):
    """큐티 세션 생성 (A단계부터 시작). DB 구현은 W2."""
    return await usecase.create_session(request)


@router.get("", response_model=SessionPageResponse)
async def list_sessions(
    page: int = 0,
    size: int = 20,
    usecase: SessionUseCase = Depends(get_session_usecase),
):
    """내 세션 목록 (X-User-Id 헤더 → Gateway 주입)."""
    return await usecase.list_sessions(page, size)


@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session(
    session_id: int,
    usecase: SessionUseCase = Depends(get_session_usecase),
):
    """세션 상세 + 대화 이력 (SessionDetailResponse)."""
    return await usecase.get_session_or_404(session_id)


@router.patch("/{session_id}/advance", response_model=SessionResponse)
async def advance_stage(
    session_id: int,
    body: AdvanceStageRequest,
    usecase: SessionUseCase = Depends(get_session_usecase),
):
    """큐티 단계 진행 A→B→C→D."""
    return await usecase.advance_stage(session_id, body)