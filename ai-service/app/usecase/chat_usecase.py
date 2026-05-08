"""ChatUseCase - Anthropic Claude SSE 스트리밍 + ChromaDB RAG 코칭

P1-7 SSE 계약 단일화:
  04_API_명세서.md canonical 포맷으로 통일.
    event: turn_started  data: {"turnId":null,"step":"A","timestamp":"..."}
    event: token         data: {"text":"..."}
    event: rag_sources   data: {"sources":[...]}
    event: turn_completed data: {"turnId":null,"step":"A","inputTokens":N,"outputTokens":N}
    data: [DONE]
"""
import json
import os
from datetime import datetime, timezone
from typing import AsyncIterator

import anthropic

from app.domain.schemas import SendMessageRequest
from app.infrastructure.chroma import get_chroma_collection

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


def _rag_context(book: str, chapter: int, verse: int) -> list[dict]:
    """ChromaDB 에서 관련 신학 주석 검색. 소스 목록 반환."""
    try:
        collection = get_chroma_collection()
        results = collection.query(
            query_texts=[f"{book} {chapter}:{verse}"],
            n_results=3,
        )
        docs = results.get("documents", [[]])[0]
        distances = results.get("distances", [[]])[0]
        return [
            {"id": f"rag_{i}", "text": doc, "score": round(1 - dist, 4)}
            for i, (doc, dist) in enumerate(zip(docs, distances))
        ]
    except Exception:
        return []


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z")


class ChatUseCase:
    def __init__(self) -> None:
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
        04_API_명세서.md canonical SSE 포맷으로 스트림 생성.
        event: turn_started → event: token (N회) → event: rag_sources → event: turn_completed → [DONE]
        """
        # ── turn_started ───────────────────────────────────────────────────────
        yield (
            "event: turn_started\n"
            f"data: {json.dumps({'turnId': None, 'step': stage, 'timestamp': _now_iso()}, ensure_ascii=False)}\n\n"
        )

        # ── RAG 컨텍스트 수집 (스트리밍 전 동기 호출) ──────────────────────────
        sources = _rag_context(book, chapter, verse)
        system = STAGE_SYSTEM_PROMPTS.get(stage, STAGE_SYSTEM_PROMPTS["A"])
        if sources:
            system += "\n\n[참고 주석]\n" + "\n".join(s["text"] for s in sources)

        # ── event: token (Anthropic 스트리밍) ──────────────────────────────────
        input_tokens = 0
        output_tokens = 0
        async with self._client.messages.stream(
            model=MODEL,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": request.user_message}],
        ) as stream:
            async for text in stream.text_stream:
                yield (
                    "event: token\n"
                    f"data: {json.dumps({'text': text}, ensure_ascii=False)}\n\n"
                )
            # 최종 메시지에서 토큰 카운트 추출
            final_msg = await stream.get_final_message()
            input_tokens = final_msg.usage.input_tokens
            output_tokens = final_msg.usage.output_tokens

        # ── event: rag_sources ─────────────────────────────────────────────────
        yield (
            "event: rag_sources\n"
            f"data: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"
        )

        # ── event: turn_completed ──────────────────────────────────────────────
        yield (
            "event: turn_completed\n"
            f"data: {json.dumps({'turnId': None, 'step': stage, 'inputTokens': input_tokens, 'outputTokens': output_tokens}, ensure_ascii=False)}\n\n"
        )

        # ── [DONE] ─────────────────────────────────────────────────────────────
        yield "data: [DONE]\n\n"