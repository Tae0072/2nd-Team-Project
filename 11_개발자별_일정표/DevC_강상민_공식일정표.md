# 📋 QT-AI — Dev C (강상민) 상세 일정표

문서 버전: v1.0
작성일: 2026-05-08
담당자: 강상민
역할: AI/RAG Service Owner (팀 내 기술적 깊이 최고)
담당 서비스: AI/RAG Service — Python FastAPI + Anthropic Claude SSE + ChromaDB RAG
개발 기간: W1(5/12) ~ W5(6/17)
연관 문서: 00_개발_일정_총괄표 / 02_ERD_문서 v1.3 / 04_API_명세서 v1.5 / 09_AI_프롬프트_운영_가이드 v1.0

---

## 0. 역할 핵심 선언

> **"AI 없이는 이 앱이 존재하지 않는다."**
> AI/RAG Service는 QT-AI의 핵심 가치인 소크라테스식 큐티 코칭을 담당한다.
> SSE 스트리밍 응답 품질, 신학 가드레일, 큐티 A~D 단계 프롬프트 설계가
> 시연에서 가장 강렬한 인상을 남기는 부분이다.
> 팀에서 유일한 Python FastAPI 서비스이므로 독립적으로 빌드·배포한다.

### 공통 PR 완료 조건

> 모든 코드 PR은 테스트 코드 작성 후 단위 테스트와 통합 테스트가 모두 통과해야 완료로 인정한다.

- [ ] 변경 범위 테스트 코드 작성 완료 (문서-only PR은 사유 명시)
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] PR 본문에 테스트 명령과 통과 결과 첨부
- [ ] 미충족 시 Draft 유지, 머지 금지

---

## 1. 소유권 선언

```
ai-service/                         ← 전담 소유 (Python FastAPI, 포트 8085)
  ├── main.py                       (FastAPI 앱 엔트리포인트)
  ├── requirements.txt
  ├── Dockerfile
  ├── app/
  │   ├── api/v1/
  │   │   ├── sessions.py           (세션 CRUD — 현재 501 stub)
  │   │   ├── turns.py           (SSE 스트리밍 — ChatUseCase 연결)
  │   │   └── templates.py          (프롬프트 템플릿 조회)
  │   ├── domain/
  │   │   └── schemas.py            (Pydantic 모델 — camelCase alias)
  │   ├── infrastructure/
  │   │   ├── chroma.py             (ChromaDB 클라이언트)
  │   │   └── database.py           (SQLAlchemy MySQL)
  │   └── usecase/
  │       ├── chat_usecase.py       (AsyncAnthropic SSE 스트리밍)
  │       └── session_usecase.py    (세션 CRUD — W1 구현 예정)
  └── scripts/
      └── rag_index.py              (ChromaDB 시드 스크립트 — W0 준비 필요)

alembic/                            (DB 마이그레이션)
```

**팀에 제공하는 공개 인터페이스**
- `POST /ai/sessions/{id}/turns` (SSE) — Flutter가 `dio_sse`로 수신
- `- 단계 완료 시 → Kafka `ai.session.completed` 이벤트 발행 (W3)

---

## 2. AI Service 핵심 기술 요구사항

| 요구사항 | 구현 방식 | 완료 목표 | 왜 중요한가 |
|---------|-----------|-----------|-------------|
| RAG 시드 데이터 | `rag_index.py` — 신학 주석 5종 이상 ChromaDB 적재 | **W0 말~W1 초 (최우선)** | 없으면 W2 AI 1턴 테스트 불가 |
| Claude SSE 스트리밍 | `AsyncAnthropic` + `async with stream` | W1 수 (골격 완료, 실DB 연결은 W2) | 시연 핵심 기능 |
| 큐티 A~D 프롬프트 | 09번 문서 기준 시스템 프롬프트 4종 | W1 목 | 코칭 품질 좌우 |
| 신학 가드레일 | 시스템 프롬프트에 가드레일 문구 삽입 | W2 화 | 이단·비신학적 응답 차단 |
| DB 실구현 | Alembic + AI_SESSIONS·AI_TURNS 테이블 | W2 월 | 세션 이력 저장 |
| Kafka 발행 | `ai.session.completed` (confluent-kafka) | W3 월 | Journal Service Saga 트리거 |

---

## 3. 일별 상세 일정

### 🟦 W0 말 (5/10~5/11) — RAG 시드 준비 ← **최우선**

```
W1 AI 1턴 테스트를 위해 ChromaDB 시드가 W1 시작 전에 준비되어야 한다.
```

| 작업 | 내용 |
|------|------|
| `scripts/rag_index.py` 작성 | sentence-transformers 임베딩 + ChromaDB 적재 |
| 신학 주석 원문 수집 | Matthew Henry, 한국성경주석 등 공개 도메인 5종 이상 (JHN 3장 집중) |
| 로컬 ChromaDB 테스트 실행 | `python scripts/rag_index.py` → collection size ≥ 5 확인 |

---

### 🟩 W1 (5/12~5/22)

| 일자 | 오전 | 오후 코어 | 저녁 |
|------|------|-----------|------|
| 5/12 화 | 킥오프 참석. Python venv 구성 | `pip install -r requirements.txt`. ChromaDB K8s 배포 확인 | `rag_index.py` 실행 — collection size 확인 |
| 5/13 화 | Stand-up | Alembic 초기화. AI_SESSIONS 마이그레이션 작성 | AI_TURNS 마이그레이션 작성 |
| 5/14 수 | Stand-up | `ChatUseCase.stream_response()` — DB 연결 없이 하드코딩으로 SSE 동작 확인 | curl SSE 테스트: `curl -N http://localhost:8085/ai/sessions/1/turns` |
| 5/15 목 | Stand-up | 큐티 A~D 시스템 프롬프트 4종 (`STAGE_SYSTEM_PROMPTS`) 작성 (09번 참조) | 단계별 응답 품질 셀프 테스트 |
| 5/16 금 | Stand-up | `SessionUseCase` DB 실구현 시작 (create_session) | `/ai/sessions` POST → 201 반환 확인 |
| 5/19 월 | Stand-up | `SessionUseCase` 전체 CRUD 구현 (get, list, advance) | 세션 단계 진행 (A→B) 테스트 |
| 5/20 화 | Stand-up | `turns.py` — 세션 존재·소유권 검증 완성 | pytest 기본 테스트 작성 |
| 5/21 수 | Stand-up | Gateway 경유 SSE 테스트 (강태오 협력) — NoBufferingFilter 동작 확인 | 단계별 프롬프트 품질 재검토 |
| 5/22 목 | Stand-up | **W1 Lock-in 게이트 참석 (18:00)** | W1 회고 |

**W1 완료 기준**
- [ ] `POST /ai/sessions` → 201 세션 생성
- [ ] `POST /ai/sessions/1/turns` → SSE 스트림 첫 토큰 수신
- [ ] ChromaDB RAG 컨텍스트 검색 결과 ≥ 1건
- [ ] 큐티 A단계 프롬프트 응답 품질 셀프 확인
- [ ] Alembic 마이그레이션 성공

---

### 🟨 W2 (5/26~5/29)

| 일자 | 주요 작업 |
|------|-----------|
| 5/26 화 | 페이스 점검 (11:30). 신학 가드레일 시스템 프롬프트 추가 (이단 탐지 문구) |
| 5/27 수 | `| 5/28 목 | `GET /ai/prompt-templates` DB 연결 완성. Bible Service 연동 (강태오·김태혁 협력) |
| 5/29 금 | pytest 커버리지 60%+. `/ai/sessions` 목록·상세 API 완성 |

---

### 🟧 W3 (6/1~6/5) + 🟥 W4 (6/8~6/12)

| 주차 | 주요 작업 |
|------|-----------|
| W3 | Kafka `ai.session.completed` 이벤트 발행 (confluent-kafka). SSE P95 ≤ 2000ms 측정. 프롬프트 인젝션 방어 테스트 |
| W4 | 큐티 D단계 완결 시나리오 시연 dry-run. pytest 커버리지 70%+ |

---

## 4. 큐티 A~D 프롬프트 설계 원칙 (09번 요약)

```python
# 각 단계별 핵심 지침
A (관찰): "본문에서 무엇이 보이는가?" → 관찰 사실만, 해석 금지
B (해석): "이 말씀의 의미는?" → 역사·문화적 배경, 원어 의미 활용
C (적용): "내 삶에 어떻게 적용하는가?" → 구체적 상황 이끌어내기
D (결단): "오늘 무엇을 결단하는가?" → 실천 가능한 행동 1가지로 좁히기

# 공통 가드레일 (모든 단계에 삽입)
"이단적 교리, 비성경적 해석, 개인의 주관적 신학을 지지하지 마세요.
 잘 모르겠으면 '성경 원문을 다시 살펴보겠습니다'로 돌아오세요."
```

---

## 5. AI 에이전트 활용 가이드

| 단계 | Claude 활용처 | 주의사항 |
|------|--------------|----------|
| W1 | Alembic DDL 초안, FastAPI 라우터 패턴 | DB URL·API Key Claude에 입력 금지 |
| W2 | Kafka producer 코드, pytest fixture | 실제 Kafka 토픽명 03번 문서와 대조 |
| W3 | 프롬프트 튜닝 반복 실험 | 시스템 프롬프트 길이 ≤ 4000자 유지 |
| 전체 | ANTHROPIC_API_KEY는 절대 Claude에 붙여넣기 금지 | K8s Secret 경로만 공유 |
