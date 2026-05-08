"""ChatUseCase — Anthropic Claude SSE 스트리밍 + ChromaDB RAG 코칭"""
import json
import os
from typing import AsyncIterator
import anthropic
from app.domain.schemas import SendMessageRequest
from app.infrastructure.chroma import get_chroma_collection

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
MODEL = "claude-sonnet-4-20250514"

STAGE_SYSTEM_PROMPTS = {
    "A": """당신은 큐티(QT) 코치입니다. 사용자가 성경 본문을 '관찰'하도록 돕습니다.
본문에서 무엇이 보이는지, 누가 등장하는지, 어떤 사건이 일어나는지
소크라테스식 꼬리 질문으로 이끌어 주세요. 신학적으로 정확하게 답변하세요.""",
    "B": """당신은 큐티(QT) 코치입니다. '해석' 단계에서 사용자가 본문의 의미를
깊이 이해하도록 돕습니다. 역사적·문화적 배경, 원어 의미를 바탕으로
소크라테스식 꼬리 질문으로 안내하세요.""",
    "C": """당신은 큐티(QT) 코치입니다. '적용' 단계에서 사용자가 말씀을
오늘 자신의 삶에 어떻게 적용할지 발견하도록 돕습니다.""",
    "D": """당신은 큐티(QT) 코치입니다. '결단' 단계에서 사용자가
구체적이고 실천 가능한 결단을 내리도록 격려합니다.""",
}


class ChatUseCase:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    def _rag_context(self, book: str, chapter: int, verse: int) -> str:
        """ChromaDB에서 관련 신학 주석 검색"""
        try:
            collection = get_chroma_collection()
            query = f"{book} {chapter}:{verse}"
            results = collection.query(query_texts=[query], n_results=3)
            docs = results.get("documents", [[]])[0]
            return "\n".join(docs) if docs else ""
        except Exception:
            return ""

    async def stream_response(
        self, session_id: int, request: SendMessageRequest
    ) -> AsyncIterator[str]:
        """SSE 스트림 생성 — 토큰 단위 전송"""
        # TODO: DB에서 세션·단계·이력 조회
        stage = "A"  # 실제로는 DB 조회
        rag_ctx = self._rag_context("JHN", 3, 16)  # 실제로는 세션에서 조회

        system = STAGE_SYSTEM_PROMPTS[stage]
        if rag_ctx:
            system += f"\n\n[참고 주석]\n{rag_ctx}"

        with self.client.messages.stream(
            model=MODEL,
            max_tokens=1000,
            system=system,
            messages=[{"role": "user", "content": request.user_message}],
        ) as stream:
            for text in stream.text_stream:
                chunk = {"type": "token", "data": text, "sessionId": session_id, "stage": stage}
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

        done_chunk = {"type": "done", "data": "", "sessionId": session_id, "stage": stage}
        yield f"data: {json.dumps(done_chunk)}\n\n"