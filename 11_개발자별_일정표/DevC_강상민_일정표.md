# QT-AI -- DevC (강상민) AI/RAG Service 상세 일정표 v2.0

> 이 문서 목적: Python FastAPI 기반 AI/RAG Service를 처음부터 완성하는 가이드.
> 이 서비스만 Kotlin 이 아닌 Python 이다. Gradle 멀티모듈과 별도로 실행한다.

문서 버전: v2.0 | 작성일: 2026-05-08 | 담당자: 강상민
연관 문서: 04_API_명세서 v1.2 / 09_AI_프롬프트_운영_가이드 v1.0

---

## 0. AI Service가 하는 일

AI Service는 큐티(QT) 코칭 AI를 제공한다.

```
사용자가 성경 구절 선택 --> AI 세션 생성 (A단계: 관찰)
사용자가 질문 입력 --> Claude API에 스트리밍 요청 --> 토큰 단위로 Flutter에 전송
단계 진행: A(관찰) --> B(해석) --> C(적용) --> D(결단)
세션 완료 --> Kafka "ai.session.completed" 이벤트 발행
```

**만들어야 하는 API**
```
POST  /ai/sessions                    큐티 세션 생성
GET   /ai/sessions                    내 세션 목록
GET   /ai/sessions/{id}               세션 상세 + 대화 이력
POST  /ai/sessions/{id}/messages      AI 대화 (SSE 스트리밍)
PATCH /ai/sessions/{id}/advance       단계 진행 A --> B --> C --> D
GET   /ai/prompt-templates            프롬프트 템플릿 목록
```

**이 서비스가 다른 서비스와 다른 점**
- Python 3.11 + FastAPI (Spring Boot 가 아니다)
- `.\gradlew.bat` 으로 실행하지 않는다
- `uvicorn main:app --port 8085` 로 실행한다
- `ai-service/` 폴더 안에서만 작업한다

---

## 1. W0 말 -- RAG 시드 데이터 준비 (최우선, 5/10~5/11)

### 왜 이게 최우선인가?

W2 에 AI 1턴 테스트를 하려면 ChromaDB 에 신학 주석 데이터가 있어야 한다.
데이터 없이는 RAG 검색 결과가 0 건이 되고 AI 응답 품질이 크게 떨어진다.
따라서 W1 이 시작되기 전에 최소 5개 이상 주석이 ChromaDB 에 들어가야 한다.

### Python 환경 구성

```bash
cd C:\workspace\2nd-Team-Project\ai-service

# Python 버전 확인 (3.11 이상이어야 함)
python --version

# 가상환경 생성
# "왜 가상환경을 쓰는가?" --> 프로젝트마다 다른 버전의 패키지를 쓸 수 있게 분리
python -m venv venv

# 가상환경 활성화 (Windows PowerShell)
venv\Scripts\Activate.ps1
# 프롬프트 앞에 (venv) 가 붙으면 성공

# 의존성 설치
pip install -r requirements.txt
```

### scripts/rag_index.py 작성 + 실행

