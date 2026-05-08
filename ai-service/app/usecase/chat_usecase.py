"""ChatUseCase — Anthropic Claude SSE 스트리밍 + ChromaDB RAG 코칭
P2 fix: 동기 client → AsyncAnthropic (이벤트 루프 블로킹 방지)
"""
import json
import os
from typing import AsyncIterator, Optional
import anthropic
from app.domain.schemas import SendMessageRequest
from app.infrastructure.chroma import get_chroma_collection

# P2 fix: 환경변수 명칭 통일 (.env.example 기준)
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-20250514"

STAGE_SYSTEM_PROMPTS = {
    "A": (
        "당신은 큐티(QT) 코치입니다. 사용자가 성경 본문을 '관찰'하도록 돕습니다. "
        "본문에서 무엇이 보이는지, 누가 등장하는지, 어떤 사건이 일어나는지 "
        "소크라테스식 꼬리 질문으로 이끌어 주세요. 신학적으로 정확하게 답변하세요."
    ),
    "B": (
        "당신은 큐티(QT) 코치입니다. '해석' 단계에서 사용자가 본문의 의미를 "
        "깊이 이해하도록 돕습니다. 역사적·문화적 배경, 원어 의미를 바탕으로 "
        "소크라테스식 꼬리 질문으로 안내하세요."
    ),
    "C": (
        "당신은 큐티(QT) 코치입니다. '적용' 단계에서 사용자가 말씀을 "
        "오늘 자신의 삶에 어떻게 적용할지 발견하도록 돕습니다."
    ),
    "D": (
        "당신은 큐티(QT) 코치입니다. '결단' 단계에서 사용자가 "
        "구체적이고 실천 가능한 결단을 내리도록 격려합니다."
    ),
}


def _rag_context(book: str, chapter: int, verse: int) -> str:
    """ChromaDB에서 관련 신학 주석 검색 (동기 — ChromaDB SDK가 sync)"""
    try:
        collection = get_chroma_collection()
        results = collection.query(
            query_texts=[f"{book} {chapter}:{verse}"],
            n_results=3,
        )
        docs = results.get("documents", [[]])[0]
        return "\n".join(docs) if docs else ""
    except Exception:
        return ""


class ChatUseCase:
    def __init__(self) -> None:
        # P2 fix: AsyncAnthropic 사용 — async with stream
        self._client = anthropic.AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

    async def stream_response(
        self,
        session_id: int,
        request: SendMessageRequest,
        *,
        stage: str,
        book: str,
        chapter: int,
        verse: int,
    ) -> AsyncIterator[str]:
        """
        SSE 스트림 생성.
        stage / book / chapter / verse 는 호출자(router)가 DB에서 조회해 전달.
        P1 fix: 하드코딩 제거, 세션 컨텍스트 파라미터로 수신.
        P2 fix: async with stream → 이벤트 루프 블로킹 없음.
        """
        rag_ctx = _rag_context(book, chapter, verse)
        system = STAGE_SYSTEM_PROMPTS.get(stage, STAGE_SYSTEM_PROMPTS["A"])
        if rag_ctx:
            system += f"\n\n[참고 주석]\n{rag_ctx}"

        async with self._client.messages.stream(
            model=MODEL,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": request.user_message}],
        ) as stream:
            async for text in stream.text_stream:
                chunk = {
                    "type": "token",
                    "data": text,
                    "sessionId": session_id,
                    "stage": stage,
                }
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        done = {"type": "done", "data": "", "sessionId": session_id, "stage": stage}
        yield f"data: {json.dumps(done)}\n\n"