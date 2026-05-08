from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.domain.schemas import SendMessageRequest
from app.usecase.chat_usecase import ChatUseCase

router = APIRouter()


def get_chat_usecase() -> ChatUseCase:
    return ChatUseCase()


@router.post("/{session_id}/messages")
async def send_message(
    session_id: int,
    request: SendMessageRequest,
    usecase: ChatUseCase = Depends(get_chat_usecase),
):
    """
    AI에게 메시지 전송 — SSE 스트리밍 응답 (text/event-stream)
    Gateway NoBufferingFilter 적용 필수.
    """
    return StreamingResponse(
        usecase.stream_response(session_id, request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )