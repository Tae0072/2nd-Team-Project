# AGENTS.md — QT-AI AI 에이전트 협업 가이드

> **이 파일은 Claude Code / Cursor 등 AI 에이전트가 코드를 생성할 때 반드시 참조해야 하는 컨텍스트 파일이다.**
> 01번 § 9.1·9.3·10.3, 03번 § 16에서 "AI 컨텍스트에 OpenAPI yaml 강제 주입"으로 참조.

## 필수 참조 문서 (코드 생성 전 반드시 로드)

| 우선순위 | 파일 | 목적 |
| --- | --- | --- |
| 🔴 필수 | `apis/{service}/openapi.yaml` | 작업 대상 서비스 API 계약 (요청/응답 스키마) |
| 🔴 필수 | `events/schema/{topic}-value.json` | Kafka 이벤트 envelope 및 payload 스키마 |
| 🟡 중요 | `02_ERD_문서.md` | 테이블 구조, 외래키 정책, 인덱스 |
| 🟡 중요 | `03_아키텍처_정의서.md` | 서비스 경계, 통신 패턴, 기술 스택 |
| 🟢 참고 | `docs/adr/` | 기술 결정 근거 |

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
| Mobile | Flutter | 3.24+ | Dart null-safety 필수 |

## 서비스별 담당자 (코드 생성 범위)

| 서비스 디렉토리 | Owner | 담당 범위 |
| --- | --- | --- |
| `gateway/` | 강태오 | JWT 필터, 라우팅, Rate Limit |
| `bff-aggregator/` | 강태오 | UseCase 패턴, CompletableFuture 병렬 호출 |
| `auth-service/` | 이지윤 | JWT RS256, OAuth JWK 검증, Refresh Rotation |
| `bible-service/` | 김태혁 | 성경 다중 JOIN, Redis 캐시 |
| `ai-service/` | 강상민 | FastAPI (Python), ChromaDB RAG, SSE, 큐티 A~D 프롬프트 |
| `journal-service/` | 이승욱 | 이벤트 소싱, Kafka 컨슈머, @Lock PESSIMISTIC_WRITE |
| `flutter-app/` | 김지민 | Sliver Sync Scroll, RiverPod, DIO, SSE |

## AI Service 스택 확정 (단독 FastAPI — 혼용 금지)

> **ai-service는 Python FastAPI 단독.** Spring Boot WebClient로 호출하는 Java 코드 생성 금지.

```
ai-service/
  main.py           # FastAPI app
  routers/
    session.py      # POST /ai/sessions, POST /ai/sessions/{id}/turns (SSE)
  rag/
    chroma_client.py
    embedder.py
  prompts/
    templates.py    # 큐티 A~D 시스템 프롬프트
  kafka/
    event_publisher.py  # ai.session.completed 발행
```

BFF → AI 서비스 호출: `RestClient.get().uri("http://ai-service.qtai.svc.cluster.local:8085/ai/sessions").retrieve()`

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
❌ Spring Boot 2.x 전용 API (WebMvcConfigurerAdapter, @EnableSwagger2 등)
❌ PostgreSQL dialect, ZooKeeper Kafka 설정, Tempo tracing 설정
❌ AI Service에 Spring Boot 코드 / 반대로 Java 서비스에 FastAPI 코드
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
