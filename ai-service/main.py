"""QT-AI -- AI/RAG Service (Python FastAPI)
- Claude Anthropic SSE 스트리밍
- ChromaDB RAG (신학 주석 벡터 검색)
- 큐티 A(관찰)·B(해석)·C(적용)·D(결단) 4단계 코칭
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import sessions, messages, templates
from app.infrastructure.database import init_db
from app.infrastructure.chroma import init_chroma

# P2 fix: liveness/readiness 상태를 분리하여 관리
# - liveness: 앱 프로세스 자체가 살아있는지 (DB/Chroma 초기화 전에도 응답)
# - readiness: 의존성이 모두 준비된 후에만 true
_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 훅 -- 의존성 초기화 실패 시 readiness만 false로 유지"""
    global _ready
    try:
        await asyncio.gather(
            init_db(),
            init_chroma(),
        )
        _ready = True
    except Exception as exc:
        # 초기화 실패해도 liveness 는 유지 (K8s가 재시작 결정)
        import logging
        logging.getLogger(__name__).warning("Dependency init failed (degraded): %s", exc)
        _ready = False
    yield
    _ready = False


app = FastAPI(
    title="QT-AI AI Service",
    version="1.2.0",
    description="큐티 AI 코칭 서비스 -- SSE 스트리밍 + ChromaDB RAG",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(sessions.router, prefix="/ai/sessions", tags=["sessions"])
app.include_router(messages.router, prefix="/ai/sessions", tags=["messages"])
app.include_router(templates.router, prefix="/ai/prompt-templates", tags=["templates"])


# ── Health Probe endpoints ──────────────────────────────────────────────
@app.get("/actuator/health/liveness", tags=["health"])
async def liveness():
    """K8s livenessProbe -- 프로세스가 살아있으면 항상 200 (재시작 여부 판단용)"""
    return {"status": "UP"}


@app.get("/actuator/health/readiness", tags=["health"])
async def readiness():
    """K8s readinessProbe -- DB/Chroma 연결 완료 후 200 (트래픽 수신 여부 판단용)"""
    if _ready:
        return {"status": "UP"}
    from fastapi import Response
    return Response(
        content='{"status":"OUT_OF_SERVICE","detail":"dependency initializing"}',
        status_code=503,
        media_type="application/json",
    )


@app.get("/actuator/health", tags=["health"])
async def health():
    """기존 호환 -- liveness + readiness 통합 응답"""
    return {
        "status": "UP" if _ready else "OUT_OF_SERVICE",
        "service": "ai-service",
        "components": {
            "liveness":  {"status": "UP"},
            "readiness": {"status": "UP" if _ready else "OUT_OF_SERVICE"},
        },
    }