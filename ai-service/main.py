"""QT-AI — AI/RAG Service (Python FastAPI)
- Claude Anthropic SSE 스트리밍
- ChromaDB RAG (신학 주석 벡터 검색)
- 큐티 A(관찰)·B(해석)·C(적용)·D(결단) 4단계 코칭
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1 import sessions, messages, templates
from app.infrastructure.database import init_db
from app.infrastructure.chroma import init_chroma


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작·종료 훅"""
    await init_db()
    await init_chroma()
    yield
    # cleanup (필요 시)


app = FastAPI(
    title="QT-AI AI Service",
    version="1.2.0",
    description="큐티 AI 코칭 서비스 — SSE 스트리밍 + ChromaDB RAG",
    lifespan=lifespan,
)

# CORS (Gateway 경유 시 Gateway 레벨에서 처리, 직접 호출 개발용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus 메트릭
Instrumentator().instrument(app).expose(app, endpoint="/actuator/prometheus")

# 라우터 등록
app.include_router(sessions.router, prefix="/ai/sessions", tags=["sessions"])
app.include_router(messages.router, prefix="/ai/sessions", tags=["messages"])
app.include_router(templates.router, prefix="/ai/prompt-templates", tags=["templates"])


@app.get("/actuator/health")
async def health():
    return {"status": "UP", "service": "ai-service"}