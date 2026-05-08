"""SessionUseCase — 큐티 세션 CRUD
P1 fix: NotImplementedError(→ 500) 대신 HTTPException 501 반환.
W1 DB 초기화 후 실제 구현 예정.
"""
from fastapi import HTTPException, status
from app.domain.schemas import CreateSessionRequest


_NOT_IMPL_MSG = "W1 DB 초기화 후 구현 예정 (현재 스켈레톤 단계)"


class SessionUseCase:

    async def create_session(self, request: CreateSessionRequest) -> dict:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"code": "NOT_IMPLEMENTED", "message": _NOT_IMPL_MSG},
        )

    async def list_sessions(self, page: int, size: int) -> dict:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"code": "NOT_IMPLEMENTED", "message": _NOT_IMPL_MSG},
        )

    async def get_session(self, session_id: int) -> dict | None:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"code": "NOT_IMPLEMENTED", "message": _NOT_IMPL_MSG},
        )

    async def get_session_or_404(self, session_id: int) -> dict:
        """세션 존재·소유권 검증. 없으면 404, 미구현이면 501."""
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"code": "NOT_IMPLEMENTED", "message": _NOT_IMPL_MSG},
        )

    async def advance_stage(self, session_id: int) -> dict:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail={"code": "NOT_IMPLEMENTED", "message": _NOT_IMPL_MSG},
        )