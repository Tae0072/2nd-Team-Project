# AGENTS.md — QT-AI AI 에이전트 협업 가이드

> **이 파일은 Claude Code / Cursor 등 AI 에이전트가 코드를 생성할 때 반드시 참조해야 하는 컨텍스트 파일이다.**
> 01번 § 9.1·9.3·10.3, 03번 § 16에서 "AI 컨텍스트에 OpenAPI yaml 강제 주입"으로 참조.

## 필수 참조 문서 (코드 생성 전 반드시 로드)

| 우선순위 | 파일 | 목적 |
| --- | --- | --- |
| 🔴 필수 | `DECISIONS.md` | 포트·TTL·스택·저작권·팀 배치 단일 기준 |
| 🔴 필수 | `apis/{ai,bff,bible}/openapi.yaml` | 작업 대상 도메인 API 계약 (요청/응답 스키마) |
| 🟡 중요 | `02_ERD_문서.md` | 단일 DB `qtai_db` 테이블 구조, 도메인별 prefix, 인덱스 |
| 🟡 중요 | `03_아키텍처_정의서.md` | Modular Monolith 구조, 도메인 패키지 경계 |
| 🟢 참고 | `docs/adr/` | 기술 결정 근거 (ADR-0001 모놀리식, ADR-0003 단일 DB, ADR-0013 No RAG, ADR-0014 QT Scrape) |

> **묵상 기록 API 작업 기준:** Journal은 `com.qtai.journal` 도메인 패키지. `apis/bible/openapi.yaml` 안에 묵상 기록 계약이 포함됨.
> **별도 Journal/Auth OpenAPI 사용 금지** (5/12 결정 — `apis/journal`, `apis/auth` 폐기).

## 기술 스택 확정 목록 (환각 방지)

| 영역 | 확정 스택 | 버전 | 주의 |
| --- | --- | --- | --- |
| Java | JDK 21 | 21 LTS | Java 17 코드 생성 금지 |
| Framework | Spring Boot | 3.3.x | 2.x API 사용 금지 (`WebMvcConfigurer` 등 deprecated) |
| Build | Gradle Kotlin DSL | 8.x | `build.gradle` (Groovy) 생성 금지 |
| **배포 단위** | **단일 서비스 `qtai-server`** (Modular Monolith) | — | **별도 서비스 분리 코드 생성 금지** (ADR-0001) |
| DB | MySQL | 8.0 | **PostgreSQL 코드 생성 금지** (dialect: `MySQLDialect`). **단일 DB `qtai_db`** + 도메인별 prefix |
| ORM | Spring Data JPA + Hibernate | 6.x | `@SQLRestriction` 사용 (구 `@Where` 금지) |
| Migration | Flyway | 10.x | 도메인별 하위 디렉토리 (`db/migration/{auth,bible,ai,journal}/`) |
| 도메인 간 통신 | **Spring `ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)`** | — | **v1은 in-process 이벤트, Kafka 코드 생성 금지** |
| ~~Kafka~~ | **v2 분리 시 도입 (보류)** | — | v1 구현 금지 |
| ~~Schema Registry~~ | **v2 분리 시 도입 (보류)** | — | v1 구현 금지 |
| Tracing | Jaeger + OpenTelemetry | Spring Boot 3.3 표준 키 | **Tempo 설정 생성 금지** |
| AI LLM | **DeepSeek API** | OpenAI 호환 | **Anthropic SDK 코드 생성 금지** |
| LLM 클라이언트 | Spring `RestClient` | — | OpenAI 호환 엔드포인트 직접 호출 |
| ~~Vector Store~~ | **사용 안 함** | — | **ChromaDB / 벡터 DB / 엘라스틱서치 코드 생성 금지** (ADR-0013) |
| Full-text Search | MySQL B-tree 인덱스 + 필요 시 FULLTEXT | — | 엘라스틱서치 금지 |
| ~~Container Orchestration~~ | **Docker Compose (v1)** | — | **K8s 매니페스트·Helm 차트 생성 금지** (v2 분리 시 도입) |
| Mobile | Flutter | 3.24+ | Dart null-safety 필수 |

