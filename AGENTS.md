# AGENTS.md — QT-AI AI 에이전트 협업 가이드

> **이 파일은 Claude Code / Cursor 등 AI 에이전트가 코드를 생성할 때 반드시 참조해야 하는 컨텍스트 파일이다.**
> 01번 § 9.1·9.3·10.3, 03번 § 16에서 "AI 컨텍스트에 OpenAPI yaml 강제 주입"으로 참조.

## 필수 참조 문서 (코드 생성 전 반드시 로드)

| 우선순위 | 파일 | 목적 |
| --- | --- | --- |
| 🔴 필수 | `DECISIONS.md` | 포트·TTL·스택·저작권 단일 기준 |
| 🔴 필수 | `apis/{service}/openapi.yaml` | 작업 대상 서비스 API 계약 (요청/응답 스키마) |
| 🔴 필수 | `events/schema/{topic}-value.json` | Kafka 이벤트 envelope 및 payload 스키마 |
| 🟡 중요 | `02_ERD_문서.md` | 테이블 구조, 외래키 정책, 인덱스 |
| 🟡 중요 | `03_아키텍처_정의서.md` | 서비스 경계, 통신 패턴, 기술 스택 |
| 🟢 참고 | `docs/adr/` | 기술 결정 근거 |

> **묵상 기록 API 작업 기준:** Journal API는 별도로 사용하지 않는다. 묵상 기록(`/api/v1/journals...`) 계약은 `apis/bible/openapi.yaml`을 기준으로 한다.

## 기술 스택 확정 목록 (환각 방지)

| 영역 | 확정 스택 | 버전 | 주의 |
| --- | --- | --- | --- |
| Java | JDK 21 | 21 LTS | Java 17 코드 생성 금지 |
| Framework | Spring Boot | 3.3.x | 2.x API 사용 금지 (`WebMvcConfigurer` 등 deprecated) |
| Build | Gradle Kotlin DSL | 8.x | `build.gradle` (Groovy) 생성 금지 |
| DB | MySQL | 8.0 | **PostgreSQL 코드 생성 금지** (dialect: `MySQLDialect`) |
| ORM | Spring Data JPA + Hibernate | 6.x | `@SQLRestriction` 사용 (구 `@Where` 금지) |
| Migration | Flyway | 10.x | |
| Messaging | Apache Kafka | KRaft 모드 | **ZooKeeper 코드 생성 금지** |
| Schema Registry | Apicurio Registry | 2.5+ | `apicurio.registry.use-id: contentId` |
| Tracing | Jaeger + OpenTelemetry | Spring Boot 3.3 표준 키 | **Tempo 설정 생성 금지** |
| AI LLM | **DeepSeek API** | OpenAI 호환 | **Anthropic SDK 코드 생성 금지** |
| LLM 클라이언트 | Spring `RestClient` | — | OpenAI 호환 엔드포인트 직접 호출 |
| Vector Store | ChromaDB | — | Spring `RestClient`로 REST 호출 |
| Mobile | Flutter | 3.24+ | Dart null-safety 필수 |

> **모든 백엔드 서비스는 Spring Boot 3.3 / Java 21로 통일.**

## 서비스별 담당자 (코드 생성 범위)

| 서비스 디렉토리 | Owner | 담당 범위 |
| --- | --- | --- |
| `gateway/` | 강태오 | JWT 필터, 라우팅, Rate Limit |
| `bff-aggregator/` | 강태오 | UseCase 패턴, CompletableFuture 병렬 호출 |
| `bible-service/` | 이지윤·이승욱 | 성경 다중 JOIN, Redis 캐시, 묵상일지(journal) 통합 |
| `ai-service/` | 강태오(팀장)·김태혁·강상민 | DeepSeek API, ChromaDB RAG, SSE (SseEmitter) |
| `flutter-app/` | 김지민 | Sliver Sync Scroll, RiverPod, DIO, SSE, 관리자 웹 |

> **Auth Service 제거 (2026-05-12):** 독립 서비스 불필요. JWT 처리는 Gateway 담당.
> **Journal Service 제거 (2026-05-12):** 묵상일지 기능 Bible Service로 통합.
> **Journal API 폐기:** `apis/journal/openapi.yaml` 참조 금지. `/api/v1/journals...`는 Bible Service API로 구현한다.

## AI Service 스택 (Spring Boot 3.3 / Java 21)

> **변경 이력:**
> - v1.0: Python FastAPI 단독 결정
> - W0 (2026-05-11): Spring Boot 3.3 전환
> - W1 (2026-05-12): LLM Anthropic Claude → **DeepSeek** 전환