```python
# ai-service/scripts/rag_index.py
"""
ChromaDB 에 신학 주석 시드 데이터를 적재하는 스크립트.
서비스 시작 전에 한 번만 실행한다.
"""
import chromadb

client = chromadb.HttpClient(host="localhost", port=8000)

collection = client.get_or_create_collection(
    name="qtai_corpus",
    metadata={"hnsw:space": "cosine"}   # 코사인 유사도로 검색
)

documents = [
    "요한복음 3:16은 복음의 핵심 구절이다. 하나님의 사랑은 세상을 향한 것으로, 독생자를 주심으로 표현되었다.",
    "독생자를 주셨다는 표현은 하나님의 사랑이 실제 행동으로 나타났음을 의미한다.",
    "믿는 자마다 영생을 얻는다는 약속은 조건이 오직 믿음임을 강조한다.",
    "요한복음 3장에서 니고데모와의 대화는 거듭남의 본질을 다룬다.",
    "큐티 관찰 단계: 본문에서 무엇이 보이는지, 누가 등장하는지를 사실 그대로 확인한다.",
    "큐티 해석 단계: 이 말씀이 원래 독자들에게 무슨 의미였는지를 탐구한다.",
    "큐티 적용 단계: 이 말씀이 오늘 나의 삶에 어떻게 연결되는지를 구체적으로 찾는다.",
    "큐티 결단 단계: 오늘 실천할 수 있는 구체적인 행동 하나를 결단한다.",
    "요한복음 3:16에서 영생은 하나님과의 관계 속에서 누리는 풍성한 생명이다."
]

metadatas = [
    {"book": "JHN", "chapter": 3, "verse": 16, "type": "commentary"},
    {"book": "JHN", "chapter": 3, "verse": 16, "type": "commentary"},
    {"book": "JHN", "chapter": 3, "verse": 16, "type": "commentary"},
    {"book": "JHN", "chapter": 3, "verse": 1,  "type": "commentary"},
    {"book": "QT",  "chapter": 0, "verse": 0,  "type": "qt_guide", "stage": "A"},
    {"book": "QT",  "chapter": 0, "verse": 0,  "type": "qt_guide", "stage": "B"},
    {"book": "QT",  "chapter": 0, "verse": 0,  "type": "qt_guide", "stage": "C"},
    {"book": "QT",  "chapter": 0, "verse": 0,  "type": "qt_guide", "stage": "D"},
    {"book": "JHN", "chapter": 3, "verse": 16, "type": "commentary"},
]

ids = [f"doc_{i}" for i in range(len(documents))]

collection.upsert(documents=documents, metadatas=metadatas, ids=ids)
print(f"ChromaDB 에 {collection.count()}개 문서 적재 완료")

# 테스트 검색
results = collection.query(
    query_texts=["요한복음 3:16 하나님의 사랑"],
    n_results=3
)
print("\n검색 테스트:")
for doc in results["documents"][0]:
    print(f"  - {doc[:60]}...")
```

```bash
# ChromaDB 로컬 실행 (K8s 없이 테스트할 때)
pip install chromadb
chroma run --path ./chroma_data --port 8000

# 다른 터미널에서 시드 스크립트 실행
python scripts/rag_index.py
# 기대 출력:
# ChromaDB 에 9개 문서 적재 완료
```

---

## 2. Day1~2 -- 5/12~5/13: Alembic DB 마이그레이션

### Alembic 이란?

Python 에서 Flyway 역할을 하는 도구다.
DB 스키마를 버전으로 관리한다.

```bash
# ai-service 폴더에서 (가상환경 활성화 상태)
alembic init alembic    # alembic/ 폴더 생성
```

**SQLAlchemy 모델 작성** (app/infrastructure/models.py):

```python
# ai-service/app/infrastructure/models.py
from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Enum, Text
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class AiSession(Base):
    __tablename__ = "ai_sessions"

    session_id    = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id       = Column(BigInteger, nullable=False, index=True)
    book          = Column(String(10), nullable=False)
    chapter       = Column(Integer, nullable=False)
    verse         = Column(Integer, nullable=False)
    # 큐티 단계: A(관찰), B(해석), C(적용), D(결단)
    current_stage = Column(Enum("A","B","C","D"), nullable=False, default="A")
    status        = Column(Enum("ACTIVE","COMPLETED","ABANDONED"), nullable=False, default="ACTIVE")
    created_at    = Column(DateTime, nullable=False, default=datetime.now)
    updated_at    = Column(DateTime, nullable=False, default=datetime.now, onupdate=datetime.now)


class AiTurn(Base):
    __tablename__ = "ai_turns"

    turn_id    = Column(BigInteger, primary_key=True, autoincrement=True)
    session_id = Column(BigInteger, nullable=False, index=True)
    role       = Column(Enum("USER","ASSISTANT"), nullable=False)
    content    = Column(Text, nullable=False)
    stage      = Column(Enum("A","B","C","D"), nullable=False)
    input_tokens  = Column(Integer)   # 비용 추적용
    output_tokens = Column(Integer)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
```

```bash
# 마이그레이션 파일 생성
alembic revision --autogenerate -m "create ai tables"

# 마이그레이션 실행 (DB에 테이블 생성)
alembic upgrade head
```

---

## 3. Day3~5 -- 5/14~5/16: SSE 스트리밍 동작 확인

### SSE (Server-Sent Events) 란?

서버가 클라이언트에게 데이터를 실시간으로 스트리밍하는 방식이다.
Claude API 가 토큰을 하나씩 생성할 때마다 즉시 클라이언트로 전송한다.