> **모든 백엔드 도메인 패키지는 동일 `qtai-server` 프로세스 안에서 Spring Boot 3.3 / Java 21로 통일.**

## 도메인 패키지별 담당자 (코드 생성 범위)

| 도메인 패키지 | Owner | 담당 범위 |
| --- | --- | --- |
| `com.qtai.gatewayauth` | Bible팀 (이지윤·이승욱·김지민) | JWT 필터, 라우팅, Rate Limit, OAuth |
| `com.qtai.bff` | 강태오 + Bible팀 | UseCase 패턴, 화면별 어그리게이션 |
| `com.qtai.bible` | Bible팀 | 성경 다중 JOIN, Redis 캐시, 본문 설명, 해설 |
| `com.qtai.journal` | Bible팀 (이승욱 주도) | 이벤트 소싱, 익명 나눔, in-process 이벤트 핸들러 |
| `com.qtai.ai` | **강상민 (주도)**, 강태오 | DeepSeek API, SSE (SseEmitter), 해설 생성, 편집자 에이전트 |
| `com.qtai.simulator` | 김태혁 | 본문 장면 시뮬레이터 (스프라이트 기반 검토) |
| `flutter-app/` | Bible팀 (이승욱이 빌드 책임자, 시연 6/17) | Sliver Sync Scroll, RiverPod, DIO, SSE |

> **2026-05-14 팀 재배치 반영:** AI 주도자 강태오→강상민. 김지민·이지윤·이승욱 = Bible팀, Bible 프로토타입→Flutter→인증→관리자 페이지 순서 일괄 진행. 강태오는 단일 파트 고정 X, Lead·DevOps·횡단 지원.
> **Auth Service 제거:** 독립 서비스 불필요. JWT는 `com.qtai.gatewayauth` 패키지에서 처리.
> **Journal Service 제거:** 묵상일지는 `com.qtai.journal` 패키지로 통합.

## AI 도메인 패키지 (Spring Boot 3.3 / Java 21)

> **변경 이력:**
> - v1.0: Python FastAPI 단독 결정
> - W0 (2026-05-11): Spring Boot 3.3 전환
> - W1 (2026-05-12): LLM Anthropic Claude → **DeepSeek** 전환
> - **2026-05-14: ChromaDB·RAG 제외. AI 도메인은 `qtai-server`의 패키지로 통합.**

```
qtai-server/src/main/java/com/qtai/ai/
  AiModuleConfig.java
  controller/AiSessionController.java       # POST /ai/sessions
                                            # POST /ai/sessions/{id}/turns  ← SSE (SseEmitter)
  service/
    DeepSeekStreamService.java              # DeepSeek API 래퍼 (OpenAI 호환 RestClient 호출)
    EditorAgentService.java                 # 편집자 에이전트 (이단성·페르소나 검증)
    ExplanationGenerator.java               # 해설 생성 (Public Domain 비교 데이터 기반)
  event/AiSessionCompletedPublisher.java    # ApplicationEventPublisher 발행 (v1)
                                            # v2 분리 시 Kafka publisher로 교체
  prompts/QtPromptTemplates.java            # 큐티 A~D 시스템 프롬프트
src/main/resources/
  application.yml                           # ai 도메인 설정 spring.profiles.include=ai
```

다른 도메인이 AI 도메인을 호출할 때는 `com.qtai.ai.api.AiSessionFacade` Interface를 통해서만 호출 (ADR-0001 도메인 경계 절대 규칙).

### 사용 라이브러리 요점

- **Spring `RestClient`** — DeepSeek OpenAI 호환 엔드포인트 호출 (별도 SDK 없음)
- **Spring `SseEmitter`** — 클라이언트로 SSE 프록시 스트리밍
- **Spring `ApplicationEventPublisher`** — `ai.session.completed` in-process 이벤트 발행
- ~~ChromaDB~~ — 사용 안 함 (ADR-0013)

### 해설 생성 파이프라인 (강상민 주도)

1. Public Domain 영어 주석(예: Matthew Henry) PDF → MD 변환
2. MD = LLM **비교 데이터로만 활용** (그대로 노출 X)
3. LLM이 본문 + 비교 데이터로 자체 해설 생성
4. **편집자 에이전트가 자동 검증** (이단성·페르소나 일탈 거름)
5. 최종 "해설" 출력 + 출처 표시 (검증 거친 결과물로 인정)

> 메커니즘 상세(입력·출력·평가지표·합격선)는 강상민이 단독 정의 후 09_AI 가이드에 박제.

## 금지 패턴 (환각 체크리스트 — 01번 § 10.3)

```
❌ 다른 도메인 패키지의 클래스(Entity, Service, Repository) 직접 import
   → DTO 변환 + 도메인 Interface 호출만 허용 (ADR-0001)
   → 위반 시 PR 자동 거절 (검증 스크립트, 강태오 작성)

❌ ChromaDB / 벡터 DB / 엘라스틱서치 도입 코드
   → 정확한 좌표 셀렉트는 MySQL B-tree 인덱스로 (ADR-0013)
   → "rag_sources" 필드명도 금지 — sources로 통일

❌ Kafka 코드 생성 (v1 범위)
   → v1 도메인 간 통신은 ApplicationEventPublisher + @TransactionalEventListener(AFTER_COMMIT)
   → KafkaTemplate.send(), @KafkaListener 등 v1에서 생성 금지

❌ K8s 매니페스트 / Helm 차트 생성 (v1 범위)
   → v1 배포는 Docker Compose

❌ @Transactional 없는 DB 변경 메서드
❌ TX 안에서 ApplicationEventPublisher.publishEvent() 동기 핸들러 호출
   → 반드시 @TransactionalEventListener(AFTER_COMMIT) 사용

❌ 평문 비밀번호·API Key를 application.yml/코드에 하드코딩
   → Docker .env + envFrom 또는 OS env (v1)
   → v2에서 K8s Secret 도입

❌ JOURNAL_EVENTS 삭제·수정 코드
   → 이벤트 소싱: append-only (ADR-0004)

❌ in-process 이벤트 핸들러에 idempotency_key 검증 없음
   → journal_inbox_keys UNIQUE 제약 + DuplicateKeyException catch + skip 패턴 필수 (ADR-0007)

❌ 별도 Journal API 또는 apis/journal/openapi.yaml 기준 코드 생성
   → 묵상 기록 API는 apis/bible/openapi.yaml 기준으로 com.qtai.journal에서 구현

❌ 별도 Auth Service 또는 apis/auth/openapi.yaml 기준 독립 서비스 코드 생성
   → JWT는 com.qtai.gatewayauth 패키지에서 처리

❌ Spring Boot 2.x 전용 API (WebMvcConfigurerAdapter, @EnableSwagger2 등)
❌ PostgreSQL dialect, ZooKeeper Kafka 설정, Tempo tracing 설정

❌ Anthropic SDK 코드 (com.anthropic:anthropic-java) — DeepSeek 사용
❌ LLM 공급자 교체 (DeepSeek 고정)
❌ Kafka envelope에 payload 키 사용 (data 사용)
❌ /messages 경로 (AI SSE는 /turns)

❌ 성경 데이터에 개역개정 / ESV / NIV
❌ "주석" 용어 (DB·API·UI 모두 "해설"로 통일 — COMMENTARIES → EXPLANATIONS)
```

## 도메인 이벤트 Envelope (v1 in-process / v2 Kafka 공통)

```json
{
  "eventId":         "evt_01HZX...",   // ULID
  "eventType":       "ai.session.completed",
  "eventVersion":    1,
  "schemaSubject":   "ai.session.completed-value",
  "occurredAt":      "2026-05-26T14:30:00Z",
  "traceId":         "...",
  "producerService": "ai-service",
  "idempotencyKey":  "ai.session.completed:{sessionId}",
  "data":            { ... }
}
```

> **v1:** Spring `ApplicationEventPublisher`로 발행, `@TransactionalEventListener(AFTER_COMMIT)` 핸들러가 수신.
> **v2:** 동일 envelope을 Kafka로 발행. publisher만 교체.
> **payload 키 사용 금지** — 표준은 `data`.

## API 에러 응답 표준 (RFC 7807 ProblemDetail)