```
ai-service/
  build.gradle.kts                    # DeepSeek API 호출 (RestClient, 별도 SDK 없음)
  settings.gradle.kts
  src/main/
    java/com/qtai/ai/
      AiServiceApplication.java
      controller/AiSessionController.java       # POST /ai/sessions
                                                # POST /ai/sessions/{id}/turns  ← SSE (SseEmitter)
      service/
        DeepSeekStreamService.java              # DeepSeek API 래퍼 (OpenAI 호환 RestClient 호출)
        ChromaDbClient.java                     # ChromaDB REST 호출 (RestClient)
      kafka/AiSessionCompletedPublisher.java    # ai.session.completed 발행
      prompts/QtPromptTemplates.java            # 큐티 A~D 시스템 프롬프트
    resources/
      application.yml
```

BFF → AI 서비스 호출: `RestClient.get().uri("http://ai-service.qtai.svc.cluster.local:8085/ai/sessions").retrieve()`

### 사용 라이브러리 요점

- **Spring `RestClient`** — DeepSeek OpenAI 호환 엔드포인트 호출 (별도 SDK 없음)
- **Spring `SseEmitter`** — 클라이언트로 SSE 프록시 스트리밍
- **Spring `RestClient`** — ChromaDB REST API 호출
- **Spring Kafka** — `ai.session.completed` 이벤트 발행

## 금지 패턴 (환각 체크리스트 — 01번 § 10.3)

```
❌ @Transactional 없는 DB 변경 메서드
❌ TX 안에서 KafkaTemplate.send() 직접 호출
   → 반드시 @TransactionalEventListener(AFTER_COMMIT) 사용
❌ 평문 비밀번호·API Key를 application.yml/코드에 하드코딩
   → K8s Secret + envFrom: secretKeyRef 만 허용
❌ 서비스 간 직접 JOIN / 직접 @Repository 호출
   → RestClient 또는 Kafka 이벤트로만
❌ JOURNAL_EVENTS 삭제·수정 코드
   → 이벤트 소싱: append-only
❌ Kafka 컨슈머에 idempotency_key 검증 없음
   → DataIntegrityViolationException catch + skip 패턴 필수
❌ 별도 Journal API 또는 apis/journal/openapi.yaml 기준 코드 생성
   → 묵상 기록 API는 apis/bible/openapi.yaml 기준으로 Bible Service에서 구현
❌ Spring Boot 2.x 전용 API (WebMvcConfigurerAdapter, @EnableSwagger2 등)
❌ PostgreSQL dialect, ZooKeeper Kafka 설정, Tempo tracing 설정
❌ Anthropic SDK 코드 (com.anthropic:anthropic-java) — DeepSeek 사용
❌ LLM 공급자 교체 (DeepSeek 고정)
❌ Kafka envelope에 payload 키 사용 (data 사용)
❌ /messages 경로 (AI SSE는 /turns)
❌ 성경 데이터에 개역개정 / ESV / NIV
```

## Kafka 이벤트 Envelope 표준 (events/schema/*.json 참조)

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

> **payload 키 사용 금지** — 표준은 `data`. (events/schema/*.json 모두 `data`로 통일됨)

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

## SSE 이벤트 계약 (AI Service `/turns` 엔드포인트)

| 이벤트 | 의미 |
| --- | --- |
| `turn_started` | 응답 시작 신호 |
| `token` | 스트리밍 토큰 청크 |
| `rag_sources` | RAG 참조 출처 |
| `turn_completed` | 응답 완료 |
| `[DONE]` | SSE 스트림 종료 |

## 토큰 TTL 확정값

| 항목 | 값 | 비고 |
| --- | --- | --- |
| Access Token | 30분 (1800s) | expiresIn: 1800 |
| Refresh Token | 14일 | v1.1에서 7일 검토 |
| Refresh blacklist TTL | refresh 만료까지 | Redis-WS auth:refresh:revoked:{jti} |

## 성경 데이터 저작권 (01번 § 3.1 — 위반 시 법적 리스크)

| 데이터 | 허용 여부 |
| --- | --- |
| KJV (영어) | ✅ Public Domain |
| 개역한글 | ⚠️ 비상업·교육 목적, 출처 표기 필수 |
| Matthew Henry 주석 (영문) | ✅ Public Domain |
| **개역개정** | ❌ **사용 금지** |
| **ESV / NIV** | ❌ **사용 금지** |
| 한글 주석 / 신학 논문 | ❌ 더미 데이터로 대체 |

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
