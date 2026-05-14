# DECISIONS.md — QT-AI 단일 기준표

> 이 파일은 분산된 문서들에서 충돌할 수 있는 **포트·TTL·Route·Envelope·DB·인프라·저작권** 값의
> **단일 진실 원천(Single Source of Truth)** 이다.
> 문서 간 값이 다르면 이 파일이 정답. 수정 시 이 파일과 해당 문서를 동시에 PR.

---

## 📌 변경 이력

| 날짜 | 주요 변경 |
| --- | --- |
| 2026-05-12 | Auth Service 제거, Journal Service → Bible Service 통합, AI 팀원 3인, LLM DeepSeek 전환 |
| 2026-05-13 (오전) | MVP 범위 확정 — 한 절 고정, AI 1회성 Q&A, 자동 저장 4필드, 첫 화면 = 오늘 QT |
| 2026-05-13 (오후) | AI 에이전트 3종 분화(해설 생성·편집자·시뮬레이터), QT 콘텐츠 합법 소싱 방향 |
| **2026-05-14** | **MSA → Modular Monolith 전환** · **RAG/벡터 DB/엘라스틱서치 제외** · **Kafka·K8s 보류(v2 분리 시 도입)** · **팀 재배치(Bible팀 3인 = 이지윤·이승욱·김지민)** · **QT 본문 19:00 스크래핑 수집** · **"주석 → 해설" 전면 리네이밍** · **`rag_sources → sources`** |

---

## 0. 팀 구성 및 담당 (2026-05-14 재배치)

| 팀원 | 역할 | 담당 |
| --- | --- | --- |
| 강태오 | **Lead · DevOps** (단일 파트 고정 X) | 전체 조율, PR 검증 스크립트, 인프라, 컨벤션, 횡단 지원 |
| 강상민 | **AI 주도** | AI 해설 생성, 편집자 에이전트, AI 자동 검증 메커니즘 정의 |
| 김태혁 | Dev | 시뮬레이터 (스프라이트 기반 검토 중) |
| 이지윤 | **Bible팀** | Bible 도메인 → Flutter → 인증 → 관리자 페이지 / 편집자 에이전트 보조 큐레이션·골든셋 |
| 이승욱 | **Bible팀 · Flutter 빌드 책임자** (시연 6/17) | Bible 도메인 → Flutter → 인증 → 관리자 페이지 |
| 김지민 | **Bible팀** | Bible 도메인 → Flutter → 인증 → 관리자 페이지 |

> **Bible팀 작업 순서:** Bible 프로토타입으로 작동 확인 → Flutter → 인증 → 관리자 페이지 일괄 진행.
> **변경 요지:** AI 주도자 강태오 → 강상민, 김지민 Flutter 단독 → Bible팀 합류, 이지윤 1차 검증 → 보조 큐레이션·골든셋.

---

## 1. 서비스 포트 (Modular Monolith)

| 컴포넌트 | 로컬 포트 | Docker 포트 | 비고 |
| --- | --- | --- | --- |
| **`qtai-server` (단일 서비스)** | 8080 | 8080 | 도메인 패키지 `bible`·`ai`·`journal`·`gateway-auth`·`bff`로 경계 |
| Flutter Mock Server (Prism) | 4010 | — | OpenAPI mock |
| MySQL | 3306 | 3306 | **단일 DB `qtai_db`**, 도메인별 테이블 prefix |
| Redis | 6379 | 6379 | 캐시 + 세션 + WS 레지스트리 |
| Kafka | — | — | **v2 분리 시 도입 (보류)** |
| Schema Registry | — | — | **v2 분리 시 도입 (보류)** |
| ChromaDB | — | — | **사용 안 함** (2026-05-14 제외) |
| K8s / Helm | — | — | **v2 분리 시 도입 (보류)** |

> **단일 포트 8080.** Gateway·BFF·Bible·AI 모두 동일 프로세스 내 도메인 패키지.
> **단일 DB `qtai_db`.** 도메인별 테이블 prefix(`bible_*`, `ai_*`, `journal_*`, `auth_*`).
> OpenAPI는 도메인별 분할 유지(`apis/{ai,bff,bible}/openapi.yaml`) — 단일 서비스가 모두 서빙.

---

## 2. 토큰 정책

| 항목 | 값 | 근거 |
| --- | --- | --- |
| Access Token 유효기간 | **30분 (1800s)** | 03번 § 11.1 |
| Refresh Token 유효기간 | **14일** | 03번 § 11.1 (v1.1에서 7일 단축 검토) |
| Refresh blacklist | Redis `auth:refresh:revoked:{jti}` TTL=만료까지 | 03번 § 11.1 |
| Access blacklist | **없음** (30분 단명) | ADR-0012 단순화 정책 |
| JWT 알고리즘 | RS256 | 03번 § 11.1 |

> JWT 발급·검증은 `gateway-auth` 도메인 패키지에서 처리. expiresIn: 1800이 기준.

---

## 3. API Route 확정 (Gateway 라우팅 표 요약)

| 용도 | External Path | 내부 도메인 | 인증 |
| --- | --- | --- | --- |
| 오늘의 QT 미리보기 | `GET /api/v1/qt/today` | bff | ❌/✅ |
| 입체 묵상 화면 | `GET /api/v1/passages/{bookCode}/{chapter}/{verse}` | bff | ❌/✅ |
| 대시보드 | `GET /api/v1/me/dashboard` | bff | ✅ |
| 한글 성경 | `GET /bible/kr/{bookCode}/{ch}/{v}` | bible | ❌ |
| 영어 성경 | `GET /bible/en/{bookCode}/{ch}/{v}` | bible | ❌ |
| 쉬운 본문 설명 | `GET /api/v1/explanations/{bookCode}/{ch}/{v}` | bible | ❌ |
| **해설** | `GET /api/v1/explanations/commentary/{bookCode}/{ch}/{v}` | bible | ✅ |
| 성경 목록 | `GET /bible/books` | bible | ❌ |
| 오늘 QT 묵상 DRAFT 생성/조회 | `POST /api/v1/journals/today` | bible (journal) | ✅ |
| 묵상 노트 목록 | `GET /api/v1/journals` | bible (journal) | ✅ |
| 묵상 노트 단건 | `GET /api/v1/journals/{id}` | bible (journal) | ✅ |
| 묵상 노트 수정 | `PATCH /api/v1/journals/{id}` | bible (journal) | ✅ |
| 묵상 노트 삭제 | `DELETE /api/v1/journals/{id}` | bible (journal) | ✅ |
| 이벤트 로그 | `GET /api/v1/journals/{id}/events` | bible (journal) | ✅ |
| AI 세션 시작 | `POST /ai/sessions` | ai | ✅ |
| AI 대화 (SSE) | `POST /ai/sessions/{id}/turns` | ai | ✅ |
| AI 세션 묵상 완료 | `POST /ai/sessions/{id}/complete` | ai | ✅ |
| AI 세션 조회 | `GET /ai/sessions/{id}` | ai | ✅ |
| AI 세션 목록 | `GET /ai/sessions` | ai | ✅ |
| 익명 나눔 목록 | `GET /api/v1/shares` | bible (journal) | ❌ |
| 익명 나눔 공개/취소 | `POST/DELETE /api/v1/journals/{id}/share` | bible (journal) | ✅ |
| 익명 나눔 좋아요 | `POST/DELETE /api/v1/shares/{shareId}/likes` | bible (journal) | ✅ |
| 익명 나눔 댓글 | `GET/POST /api/v1/shares/{shareId}/comments` | bible (journal) | ❌/✅ |
| 익명 나눔 신고 | `POST /api/v1/shares/{shareId}/reports` | bible (journal) | ✅ |
| 관리자 운영 API | `/api/v1/admin/**` | bff | ✅ ROLE_ADMIN |
| WebSocket 알림 | `WS /ws/notifications` | bff | ❌ (STOMP CONNECT 헤더) |

> **AI SSE endpoint:** `/ai/sessions/{id}/turns` (turns가 정식명, /messages 금지)
> **SSE 응답 필드:** `rag_sources` → **`sources`** 로 리네이밍 (2026-05-14). 의미는 사용된 사전 적재 해설 row 출처 배열.
> **용어 리네이밍:** UI·DB·API 모두 "주석" → **"해설"**. `COMMENTARIES → EXPLANATIONS`, `commentary_* → explanation_*`. 변경 영향은 02_ERD·04_API·08_Flutter·09_AI에서 동기 갱신.
> **소프트 로그인 정책:** 첫 진입 강제 로그인 없음. 튜토리얼·성경 본문·오늘의 QT 미리보기는 비로그인 허용, 해설 열람·AI 질문·묵상 기록·찬양 저장/공유는 로그인 필수.
> **BFF 입체 묵상 화면 인증:** 비로그인 요청은 한/영 본문과 오늘의 QT 미리보기만 반환하고, 해설·개인화 데이터는 로그인 후 제공한다.
> **Journal 생성 범위:** 자유 본문용 `POST /api/v1/journals`는 없다. MVP에서는 오늘의 QT 기준 DRAFT만 `POST /api/v1/journals/today`로 멱등 생성/조회하고, AI 완료(`ai.session.completed`)는 같은 오늘 QT Journal에 AI 요약을 연결한다.
> **계정 탈퇴 MVP 제외:** `user.deactivated` 이벤트 및 관련 API 미구현.

