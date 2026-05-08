from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.domain.schemas import SendMessageRequest
from app.usecase.chat_usecase import ChatUseCase
from app.usecase.session_usecase import SessionUseCase

router = APIRouter()


def get_chat_usecase() -> ChatUseCase:
    return ChatUseCase()


def get_session_usecase() -> SessionUseCase:
    return SessionUseCase()


@router.post("/{session_id}/messages")
async def send_message(
    session_id: int,
    request: SendMessageRequest,
    chat_uc: ChatUseCase = Depends(get_chat_usecase),
    session_uc: SessionUseCase = Depends(get_session_usecase),
):
    """AI SSE 스트리밍 — 세션 검증 후 ChatUseCase에 실제 컨텍스트 전달."""
    session = await session_uc.get_session_or_404(session_id)
    return StreamingResponse(
        chat_uc.stream_response(
            session_id=session_id,
            request=request,
            stage=session["current_stage"],
            book=session["book"],
            chapter=session["chapter"],
            verse=session["verse"],
        ),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )