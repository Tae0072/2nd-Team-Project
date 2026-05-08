"""SessionUseCase — 큐티 세션 CRUD"""
from app.domain.schemas import CreateSessionRequest, SessionResponse


class SessionUseCase:
    async def create_session(self, request: CreateSessionRequest) -> SessionResponse:
        # TODO: DB 저장 구현 (W1 DB 초기화 후)
        raise NotImplementedError("W1 구현 예정")

    async def list_sessions(self, page: int, size: int):
        raise NotImplementedError("W1 구현 예정")

    async def get_session(self, session_id: int):
        raise NotImplementedError("W1 구현 예정")

    async def advance_stage(self, session_id: int):
        raise NotImplementedError("W1 구현 예정")