---

## 3.1 MVP 제품 범위 확정 (2026-05-13 오전 회의 — 유지)

| 항목 | 확정 |
| --- | --- |
| 오늘의 QT 본문 단위 | MVP는 **한 절 고정**. 단, DB/API는 `verseStart`, `verseEnd`를 사용하고 MVP에서는 두 값이 항상 같다. |
| 일반 성경 보기 | 책·장·절 조회 전용. 자유 본문 기반 AI 질문·묵상 기록은 MVP 제외. |
| AI 연결 범위 | AI 질문은 오늘의 QT 본문에서만 시작한다. 사용자가 여러 번 질문할 수 있지만 각 질문은 독립 1회성 Q&A다. |
| 본문 설명 | Bible 도메인 DB에 미리 저장한다. 필드는 쉬운 요약, 배경 설명, 어려운 단어, 출처. 적용 질문은 AI가 담당한다. |
| AI 응답 저장 | 필수. 이상 응답 디버깅과 관리자 모니터링 목적이다. |
| 묵상 기록 | 오늘 QT 기준 4필드(`felt`, `memorableVerse`, `application`, `prayer`)를 자동 저장한다. 사용자 입력 글자 수 제한은 두지 않는다. |
| 공개/나눔 | 기본 비공개. 전체 공개/비공개만 MVP에 포함하고 세분화 공개 범위는 후속 버전. 좋아요·댓글·신고는 MVP 포함, 팔로우는 제외. |
| 찬양 | AI가 오늘 QT 주제 기반 곡을 추천하고 사용자는 추천곡 저장/제거만 한다. 직접 YouTube URL 입력, 가사·음원 저장, 스트리밍 연동은 MVP 제외. |
| 교회 인증 | 기본 MVP 제외. 회원가입 화면에 선택 버튼만 둘 수 있으며, API가 확인되면 구현하고 없으면 패스한다. 교회 인증이 없어도 앱 사용 가능해야 한다. |
| 초기 화면·로딩 | 별도 홈 화면 없이 오늘 QT 화면으로 바로 진입한다. 필요해지면 홈을 추가한다. 오늘 QT 데이터 먼저 로딩 후 화면에 진입하고, 나머지 성경 데이터는 백그라운드 로딩한다. |
| 후속 검토 | 묵상 리포트, 묵상 달력, 목표 설정, 성장 일지, TTS/오디오북은 기본 기능 완료 후 재논의한다. |

---

## 4. 도메인 간 통신 (v1 in-process / v2 Kafka)

### 4.1 v1 — Modular Monolith in-process 이벤트 (현재 적용)

```java
// 표준 패턴
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
public void on(JournalCreatedEvent e) { ... }

applicationEventPublisher.publishEvent(new JournalCreatedEvent(...));
```

- Spring `ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)` 사용
- 동일 JVM 안에서 트랜잭션 경계를 넘는 통신
- 멱등성 키는 in-memory `Set` 대신 DB UNIQUE 제약 유지(추후 Kafka 전환 시 그대로 활용)

### 4.2 v2 — Kafka 분리 시 적용 (보류)

```json
{
  "eventId":         "evt_01HZX...",
  "eventType":       "ai.session.completed",
  "eventVersion":    1,
  "schemaSubject":   "ai.session.completed-value",
  "occurredAt":      "2026-05-26T14:30:00Z",
  "traceId":         "0af7651916cd43dd...",
  "producerService": "ai-service",
  "idempotencyKey":  "ai.session.completed:9012",
  "data":            { ... }
}
```

