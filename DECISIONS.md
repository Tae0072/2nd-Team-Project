# DECISIONS.md — QT-AI 단일 기준표

> 이 파일은 분산된 문서들에서 충돌할 수 있는 **포트·TTL·Route·Envelope·DB·인프라·저작권** 값의
> **단일 진실 원천(Single Source of Truth)** 이다.
> 문서 간 값이 다르면 이 파일이 정답. 수정 시 이 파일과 해당 문서를 동시에 PR.

---

## 1. 서비스 포트 (로컬·Prism mock·K8s ClusterIP)

| 서비스 | 로컬 직접 포트 | Prism mock 포트 | K8s ClusterIP 포트 | 내부 DNS |
| --- | --- | --- | --- | --- |
| API Gateway | 8080 | — | 8080 | gateway.qtai.svc.cluster.local:8080 |
| BFF Aggregator | 8083 | 4015 | 8080 | bff-aggregator.qtai.svc.cluster.local:8080 |
| Auth Service | 8081 | 4011 | 8080 | auth-service.qtai.svc.cluster.local:8080 |
| Bible Service | 8082 | 4012 | 8080 | bible-service.qtai.svc.cluster.local:8080 |
| AI Service | 8085 | 4013 | **8080** | ai-service.qtai.svc.cluster.local:8080 |
| Journal Service | 8084 | 4014 | 8080 | journal-service.qtai.svc.cluster.local:8080 |
| MySQL | 3306 | — | 3306 | mysql.qtai.svc.cluster.local:3306 |
| Redis-Cache (Bible) | 6379 | — | 6379 | redis-cache.qtai.svc.cluster.local:6379 |
| Redis-WS (Auth+BFF) | 6380 | — | 6380 | redis-ws.qtai.svc.cluster.local:6380 |
| Kafka | 9092 | — | 9092 | kafka.qtai.svc.cluster.local:9092 |
| Schema Registry | 8086 | — | 8080 | schema-registry.qtai.svc.cluster.local:8080 |
| ChromaDB | 8000 | — | 8000 | chromadb.qtai.svc.cluster.local:8000 |

> **Schema Registry 포트:** 로컬 `8086` (Auth 8081과 충돌 방지). .env.example과 일치시킬 것.

---

## 2. 토큰 정책

| 항목 | 값 | 근거 |
| --- | --- | --- |
| Access Token 유효기간 | **30분 (1800s)** | 03번 § 11.1 |
| Refresh Token 유효기간 | **14일** | 03번 § 11.1 (v1.1에서 7일 단축 검토) |
| Refresh blacklist | Redis-WS `auth:refresh:revoked:{jti}` TTL=만료까지 | 03번 § 11.1 |
| Access blacklist | **없음** (30분 단명) | ADR-0012 단순화 정책 |
| JWT 알고리즘 | RS256 | 03번 § 11.1 |

> ⚠️ `apis/auth/openapi.yaml`의 `expiresIn: 1800` 이 기준. 900(15분)·7일 등 다른 값 발견 시 이 표가 정답.

---

## 3. API Route 확정 (Gateway 라우팅 표 요약)

| 용도 | External Path | 내부 서비스 | 인증 |
| --- | --- | --- | --- |
| 입체 묵상 화면 | `GET /api/v1/passages/{bookCode}/{chapter}/{verse}` | BFF Aggregator | ✅ |
| 대시보드 | `GET /api/v1/me/dashboard` | BFF Aggregator | ✅ |
| 한글 성경 | `GET /bible/kr/{bookCode}/{ch}/{v}` | Bible Service | ✅ |
| 영어 성경 | `GET /bible/en/{bookCode}/{ch}/{v}` | Bible Service | ✅ |
| 주석 | `GET /api/v1/commentary/{bookCode}/{ch}/{v}` | Bible Service | ✅ |
| 성경 목록 | `GET /bible/books` | Bible Service | ✅ |
| AI 세션 시작 | `POST /ai/sessions` | AI Service | ✅ |
| AI 대화 (SSE) | `POST /ai/sessions/{id}/turns` | AI Service | ✅ |
| AI 세션 조회 | `GET /ai/sessions/{id}` | AI Service | ✅ |
| AI 세션 목록 | `GET /ai/sessions` | AI Service | ✅ |
| 묵상 노트 목록 | `GET /api/v1/journals` | Journal Service | ✅ |
| 묵상 노트 단건 | `GET /api/v1/journals/{id}` | Journal Service | ✅ |
| 묵상 노트 수정 | `PATCH /api/v1/journals/{id}` | Journal Service | ✅ |
| 묵상 노트 삭제 | `DELETE /api/v1/journals/{id}` | Journal Service | ✅ |
| 이벤트 로그 | `GET /api/v1/journals/{id}/events` | Journal Service | ✅ |
| 로그아웃 | `POST /auth/logout` | Auth Service | ❌ (갱신만) |
| Google OAuth | `POST /auth/oauth/google` | Auth Service | ❌ |
| WebSocket 알림 | `WS /ws/notifications` | BFF Aggregator | ❌ (STOMP CONNECT 헤더) |

> **AI SSE endpoint:** `/ai/sessions/{id}/turns` (turns가 정식명, messages 아님 — 04번 §6.3 기준)
> **Journal 수동 생성 없음:** `POST /api/v1/journals` 없음. Journal은 `ai.session.completed` Kafka 컨슈머로 자동 DRAFT 생성. 사용자는 수정·발행만.