```
Content-Type: application/problem+json
{
  "type": "https://api.qtai.app/errors/{slug}",
  "title": "...",
  "status": 4xx or 5xx,
  "code": "DOMAIN_ERROR_CODE",
  "traceId": "...",
  "timestamp": "2026-05-26T14:30:00.123Z"
}
```

> **application/json + ErrorResponse 패턴 생성 금지** — Spectral CI 차단됨.

## SSE 이벤트 계약 (AI 도메인 `/turns` 엔드포인트)

| 이벤트 | 의미 |
| --- | --- |
| `turn_started` | 응답 시작 신호 |
| `token` | 스트리밍 토큰 청크 |
| **`sources`** | **사용된 사전 적재 해설 row 출처 배열** (구 `rag_sources`, 2026-05-14 리네이밍) |
| `turn_completed` | 응답 완료 |
| `[DONE]` | SSE 스트림 종료 |

## 토큰 TTL 확정값

| 항목 | 값 | 비고 |
| --- | --- | --- |
| Access Token | 30분 (1800s) | expiresIn: 1800 |
| Refresh Token | 14일 | v1.1에서 7일 검토 |
| Refresh blacklist TTL | refresh 만료까지 | Redis auth:refresh:revoked:{jti} |

## 성경 데이터 저작권 (01번 § 3.1 — 위반 시 법적 리스크)

| 데이터 | 허용 여부 |
| --- | --- |
| KJV (영어) | ✅ Public Domain |
| 개역한글 | ⚠️ 비상업·교육 목적, 출처 표기 필수 |
| 새번역 | ⚠️ 2026-05-14 회의 결정대로 도입, **라이선스 명시적 확인 후 사용** |
| Matthew Henry 주석 (영문) | ✅ Public Domain. **AI 비교 데이터로만 활용, 그대로 노출 X** |
| **개역개정** | ❌ **사용 금지** |
| **ESV / NIV** | ❌ **사용 금지** |
| 한글 상업 주석 / 신학 논문 | ❌ 사용 금지 |

## QT 본문 소싱 (ADR-0014)

| 항목 | 값 |
| --- | --- |
| 출처 | 성서 유니온 |
| 방식 | 스크래핑 (공식 API 없음) |
| 범위 | 그날 본문 좌표만 |
| 갱신 시간 | 저녁 19:00 |
| Cron | `0 19 * * *` |
| 적재 테이블 | `bible_today_qt_schedule` |

## workspaces 폴더 격리 규칙 (§13)

각 팀원은 `workspaces/{본인명}/` 폴더에서만 읽기·쓰기가 허용됩니다.

| 팀원 | 개인 폴더 |
| --- | --- |
| Lead 강태오 | `workspaces/Lead_강태오/` |
| DevA 이지윤 | `workspaces/DevA_이지윤/` |
| DevB 김태혁 | `workspaces/DevB_김태혁/` |
| DevC 강상민 | `workspaces/DevC_강상민/` |
| DevD 이승욱 | `workspaces/DevD_이승욱/` |
| DevE 김지민 | `workspaces/DevE_김지민/` |

### 필수 규칙

1. **타인 폴더 접근 금지** — 다른 팀원의 개인 폴더는 읽기·수정·삭제 모두 금지. AI 에이전트도 동일.
2. **프로젝트 영향 금지** — `workspaces/` 내부 파일은 빌드·런타임·테스트·CI에 영향 0. import 대상 아님.
3. **워크플로우 → 리포트 워크플로우** — 모든 작업은 `workflows/{date}-{task}.md` 작성 → 자기 검토 → 작업 → `reports/{date}-{task}.md` 작성 순서.
4. **PR 교차 금지** — 다른 팀원 폴더 변경이 PR에 포함되면 자동 reject.
5. **템플릿 공유** — `_template.md`는 수정 금지 (공통 양식). 변경 필요 시 Lead에게 제안.

### 워크플로우/리포트 의무

- 모든 day 카드에 표시된 작업 (실행 가이드 HTML 기준) 시작 전 `workflows/` 작성.
- 작업 종료 직후 `reports/` 작성 — 다음 작업 이전에 반드시.
- 1 워크플로우 = 1 리포트 (동일 이름)

세부 내용: `workspaces/README.md` 참조.