| 이벤트 | idempotencyKey 형식 | v1 in-process 핸들러 위치 |
| --- | --- | --- |
| user.activity.tracked | `read.passage:{userId}:{book}:{ch}:{v}:{epochMinute}` | bff 도메인 |
| ai.session.completed | `ai.session.completed:{sessionId}` | ai 도메인 (publish) → journal 도메인 (handle) |
| journal.created | `journal.created:{journalId}` | journal 도메인 |
| journal.updated | `journal.update:{ULID}` | journal 도메인 |
| journal.deleted | `journal.delete:{journalId}:{epochMs}` | journal 도메인 |
| journal.creation.failed | `journal.creation.failed:{sessionId}` | journal 도메인 |
| notification.requested | `{type}:{userId}:{occurredAt}` | 다수 → bff 도메인 |

> v1에서도 envelope 구조는 동일하게 유지 → v2 Kafka 전환 시 publisher만 교체.
> **payload 키 사용 금지** — 표준은 `data`.
> **user.deactivated 제거:** 계정 탈퇴 기능 MVP 범위 제외 (2026-05-12).

---

## 5. DB·인프라 스택

| 항목 | v1 선택 (Modular Monolith) | v2 (분리 시) | 금지 |
| --- | --- | --- | --- |
| RDBMS | **MySQL 8.0, 단일 DB `qtai_db`** (도메인 prefix) | DB per Service | ~~PostgreSQL~~ |
| 도메인 간 통신 | **Spring `ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)`** | Kafka KRaft | TX 안에서 KafkaTemplate.send() 직접 호출 |
| Kafka | **보류** | Apache Kafka KRaft single-node | ~~ZooKeeper~~ |
| Schema Registry | **보류** | Apicurio Registry 2.5+ | Confluent SR (라이선스) |
| Tracing | Jaeger + OpenTelemetry | 동일 | ~~Tempo~~ |
| Logs | Loki + Promtail | 동일 | |
| Metrics | Prometheus + Micrometer | 동일 | |
| Container Orchestration | **Docker Compose** | Kubernetes (Minikube) + Helm | |
| Secret 관리 | Docker `.env` (개발) / OS env (시연) | K8s Secret | ~~평문 application.yml~~ |
| **Vector Store** | **사용 안 함** | 사용 안 함 | ChromaDB / RAG / 벡터 DB / 엘라스틱서치 |
| Full-text Search | MySQL B-tree 인덱스 (필요 시 FULLTEXT) | 동일 | 엘라스틱서치 |

> **RAG / 벡터 DB / 엘라스틱서치 전부 제외 (2026-05-14).** 성경 본문은 장·절 단위로 정형화되어 RDB 셀렉트로 충분.

---

## 6. AI 도메인 스택

| 항목 | 결정 |
| --- | --- |
| 구현 언어/프레임워크 | **Spring Boot 3.3 / Java 21** |
| 패키지 위치 | `qtai-server`의 `com.qtai.ai` 도메인 패키지 |
| LLM | **DeepSeek API (OpenAI 호환, SSE 스트리밍)** |
| LLM 클라이언트 | **Spring `RestClient`** (OpenAI 호환 엔드포인트 직접 호출) |
| ~~Vector Store~~ | **사용 안 함** (2026-05-14 ChromaDB 제외, ADR-0013) |
| SSE 스트리밍 | Spring `SseEmitter` |
| 도메인 간 통신 | in-process 이벤트 (Kafka 보류) |
| DB | `qtai_db`의 `ai_*` 테이블 (`ai_sessions`, `ai_turns`, `prompt_templates`) |
| **해설 생성 파이프라인** | Public Domain 영어 주석(예: Matthew Henry) PDF → MD 변환 → LLM 비교 데이터로만 활용 → 자체 해설 생성 → **편집자 에이전트가 자동 검증** → 최종 "해설" 출력. 메커니즘 상세 정의는 **강상민 단독 작업**. |
| 출처 표시 | 화면에 표기(검증 거친 결과물로 인정) |

> **변경 이력:** v1.0 FastAPI → W0 Spring Boot 3.3 → W1 DeepSeek → **2026-05-14: ChromaDB·RAG 제외, 단일 서비스 패키지로 통합, 해설 생성 파이프라인 정의**.

---

## 7. 에러 응답 표준

| 항목 | 값 |
| --- | --- |
| Content-Type | `application/problem+json` |
| Schema | RFC 7807 ProblemDetail (`type`, `title`, `status`, `code`, `traceId`, `timestamp`) |
| 구버전 패턴 (금지) | `application/json` + `ErrorResponse{code, message, traceId}` |

---

## 8. 성경·QT 데이터 저작권 및 소싱