---

## 4. Kafka 이벤트 Envelope 표준 (events/schema/*.json 기준)

```json
{
  "eventId":         "evt_01HZX...",          // ULID
  "eventType":       "ai.session.completed",  // const 값
  "eventVersion":    1,                        // integer
  "schemaSubject":   "ai.session.completed-value",
  "occurredAt":      "2026-05-26T14:30:00Z",
  "traceId":         "0af7651916cd43dd...",
  "producerService": "ai-service",
  "idempotencyKey":  "ai.session.completed:9012",
  "data":            { ... }                   // payload 아님 — data
}
```

| 토픽 | idempotencyKey 형식 | Producer |
| --- | --- | --- |
| user.deactivated | `user.deactivated:{userId}` | auth-service |
| user.activity.tracked | `read.passage:{userId}:{book}:{ch}:{v}:{epochMinute}` | bff-aggregator |
| ai.session.completed | `ai.session.completed:{sessionId}` | ai-service |
| journal.created | `journal.created:{journalId}` | journal-service |
| journal.updated | `journal.update:{ULID}` | journal-service |
| journal.deleted | `journal.delete:{journalId}:{epochMs}` | journal-service |
| journal.creation.failed | `journal.creation.failed:{sessionId}` | journal-service |
| notification.requested | `{type}:{userId}:{occurredAt}` | 다수 |

---

## 5. DB·인프라 스택 확정

| 항목 | 선택 | 금지 |
| --- | --- | --- |
| RDBMS | **MySQL 8.0** | ~~PostgreSQL~~ |
| Kafka 모드 | **KRaft single-node (v1.0)** | ~~ZooKeeper~~ |
| Schema Registry | **Apicurio Registry 2.5+** | Confluent SR (라이선스) |
| Tracing | **Jaeger + OpenTelemetry** | ~~Tempo~~ |
| Logs | **Loki + Promtail DaemonSet** | |
| Metrics | **Prometheus + Micrometer** | |
| Container Orchestration | **Kubernetes (Minikube) + Helm** | Docker Compose (시연용 폴백만) |
| Secret 관리 | **K8s Secret** | ~~평문 application.yml~~ |

---

## 6. AI Service 스택

| 항목 | 결정 |
| --- | --- |
| 구현 언어/프레임워크 | **Spring Boot 3.3 / Java 21** |
| 포트 | **8085** |
| LLM | Anthropic Claude API (SSE 스트리밍) |
| LLM 클라이언트 | `com.anthropic:anthropic-java` (공식 Java SDK) |
| Vector Store | ChromaDB (Spring `RestClient`로 REST 호출) |
| SSE 스트리밍 | Spring `SseEmitter` |
| Kafka 발행 | Spring Kafka |
| DB | MySQL 8.0 (세션·턴 저장) |

> **변경 이력:** v1.0에서는 Python FastAPI로 결정했으나, 팀의 Java/Spring Boot 숙련도와 5주 일정을 고려해 W0(2026-05-11)에 Spring Boot로 전환. 다른 5개 서비스(gateway, bff, auth, bible, journal)와 동일한 Spring Boot 3.3 / Java 21로 통일.

> BFF(Java)가 `http://ai-service.qtai.svc.cluster.local:8085`로 RestClient 호출.

---

## 7. 에러 응답 표준

| 항목 | 값 |
| --- | --- |
| Content-Type | `application/problem+json` |
| Schema | RFC 7807 ProblemDetail (`type`, `title`, `status`, `code`, `traceId`, `timestamp`) |
| 구버전 패턴 (금지) | `application/json` + `ErrorResponse{code, message, traceId}` |

---

## 8. 성경 데이터 저작권 (법적 리스크)

| 데이터 | 허용 | 사용 조건 |
| --- | --- | --- |
| KJV (영어 성경) | ✅ | Public Domain, 무조건 OK |
| 개역한글 | ⚠️ | 비상업·교육 목적 한정, 출처 표기 필수 |
| Matthew Henry 주석 (영문) | ✅ | Public Domain |
| **개역개정** | ❌ **금지** | 대한성서공회 저작권 — commit 절대 금지 |
| **ESV / NIV** | ❌ **금지** | 라이선스 비용 필요 |
| 한글 주석 / 신학 논문 | ❌ | 더미 데이터로 대체 |

---

## 9. 날짜·요일 확정 (2026년 실제 요일 기준)

| 날짜 | 요일 | 이벤트 |
| --- | --- | --- |
| 5/8 (금) | 금요일 | W0 킥오프 |
| 5/11 (월) | 월요일 | W0 마지막 날 |
| 5/12 (화) | 화요일 | **개발 착수 (W0 종료 → W1 시작)** |
| 5/15 (금) | 금요일 | W1 첫 주 마감 |
| 5/18 (월) | 월요일 | W1 두 번째 주 시작 |
| 5/22 (금) | 금요일 | **W1 Foundation Lock-in 검증 (18:00)** |
| 5/25 (월) | 월요일 | 부처님오신날 대체공휴일 (W2 휴무) |
| 5/26 (화) | 화요일 | W2 시작 |
| 6/3 (수) | 수요일 | 지방선거 (W3 휴무) |
| 6/17 (수) | 수요일 | **발표일** |