```
클라이언트가 POST /ai/sessions/1/messages 요청
서버: data: {"type":"token","data":"하나"}\n\n
서버: data: {"type":"token","data":"님이"}\n\n
...
서버: data: {"type":"done","data":""}\n\n
```

### chat_usecase.py -- SSE 스트리밍 구현

```python
# ai-service/app/usecase/chat_usecase.py
import json
from typing import AsyncIterator
import anthropic
import chromadb

# 큐티 단계별 시스템 프롬프트
STAGE_SYSTEM_PROMPTS = {
    "A": """당신은 큐티(QT) 코치입니다. 지금은 '관찰' 단계입니다.

역할: 사용자가 성경 본문에서 보이는 사실을 관찰하도록 돕는다.
방법: 소크라테스식 질문으로 직접 답을 알려주지 않고 스스로 발견하게 한다.

질문 예시:
- "이 본문에 누가 등장하나요?"
- "어떤 사건이 일어나고 있나요?"

주의: 해석이나 적용은 하지 말 것. 관찰 사실에만 집중.
금지: 이단적 교리나 비성경적 해석 지지 금지.""",

    "B": """당신은 큐티(QT) 코치입니다. 지금은 '해석' 단계입니다.

역할: 관찰한 사실이 무엇을 의미하는지 발견하도록 돕는다.
방법: 역사적, 문화적 배경과 원어 의미를 탐구하게 한다.

질문 예시:
- "이 말씀이 원래 독자들에게 어떤 의미였을까요?"
- "독생자라는 표현이 무엇을 강조하나요?" """,

    "C": """당신은 큐티(QT) 코치입니다. 지금은 '적용' 단계입니다.

역할: 말씀이 오늘 나의 삶과 어떻게 연결되는지 발견하도록 돕는다.
방법: 구체적인 삶의 상황에 연결하는 질문을 한다.

질문 예시:
- "이 말씀이 오늘 나의 어떤 상황과 연결되나요?" """,

    "D": """당신은 큐티(QT) 코치입니다. 지금은 '결단' 단계입니다.

역할: 오늘 실천할 수 있는 구체적인 결단을 내리도록 돕는다.
방법: 추상적 결단이 아닌 오늘 실천 가능한 행동 하나로 좁혀준다.

질문 예시:
- "오늘 이 말씀에 응답하여 무엇을 하겠습니까?" """
}


class ChatUseCase:

    def __init__(self):
        # AsyncAnthropic: 비동기 Claude API 클라이언트
        # ANTHROPIC_API_KEY 환경변수에서 자동으로 읽음
        self.anthropic = anthropic.AsyncAnthropic()
        self.chroma = chromadb.HttpClient(host="localhost", port=8000)
        self.collection = self.chroma.get_or_create_collection("qtai_corpus")

    async def stream_response(
        self, session_id: int, request, stage: str,
        book: str, chapter: int, verse: int
    ) -> AsyncIterator[str]:
        """SSE 스트리밍 응답 생성"""

        # 1. RAG: ChromaDB 에서 관련 주석 검색
        rag_results = self.collection.query(
            query_texts=[request.userMessage],
            n_results=3,
            where={"book": book}
        )
        context = "\n".join(rag_results["documents"][0]) if rag_results["documents"] else ""

        # 2. 시스템 프롬프트 구성
        system_prompt = STAGE_SYSTEM_PROMPTS.get(stage, STAGE_SYSTEM_PROMPTS["A"])
        if context:
            system_prompt += f"\n\n[참고 자료]\n{context}"

        # 3. Claude API 스트리밍 호출
        async with self.anthropic.messages.stream(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            system=system_prompt,
            messages=[{"role": "user", "content": request.userMessage}]
        ) as stream:
            async for text in stream.text_stream:
                # SSE 형식: "data: JSON\n\n"
                yield f"data: {json.dumps({'type': 'token', 'data': text, 'sessionId': session_id, 'stage': stage}, ensure_ascii=False)}\n\n"

        yield f"data: {json.dumps({'type': 'done', 'data': '', 'sessionId': session_id, 'stage': stage})}\n\n"
```

### SSE 동작 테스트