| 데이터 | 허용 | 사용 조건 |
| --- | --- | --- |
| KJV (영어 성경) | ✅ | Public Domain, 무조건 OK |
| 개역한글 | ⚠️ | 비상업·교육 목적 한정, 출처 표기 필수 |
| **새번역** | ⏸️ **pending** | **라이선스 확인 전까지 사용 금지.** 회의에서 도입 후보로 언급됐으나 대한성서공회 저작권 보호 가능성 높음. 이지윤이 라이선스 부서 회신 받기 전까지 본문 적재·앱 노출 모두 금지. 회신 결과에 따라 본 항목 갱신 |
| Matthew Henry 주석 (영문) | ✅ | Public Domain. **AI 비교 데이터로만 활용, 그대로 노출 X** |
| **개역개정** | ❌ **금지** | 대한성서공회 저작권 — commit 절대 금지 |
| **ESV / NIV** | ❌ **금지** | 라이선스 비용 필요 |
| 한글 상업 주석 / 신학 논문 | ❌ | 거의 100% 저작권 보호 — 사용 금지 |

### 8.1 QT 본문 소싱 (ADR-0014)

| 항목 | 내용 |
| --- | --- |
| 출처 | **성서 유니온** (수영로 교회 출판본과 동일 본문 확인) |
| 수집 방식 | **최소 메타데이터 수집** (좌표만, 본문 텍스트는 자체 DB). robots.txt·이용약관 확인 전까지 좌표 메타데이터만 최소 수집. 출판사가 명시적 거부하면 즉시 중단 |
| 가져오는 범위 | 그날 본문 좌표만 (예: "창세기 41:37–57"). 본문 텍스트는 가져오지 않음 |
| 갱신 시간 | **저녁 19:00** (다음 날 본문 공개). 수집 cron `0 19 * * *` |
| 본문 데이터 | 자체 DB `qtai_db`의 `bible_kr_verses` / `bible_en_verses`에서 셀렉트 |

### 8.2 성경 본문 DB 적재

| 항목 | 내용 |
| --- | --- |
| 한글 본문 출처 | **대한성서공회** PDF (이미 확보) |
| 적재 방식 | PDF → 파싱 → 절(verse) 단위 |
| 영어 본문 | 무료 API 직접 호출 vs PDF 다운로드 → 둘 다 시도 후 채택 (이지윤 추가 조사) |

---

## 9. 날짜·요일 확정 (2026년 실제 요일 기준)

| 날짜 | 요일 | 이벤트 |
| --- | --- | --- |
| 5/8 (금) | 금요일 | W0 킥오프 |
| 5/11 (월) | 월요일 | W0 마지막 날 |
| 5/12 (화) | 화요일 | **개발 착수 (W0 종료 → W1 시작)** |
| 5/15 (금) | 금요일 | W1 첫 주 마감 |
| 5/18 (월) | 월요일 | W1 두 번째 주 시작 |
| 5/22 (금) | 금요일 | **W1 Foundation Lock-in v2 검증 (18:00)** |
| 5/25 (월) | 월요일 | 부처님오신날 (W2 휴무) |
| 5/26 (화) | 화요일 | W2 시작 + **강사 면담(ADR-0016 트리거)** |
| 6/3 (수) | 수요일 | 지방선거 (W3 휴무) |
| 6/8 (월) | 월요일 | W4 시작 — (분기) v2 AI 도메인 분리 OR v1 안정화 |
| 6/17 (수) | 수요일 | **발표일** |

---

## 10. 보류·후속 결정 사항 (2026-05-14 회의 시점)

| 항목 | 상태 | 결정 책임 |
| --- | --- | --- |
| 새번역 라이선스 명시적 확인 | **pending — 확인 전 사용 금지** | 이지윤 |
| AI 자동 검증 메커니즘 상세(입출력·평가지표·합격선) | 미정 → 강상민 단독 정의 → 09_AI §6.4 박제 | 강상민 |
| 시뮬레이터 데이터 모델·저장소·생성 이미지 라이선스 | 미정 → 김태혁 일임 → 22_기능_명세서 FS-12 박제 | 김태혁 |
| ~~PR 검증 스크립트 도구~~ | **확정 (2026-05-14, ADR-0015) — Spring Modulith + ArchUnit** | 강태오 |
| ~~Kafka·K8s 재도입 시점~~ | **확정 (2026-05-14, ADR-0016) — 학습 목표 기반 + W2 강사 면담 → W4 분기** | 강태오 + 강사 면담 |
| 성서 유니온 robots.txt·이용약관 명시적 확인 | 미정 → 수집 가동 전 이지윤 확인 | 이지윤 |
