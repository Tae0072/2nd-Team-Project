"""SessionUseCase - 큐티 세션 CRUD
스켈레톤 단계: 501 반환. W1 DB 초기화 후 실제 구현 예정.
"""
from fastapi import HTTPException, status
from app.domain.schemas import CreateSessionRequest, AdvanceStageRequest

_NOT_IMPL = {"code": "NOT_IMPLEMENTED", "message": "W1 DB 초기화 후 구현 예정 (현재 스켈레톤 단계)"}


class SessionUseCase:

    async def create_session(self, request: CreateSessionRequest) -> dict:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_NOT_IMPL)

    async def list_sessions(self, page: int, size: int) -> dict:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_NOT_IMPL)

    async def get_session(self, session_id: int) -> dict | None:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_NOT_IMPL)

    async def get_session_or_404(self, session_id: int) -> dict:
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_NOT_IMPL)

    async def advance_stage(self, session_id: int, body: AdvanceStageRequest) -> dict:
        # P1-6 fix: body 인자 추가 (router가 넘기는 2번째 인자를 받음)
        raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=_NOT_IMPL)