```bash
# FastAPI 서버 실행
cd C:\workspace\2nd-Team-Project\ai-service
venv\Scripts\Activate.ps1
uvicorn main:app --reload --port 8085

# SSE 테스트 (-N: 버퍼링 없이 스트림 출력)
curl -N -X POST http://localhost:8085/ai/sessions/1/messages \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d "{\"userMessage\":\"요한복음 3:16에서 무엇을 관찰할 수 있나요?\"}"

# 기대 출력:
# data: {"type":"token","data":"요","sessionId":1,"stage":"A"}
# ...
# data: {"type":"done","data":"","sessionId":1,"stage":"A"}
```

---

## 4. Day6~9 -- 5/19~5/22: SessionUseCase DB 실구현

### session_usecase.py -- 501 stub 에서 실 구현으로

W0 에서 만든 session_usecase.py 의 모든 메서드가 501 을 반환한다.
이것을 실제 DB 연결로 바꾼다.

```python
# ai-service/app/usecase/session_usecase.py
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.infrastructure.models import AiSession

class SessionUseCase:

    async def create_session(self, request, user_id: int, db: AsyncSession) -> dict:
        """새 큐티 세션 생성"""
        new_session = AiSession(
            user_id       = user_id,
            book          = request.book,
            chapter       = request.chapter,
            verse         = request.verse,
            current_stage = "A",
            status        = "ACTIVE"
        )
        db.add(new_session)
        await db.commit()
        await db.refresh(new_session)   # DB 에서 auto_increment ID 가져오기
        return self._to_dict(new_session)

    async def get_session_or_404(self, session_id: int, user_id: int, db: AsyncSession) -> dict:
        """세션 조회 + 소유권 확인"""
        result = await db.execute(
            select(AiSession).where(AiSession.session_id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"code": "AI_SESSION_NOT_FOUND", "message": "세션을 찾을 수 없습니다."}
            )

        if session.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "FORBIDDEN", "message": "접근 권한이 없습니다."}
            )

        return self._to_dict(session)

    def _to_dict(self, session: AiSession) -> dict:
        return {
            "sessionId":    session.session_id,
            "userId":       session.user_id,
            "book":         session.book,
            "chapter":      session.chapter,
            "verse":        session.verse,
            "currentStage": session.current_stage,
            "status":       session.status
        }
```

### 동작 확인 순서

```bash
# 1. DB 마이그레이션 완료 확인
alembic upgrade head

# 2. 서버 재시작
uvicorn main:app --reload --port 8085

# 3. 세션 생성 테스트
curl -X POST http://localhost:8085/ai/sessions \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d "{\"book\":\"JHN\",\"chapter\":3,\"verse\":16,\"templateType\":\"GENERAL\"}"
# 기대: {"sessionId":1,"userId":1,"book":"JHN",...}

# 4. SSE 스트리밍 테스트 (실제 Claude API 호출)
curl -N -X POST http://localhost:8085/ai/sessions/1/messages \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d "{\"userMessage\":\"3:16에서 무엇을 발견했나요?\"}"
```

---

## 5. 자주 발생하는 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `ModuleNotFoundError: fastapi` | 가상환경 비활성화 | `venv\Scripts\Activate.ps1` 실행 |
| `chromadb.errors.NotFoundError` | 컬렉션 없음 | `python scripts/rag_index.py` 먼저 실행 |
| `anthropic.AuthenticationError` | API Key 없음 | `.env` 파일에 `ANTHROPIC_API_KEY=sk-ant-...` 설정 |
| `422 Unprocessable Entity` | 요청 JSON 필드명 오류 | camelCase 확인 (userMessage, sessionId) |
| `alembic.util.exc.CommandError` | DB 연결 실패 | `AI_DB_URL` 환경변수 확인 |
| SSE가 한꺼번에 와서 스트리밍 아님 | curl -N 옵션 없음 | `curl -N` 사용 또는 Gateway NoBufferingFilter 확인 |

---

## 6. W2~W4 주간 요약

| 주차 | 강상민 핵심 작업 |
|------|----------------|
| W2 (5/26~5/29) | 신학 가드레일 프롬프트 추가, 큐티 4단계 E2E 테스트, /advance API 완성 |
| W3 (6/1~6/5) | Kafka ai.session.completed 발행, SSE P95 측정 (목표 2000ms 이하) |
| W4 (6/8~6/12) | 시연 큐티 D단계 완결 시나리오 dry-run, pytest 커버리지 70%+ |
