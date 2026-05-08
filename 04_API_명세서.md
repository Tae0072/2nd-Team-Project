# 📖 QT-AI (큐티 AI 앱) — API 명세서 v1.2

> **문서 버전:** v1.2
> **작성일:** 2026-05-06 (v1.0) / 2026-05-06 (v1.1) / 2026-05-07 (v1.2 — 외부 검토 9항목 일괄 패치)
> **연관 문서:** [01_프로젝트_계획서 v1.3](./01_프로젝트_계획서.md) / [02_ERD_문서 v1.1.1](./02_ERD_문서.md) / [03_아키텍처_정의서 v1.1](./03_아키텍처_정의서.md)
> **W1 Lock-in 산출물:** 본 문서 + `apis/{service}/openapi.yaml` × 5 (Spectral lint 통과 + Prism mock 가동) — 03번 § 2.2
> **목적:** 6명이 W1 종료 시점에 동일한 API 계약 위에서 병렬로 코드를 작성할 수 있도록 모든 endpoint·DTO·에러·페이로드를 박제. 한 번 동결되면 W2 이후 수정은 ADR 발행 + 영향 범위 PR 일괄 동시 머지로만.

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-06 | 강태오 | 초기 작성 — 5 service OpenAPI 골격 + 공통 표준 (헤더·에러·페이징·CORS·Rate Limit) + Gateway 라우팅 표 + SSE/WebSocket 페이로드 + Spectral 룰 + Prism mock 가동 절차 + 1차 실패 패턴 ↔ API 가드레일 매핑 |
| v1.1 | 2026-05-06 | 강태오 | **3차 검토 36항목 일괄 패치** — 필수 12 (도메인 에러 코드 5개 추가 / `PageResponse<T>` Custom DTO / Rate Limiter Spring Cloud Gateway 내장 / logout 인증 ❌ / DELETE 본문 → POST /me/deactivate / OAuth JWK 직접 검증 / `/passages` 흐름 통일 BFF→Bible 3개 직접 / WS STOMP CONNECT 헤더 / yaml info.contact / Spectral 룰 함수 정정 / servers↔포트 일관 / 503 Custom Mapper) + 일관성 12 (dashboard 5 service 정확화 / activeSession 정책 / Refresh Rotation race / PATCH idempotency_key 자동 / SSE schema / wildcard 의도 / Pod 다중 다이어그램 / SYSTEM 마스킹 schema / SSE 라이브러리 fix / 금지 filter / Spring SSE 표준 / consumer group / events 02번 정합) + 선택 12 (Slack #qtai-api / PASSWORD_TOO_WEAK / SSE close 정책 / epoch_minute 분 경계 / 알림 type 확장 / wss/ws 환경별 / SpringDoc 자동생성 안 씀 / .spectral.yaml 위치 / Mock 검증 도구 / OAS 3.1 의존성 매트릭스 / Hot 100 정의 / Idempotency-Key UX) |
| v1.2 | 2026-05-07 | 강태오 | **외부 검토 9항목 일괄 패치** — § 2.10 Rate Limiter yaml 정정 (login `replenishRate=1, burstCapacity=5` — 분 단위 정확 5/min은 Spring Cloud Gateway 초 단위 한계로 불가, Bucket4j v1.1 검토) / § 3 Gateway 라우팅 표 `/ws/**` 인증 ❌ (BFF가 STOMP CONNECT 검증) / § 5 + § 8.2 `/bible/today` 모순 제거 (BFF 자체 정적 매핑 단일화) / § 6.7 AI 컨슈머 + § 7.8 Journal 발행에 `journal.creation.failed` 추가 (Saga 보상) / § 10.2 STOMP 인증 흐름 강화 (Gateway 패스스루 + BFF 검증 책임 명시) |

---

## 목차

1. [개요 · API 설계 정책](#1-개요--api-설계-정책)
2. [공통 표준 (Cross-cutting Standards)](#2-공통-표준-cross-cutting-standards)
3. [Gateway 라우팅 표](#3-gateway-라우팅-표)
4. [Auth/User Service API](#4-authuser-service-api) — 이지윤
5. [Bible Service API](#5-bible-service-api) — 김태혁
6. [AI/RAG Service API](#6-airag-service-api) — 강상민
7. [Journal Service API](#7-journal-service-api) — 이승욱
8. [BFF Aggregator API](#8-bff-aggregator-api) — 강태오
9. [SSE (Server-Sent Events) 표준](#9-sse-server-sent-events-표준)
10. [WebSocket (STOMP) 표준](#10-websocket-stomp-표준)
11. [OpenAPI 3.1 yaml 디렉토리 + Spectral 룰](#11-openapi-31-yaml-디렉토리--spectral-룰)
12. [Mock 서버 (Prism) 가동 절차](#12-mock-서버-prism-가동-절차)
13. [1차(HMS) 실패 패턴 ↔ API 가드레일](#13-1차hms-실패-패턴--api-가드레일)
14. [작성 체크리스트 + W1 Lock-in 검증](#14-작성-체크리스트--w1-lock-in-검증)

---

## 1. 개요 · API 설계 정책

### 1.1 API 스타일

| 항목 | 표준 |
| --- | --- |
| **스타일** | RESTful (HTTP/1.1) — gRPC는 v2.0 검토 |
| **포맷** | JSON (UTF-8). `Content-Type: application/json; charset=utf-8` |
| **명세 표준** | **OpenAPI 3.1** — `apis/{service}/openapi.yaml` |
| **lint** | Spectral (`@stoplight/spectral-cli`) — PR 머지 게이트 (03번 § 10.3) |
| **Mock 서버** | Prism v5+ — Flutter 작업 unblock 용 (03번 § 2.2) |
| **Spec-First** | OpenAPI yaml **수동 작성** — SpringDoc 같은 코드→yaml 자동 생성 사용 안 함 (코드 변경 시 yaml과 어긋날 위험) |

> **OAS 3.1 의존성 호환성 매트릭스 (v1.1):**
> - Spectral CLI: 6.x+ (3.1 완전 지원) ✅
> - Prism CLI: **5.x+ 필수** (v4 이하 3.1 미지원)
> - Swagger UI: **5.x+ 필수** (v3 3.1 미지원, v1.0 SwaggerUI 사용 안 함)
> - Spring Boot 3.x: yaml 수동 작성 — SpringDoc 자동 생성 미사용

### 1.2 URL 구조

```
                    공개 노출 (Flutter → Gateway)
https://api.qtai.app/api/v1/{도메인}/...
                  │       │
                  │       └─ 메이저 버전 (v1, v2). breaking change 시 v2로 분기
                  └─ /api prefix (정적 자원과 분리)

                    내부 (서비스 간, K8s DNS)
http://{service}.qtai.svc.cluster.local:8080/api/v1/{도메인}/...
```

**도메인 별 prefix:**
| Service | Prefix | 호출 경로 |
| --- | --- | --- |
| Auth | `/auth/...` | Gateway → Auth Service |
| Bible | `/bible/...` | Gateway → Bible Service (직접) 또는 BFF → Bible |
| AI | `/ai/...` | Gateway → AI Service |
| Journal | `/api/v1/journals/...` | Gateway → Journal Service |
| BFF (Aggregate) | `/api/v1/me/...`, `/api/v1/passages/...` | Gateway → BFF Aggregator |
| WebSocket | `/ws/...` | Gateway → BFF Aggregator (STOMP) |

> **`/passages` 충돌 정리 (v1.1):**
> - **공개 `GET /api/v1/passages/{bookCode}/{chapter}/{verse}` (Gateway → BFF)** — KR + EN + Commentary 어그리게이션 + `user.activity.tracked` Kafka 발행
> - BFF는 **Bible Service의 단일 엔드포인트 3개(kr/en/commentary)를 병렬 직접 호출** (03번 § 5.2 BFF UseCase 코드와 정합). 한 번에 다 받는 사설 통합 엔드포인트는 v1.0에 두지 않음 — 단일 책임 원칙 + 캐시 단위가 단일 endpoint 단위로 명확
> - Gateway 라우트 path matcher는 `/api/v1/passages/{bookCode}/{chapter}/{verse}` (정확 패턴, wildcard 미사용)

### 1.3 API 버전 관리

| 변경 종류 | 정책 |
| --- | --- |
| **Backward-compatible 추가** (새 필드, 새 endpoint) | v1 유지. OpenAPI minor bump (1.0.0 → 1.1.0) |
| **Breaking change** (필드 제거·타입 변경·필수화) | **v2 분기**. v1은 N개월(시연용은 시연일까지) 동시 운영 |
| **Deprecate** | OpenAPI `deprecated: true` + 응답 헤더 `Deprecation: true` + `Sunset: <date>` |

> **v1.0 시연 한정:** 6/17 시연일까지 v1만. v2 분기는 W4 이후 검토.

### 1.4 Service Owner 책임

| 사항 | 책임자 |
| --- | --- |
| `apis/{service}/openapi.yaml` 작성·갱신 | 해당 service owner |
| Spectral lint 통과 | 해당 service owner |
| Mock 서버 가동 시 응답 예시 작성 | 해당 service owner |
| 변경 시 다른 service owner에게 통보 | 본인 (Slack 채널) |
| Breaking change 시 ADR 발행 | 본인 + 강태오 + 영향 받는 owner |

> **Slack 채널 (W0 5/13까지 강태오가 생성):**
> - `#qtai-api` — API 변경·계약 논의 (필수)
> - `#qtai-deploy` — 배포·CI/CD 알림
> - `#qtai-incident` — 장애 대응

---

## 2. 공통 표준 (Cross-cutting Standards)

### 2.1 인증 헤더

| 헤더 | 값 | 적용 |
| --- | --- | --- |
| `Authorization` | `Bearer {access_token}` | 보호된 엔드포인트 모두 |
| `X-User-Id` | `{user_id}` | **내부 전용**. Gateway가 JWT 검증 후 주입. 외부 클라이언트가 보내면 Gateway가 strip. NetworkPolicy로 외부 spoofing 차단 (03번 § 9.4) |

**인증이 필요 없는 엔드포인트** (`security: []`):
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout` ⭐ **v1.1 변경** — refresh token만 검증, access 만료 후에도 logout 가능
- `POST /auth/oauth/google`
- `GET /actuator/health/*` (관측성)

### 2.2 분산 트레이싱 헤더

| 헤더 | 값 | 의미 |
| --- | --- | --- |
| `traceparent` | W3C Trace Context (예: `00-0af7651916cd43dd8448eb211c80319c-b9c7c989f97918e1-01`) | Gateway가 발급 (없으면 생성, 있으면 전파) |
| `tracestate` | vendor 확장 (선택) | 사용 안 함 v1.0 |
| `X-Request-Id` | ULID | Gateway가 발급. 로그·에러 응답에 포함 |

> 모든 Service가 위 헤더를 **서비스 간 호출 시 그대로 전파**. Spring Boot는 `RestClient` + Micrometer 자동 propagation. Kafka 이벤트는 페이로드 `traceId` 필드로 (03번 § 8.2).

### 2.3 표준 응답 envelope

> **결정:** **Envelope 사용 안 함**. 응답 본문은 자원 그 자체 (또는 collection이면 `{ "items": [...], "page": {...} }`).
>
> **이유:** 1차(HMS)에서 `{ "success": true, "data": {...} }` 같은 envelope 사용 → HTTP status code와 중복. RESTful 원칙 위배.

**성공 응답 예 (자원 그 자체):**
```json
HTTP/1.1 200 OK
Content-Type: application/json
{
  "id": 5678,
  "email": "user@example.com",
  "nickname": "홍길동"
}
```

**collection 응답 예 (페이지네이션):**
```json
HTTP/1.1 200 OK
{
  "items": [ ... ],
  "page": {
    "number": 0,
    "size": 20,
    "totalElements": 156,
    "totalPages": 8
  }
}
```

### 2.4 표준 에러 모델 — RFC 7807 Problem Details

> **표준:** Spring Boot 3.x ProblemDetail (`application/problem+json`) + 도메인 확장 필드.

```json
HTTP/1.1 404 Not Found
Content-Type: application/problem+json
{
  "type": "https://api.qtai.app/errors/journal-not-found",
  "title": "Journal not found",
  "status": 404,
  "detail": "Journal id=12345 does not exist or has been deleted",
  "instance": "/api/v1/journals/12345",
  "code": "JOURNAL_NOT_FOUND",
  "traceId": "0af7651916cd43dd8448eb211c80319c",
  "timestamp": "2026-05-26T14:30:00.123Z",
  "errors": []
}
```

**필수 확장 필드** (Spring `ProblemDetail.setProperty()`로 주입):
- `code`: 도메인 에러 코드 (예: `JOURNAL_NOT_FOUND`, `EMAIL_ALREADY_EXISTS`)
- `traceId`: 분산 트레이싱 ID — 사용자가 문의 시 추적 키
- `timestamp`: ISO 8601 UTC

**검증 오류 (400):**
```json
HTTP/1.1 400 Bad Request
{
  "type": "https://api.qtai.app/errors/validation-failed",
  "title": "Validation failed",
  "status": 400,
  "code": "VALIDATION_FAILED",
  "traceId": "...",
  "timestamp": "...",
  "errors": [
    { "field": "email",    "code": "INVALID_FORMAT", "message": "Invalid email format" },
    { "field": "password", "code": "TOO_SHORT",      "message": "Min 8 characters" }
  ]
}
```

### 2.5 HTTP Status Code 표준

| Code | 사용 |
| --- | --- |
| 200 OK | 일반 GET, PATCH, POST 응답 본문 있음 |
| 201 Created | POST 자원 생성 (Location 헤더 포함) |
| 204 No Content | DELETE 성공 또는 응답 본문 없음 |
| 400 Bad Request | 검증 실패, 잘못된 요청 |
| 401 Unauthorized | JWT 누락·만료·서명 오류 |
| 403 Forbidden | 권한 부족 (다른 사용자의 자원 접근 등) |
| 404 Not Found | 자원 없음 |
| 409 Conflict | UNIQUE 충돌 (이메일 중복 등), 상태 충돌 |
| 410 Gone | soft-deleted 자원 명시적 표시 (선택) |
| 422 Unprocessable Entity | 비즈니스 규칙 위반 (검증은 통과) |
| 429 Too Many Requests | Rate limit 초과 (`Retry-After` 헤더 포함) |
| 500 Internal Server Error | 예상치 못한 서버 오류 |
| 502 Bad Gateway | 업스트림 service 응답 비정상 |
| 503 Service Unavailable | Circuit Breaker OPEN, graceful shutdown 중 |
| 504 Gateway Timeout | 업스트림 service 타임아웃 |

> **금지:** 200 OK + 본문 안에 `"success": false` 같은 패턴. HTTP code로만 성공/실패 표현.

> **503 매핑 책임 (v1.1 명시):** Resilience4j의 `CallNotPermittedException`과 graceful shutdown 중 `ShuttingDownException`은 **Spring Boot가 자동으로 503에 매핑하지 않음**. 각 service가 `@ControllerAdvice`로 명시적 매핑 필요:
> ```java
> @ExceptionHandler(CallNotPermittedException.class)
> public ProblemDetail circuitBreakerOpen(CallNotPermittedException e) {
>     ProblemDetail pd = ProblemDetail.forStatus(503);
>     pd.setProperty("code", "UPSTREAM_UNAVAILABLE");
>     pd.setProperty("traceId", MDC.get("traceId"));
>     return pd;
> }
> ```

### 2.6 도메인 에러 코드 표 (v1.1 — 본문에서 사용된 모든 코드 망라)

| 도메인 | 코드 | HTTP | 의미 |
| --- | --- | --- | --- |
| Common | `VALIDATION_FAILED` | 400 | 요청 검증 실패 |
| Common | `UNAUTHORIZED` | 401 | JWT 누락·만료 |
| Common | `FORBIDDEN` | 403 | 권한 부족 |
| Common | `RATE_LIMITED` | 429 | Rate limit 초과 |
| Common | `INTERNAL_ERROR` | 500 | 알 수 없는 오류 |
| Common | `UPSTREAM_UNAVAILABLE` | 503 | Circuit Breaker OPEN |
| Auth | `EMAIL_ALREADY_EXISTS` | 409 | 회원가입 시 이메일 중복 |
| Auth | `INVALID_CREDENTIALS` | 401 | 로그인 실패 |
| Auth | `PASSWORD_TOO_WEAK` ⭐ | 400 | 비밀번호 정책 미달 (영문+숫자+특수문자) |
| Auth | `ACCOUNT_DEACTIVATED` ⭐ | 401 | 탈퇴된 계정 (`status='DEACTIVATED'`) |
| Auth | `REFRESH_TOKEN_EXPIRED` | 401 | refresh token 만료 |
| Auth | `REFRESH_TOKEN_REVOKED` | 401 | Redis blacklist 차단 |
| Auth | `REFRESH_TOKEN_INVALID` ⭐ | 401 | 서명·구조 오류, 또는 DB 미존재 |
| Auth | `OAUTH_TOKEN_INVALID` ⭐ | 401 | Google ID Token JWK 검증 실패 |
| Auth | `OAUTH_PROVIDER_ERROR` | 502 | Google JWKS 서버 5xx |
| Bible | `PASSAGE_NOT_FOUND` | 404 | 좌표가 잘못됨 (예: 창세기 100장) |
| Bible | `BOOK_CODE_INVALID` | 400 | 책 코드 잘못됨 |
| AI | `SESSION_NOT_FOUND` | 404 | AI 세션 없음 |
| AI | `SESSION_NOT_OWNED` | 403 | 본인 세션 아님 |
| AI | `SESSION_ALREADY_COMPLETED` ⭐ | 422 | 이미 D 단계 완료된 세션에 turn 추가 시도 |
| AI | `LLM_PROVIDER_ERROR` | 502 | Anthropic API 5xx |
| AI | `LLM_TIMEOUT` | 504 | 첫 토큰 timeout |
| AI | `PROMPT_TEMPLATE_NOT_ACTIVE` | 422 | 검수 안 된 프롬프트 |
| Journal | `JOURNAL_NOT_FOUND` | 404 | journal 없음 |
| Journal | `JOURNAL_NOT_OWNED` | 403 | 본인 journal 아님 |
| Journal | `JOURNAL_LOCKED` | 409 | 동시 수정 충돌 (`@Lock(PESSIMISTIC_WRITE)`) |
| Journal | `INVALID_STATUS_TRANSITION` ⭐ | 422 | 예: PUBLISHED → DRAFT 금지 |
| Journal | `INVALID_EVENT_SEQUENCE` | 422 | sequence UNIQUE 위반 |

> ⭐ = v1.1에 추가된 코드 (v1.0 누락분)

### 2.7 페이지네이션 표준 — Custom `PageResponse<T>`

> **v1.1 정정:** Spring Data `Page<T>` 기본 직렬화는 `content` 필드 + 평면 `pageable` 등 — 04번이 정의한 `{ items, page: {...} }` 구조와 **다름**. **Custom DTO 필수**.

**쿼리 파라미터:**
| 이름 | 기본값 | 의미 |
| --- | --- | --- |
| `page` | 0 | 페이지 번호 (0-based) |
| `size` | 20 | 페이지 크기 (max 100) |
| `sort` | `createdAt,desc` | 정렬 (`field,asc`/`desc`, 다중 가능) |

**Custom DTO (전 service 공통, BaseEntity와 같은 단계로 소스 복사 — 03번 § 5):**

```java
// common/PageResponse.java
public record PageResponse<T>(
    List<T> items,
    PageMeta page
) {
    public record PageMeta(
        int number,
        int size,
        long totalElements,
        int totalPages
    ) {}

    public static <T> PageResponse<T> of(Page<T> page) {
        return new PageResponse<>(
            page.getContent(),
            new PageMeta(page.getNumber(), page.getSize(),
                         page.getTotalElements(), page.getTotalPages())
        );
    }
}
```

**Controller 사용:**
```java
@GetMapping("/journals")
public PageResponse<JournalSummary> list(@PageableDefault Pageable pageable, ...) {
    Page<JournalSummary> page = journalService.findAll(pageable);
    return PageResponse.of(page);
}
```

**응답 구조:**
```json
{
  "items": [ ... ],
  "page": {
    "number": 0,
    "size": 20,
    "totalElements": 156,
    "totalPages": 8
  }
}
```

### 2.8 필터링·정렬 쿼리 표준

| 패턴 | 형식 | 예 |
| --- | --- | --- |
| 단순 일치 | `?status=PUBLISHED` | journal status |
| 다중 값 | `?status=DRAFT&status=PUBLISHED` | 여러 status |
| 범위 | `?createdAtFrom=2026-05-01&createdAtTo=2026-05-31` | 기간 |
| 검색 | `?q=묵상` | full-text (v1.1) |
| 정렬 | `?sort=createdAt,desc&sort=id,asc` | 다중 정렬 |

> **금지:** GraphQL 스타일 필드 선택 (`?fields=id,title`)은 v1.0에 없음. 필요 시 v1.1 ADR.

### 2.9 CORS 정책 (Gateway)

| 항목 | 값 |
| --- | --- |
| `Access-Control-Allow-Origin` | v1.0: `*` (시연·개발). v1.1: 정확한 origin 지정 |
| `Access-Control-Allow-Methods` | `GET, POST, PATCH, DELETE, OPTIONS` |
| `Access-Control-Allow-Headers` | `Authorization, Content-Type, X-Request-Id, traceparent` |
| `Access-Control-Allow-Credentials` | `false` (쿠키 안 씀, JWT만) |
| `Access-Control-Max-Age` | `3600` |

### 2.10 Rate Limiting 정책 (Gateway) — v1.1 정확화

| 대상 | 제한 | 식별자 |
| --- | --- | --- |
| 비로그인 (anonymous) | 60 req/min | client IP |
| ROLE_USER 일반 endpoint | 600 req/min | user_id |
| AI Service `/ai/sessions/*` | 60 req/min, 동시 SSE 3개 | user_id |
| Auth `/auth/login` | 5 req/min | client IP (brute-force 방지) |
| Auth `/auth/register` | 3 req/min | client IP |

**구현 (v1.1 정확화 → v1.2 yaml 정정):** **Spring Cloud Gateway 내장 `RedisRateLimiter`** (Lua 스크립트 기반 토큰 버킷). Bucket4j는 별도 라이브러리이며 v1.0에는 사용하지 않음.

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: auth-login
          predicates: [Path=/auth/login, Method=POST]
          filters:
            - name: RequestRateLimiter
              args:
                # ⭐ v1.2 정정 — login 5/min 정확 구현은 Spring Cloud Gateway RedisRateLimiter(초 단위)로 불가능.
                # v1.0 절충: replenishRate=1 (초당 1 토큰), burstCapacity=5 (최초 5회 burst).
                # 결과: 5초 동안 5회 발사 가능 → 이후 1초당 1회. brute-force 충분 방지 (5초당 5회 ≪ 분당 60회).
                # 분 단위 정확 5/min: Bucket4j (초·분·시간 유연) 또는 Custom Lua script. v1.1 검토.
                redis-rate-limiter.replenishRate: 1
                redis-rate-limiter.burstCapacity: 5
                key-resolver: "#{@ipAddressKeyResolver}"
```

초과 시 `429 Too Many Requests` + `Retry-After: <seconds>` 헤더 + ProblemDetail.

### 2.11 멱등성 (Idempotency)

| 메서드 | 멱등 |
| --- | --- |
| GET, HEAD, PUT, DELETE | 자동 멱등 (HTTP 표준) |
| POST | 기본 비멱등. `Idempotency-Key` 헤더 (v1.1 검토) |

> **v1.0 멱등성 적용 범위:** Kafka 컨슈머만 (DB UNIQUE — ADR-0007). HTTP는 자연 멱등 메서드만 신뢰.
>
> **UX 영향 (v1.1 명시):** 사용자가 PATCH 버튼을 동시에 N번 누르면 N번의 `journal.update:{ulid}` 이벤트가 적재됨 (각각 다른 idempotency_key). `@Lock(PESSIMISTIC_WRITE)`로 직렬화는 되지만 N개 events 생성. UX 측면에서는 클라이언트(Flutter)가 button debounce(300ms) + loading state로 1차 방어. v1.1에 `Idempotency-Key` 헤더 도입 검토.

### 2.12 시간·로케일

| 항목 | 표준 |
| --- | --- |
| 시간 | **UTC ISO 8601** (예: `2026-05-26T14:30:00.123Z`). 클라이언트가 timezone 변환 |
| Locale | `Accept-Language: ko-KR` (default), `en-US` 지원 (v1.1) |
| Timezone 헤더 | 사용 안 함 v1.0 |

---

## 3. Gateway 라우팅 표

> Spring Cloud Gateway `application.yml`의 `spring.cloud.gateway.routes` 정의. 이 표가 정답 — yml은 본 표대로 생성.

| Route ID | Path | Method | Target Service | 인증 | 비고 |
| --- | --- | --- | --- | --- | --- |
| auth-public | `/auth/register` | POST | auth-service | ❌ | Rate 3/min |
| auth-public | `/auth/login` | POST | auth-service | ❌ | Rate 5/min |
| auth-public | `/auth/refresh` | POST | auth-service | ❌ | |
| auth-public | `/auth/logout` | POST | auth-service | ❌ ⭐ | refresh token만 검증 (v1.1 변경) |
| auth-public | `/auth/oauth/google` | POST | auth-service | ❌ | |
| auth-private | `/auth/me` | GET | auth-service | ✅ | |
| auth-private | `/auth/me/deactivate` ⭐ | POST | auth-service | ✅ | v1.1 변경 — DELETE body 대신 POST |
| bible | `/bible/**` | GET | bible-service | ✅ | 직접 호출 (단일 자원) |
| bible-aggregate | `/api/v1/passages/{book}/{ch}/{v}` ⭐ | GET | **bff-aggregator** | ✅ | v1.1 — wildcard 제거, 정확 패턴 |
| commentary | `/api/v1/commentary/**` | GET | bible-service | ✅ | 직접 호출 |
| ai | `/ai/sessions` | POST | ai-service | ✅ | |
| ai-sse | `/ai/sessions/*/turns` | POST | ai-service | ✅ | **SSE 패스스루** |
| ai | `/ai/sessions/*` | GET | ai-service | ✅ | |
| ai-list | `/ai/sessions` | GET | ai-service | ✅ | |
| journal | `/api/v1/journals/**` | GET, PATCH, DELETE | journal-service | ✅ | |
| me | `/api/v1/me/**` | GET | bff-aggregator | ✅ | 대시보드 |
| ws | `/ws/**` | WebSocket | bff-aggregator | ❌ ⭐ | v1.2 — Gateway 단순 패스스루 (HTTP handshake에는 JWT 헤더 없음). BFF가 STOMP CONNECT 프레임 헤더 검증 (§ 10.2) |
| health | `/actuator/health` | GET | gateway 자체 | ❌ | |

⭐ = v1.1 변경

**Gateway 필터 체인:**
```
[전역 Pre 필터]
  1. TraceId 발급/전파 (W3C)
  2. X-User-Id strip (외부에서 들어오면 제거)
  3. JWT 검증 (RS256, 공개키 K8s Secret)
  4. JWT → X-User-Id 헤더 주입 (내부용)
  5. Rate Limit (Redis 내장 RateLimiter, Lua)

[라우팅]

[전역 Post 필터]
  1. 응답 시간 메트릭
  2. 에러 매핑 (업스트림 5xx → ProblemDetail)
```

---

## 4. Auth/User Service API

> **Owner:** 이지윤 / **Base URL:** `http://auth-service.qtai.svc.cluster.local:8080` / **Public:** `https://api.qtai.app/auth/...`
>
> **OpenAPI 파일:** `apis/auth/openapi.yaml`

### 4.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 4.2 | POST | `/auth/register` | ❌ | 회원가입 |
| 4.3 | POST | `/auth/login` | ❌ | 로그인 |
| 4.4 | POST | `/auth/refresh` | ❌ | 토큰 갱신 (Token Rotation, Distributed Lock) |
| 4.5 | POST | `/auth/logout` | ❌ ⭐ | 로그아웃 (refresh token만 검증) |
| 4.6 | GET | `/auth/me` | ✅ | 내 정보 조회 |
| 4.7 | POST | `/auth/me/deactivate` ⭐ | ✅ | 회원 탈퇴 (v1.1 — DELETE body 대신) |
| 4.8 | POST | `/auth/oauth/google` | ❌ | Google OAuth 로그인 (JWK 직접 검증) |

### 4.2 POST /auth/register

**Request:**
```http
POST /auth/register
Content-Type: application/json

{
  "email":    "user@example.com",
  "password": "P@ssw0rd123",
  "nickname": "홍길동"
}
```

**Validation:**
- `email`: RFC 5321, max 254
- `password`: min 8, max 72 (bcrypt 한계), 영문 + 숫자 + 특수문자 1개 이상 (위반 시 `PASSWORD_TOO_WEAK`)
- `nickname`: min 2, max 50

**Response 201 Created:**
```http
HTTP/1.1 201 Created
Location: /auth/me
Content-Type: application/json

{
  "id":       5678,
  "email":    "user@example.com",
  "nickname": "홍길동",
  "createdAt": "2026-05-12T03:21:11.456Z"
}
```

**Errors:**
- 400 `VALIDATION_FAILED` — 입력 검증 실패 (이메일 형식 등)
- 400 `PASSWORD_TOO_WEAK` — 비밀번호 정책 미달
- 409 `EMAIL_ALREADY_EXISTS` — 활성(`status='ACTIVE'`) 사용자 중 동일 이메일 존재 (탈퇴된 사용자는 마스킹되어 충돌 안 남 — 02번 § 2.2.1)
- 429 `RATE_LIMITED` — 3회/분 초과

### 4.3 POST /auth/login

**Request:**
```http
POST /auth/login
Content-Type: application/json

{
  "email":    "user@example.com",
  "password": "P@ssw0rd123"
}
```

**Response 200 OK:**
```json
{
  "accessToken":  "eyJhbGciOiJSUzI1NiIs...",
  "refreshToken": "eyJhbGciOiJSUzI1NiIs...",
  "tokenType":    "Bearer",
  "expiresIn":    1800,
  "user": {
    "id":       5678,
    "email":    "user@example.com",
    "nickname": "홍길동"
  }
}
```

**Errors:**
- 401 `INVALID_CREDENTIALS` — 이메일/비밀번호 불일치 (구체적 사유 노출 X)
- 401 `ACCOUNT_DEACTIVATED` — `status='DEACTIVATED'`
- 429 `RATE_LIMITED` — 5회/분 초과

### 4.4 POST /auth/refresh — Token Rotation + race condition 방지

**Request:**
```json
{
  "refreshToken": "eyJhbGciOiJSUzI1NiIs..."
}
```

**Response 200 OK (Token Rotation):**
```json
{
  "accessToken":  "eyJ... (new)",
  "refreshToken": "eyJ... (new, 기존은 Redis blacklist 추가)",
  "tokenType":    "Bearer",
  "expiresIn":    1800
}
```

**처리 시퀀스 (v1.1 — race condition 방지):**
1. JWT 서명·만료 검증 → 실패 시 401 `REFRESH_TOKEN_EXPIRED` / `REFRESH_TOKEN_INVALID`
2. **Redis Distributed Lock** 획득 — `auth:refresh:rotating:{jti}` (NX, TTL 5s). 이미 잠겨 있으면 200ms 대기 후 재시도 1회 → 그래도 실패 시 409 (다른 요청이 처리 중이니 잠시 후 재시도)
3. `token_hash` DB 조회 → 존재·활성 확인
4. **Redis-WS** `auth:refresh:revoked:{jti}` 조회 → 있으면 401 `REFRESH_TOKEN_REVOKED`
5. Token Rotation: 기존 토큰 `revoked_at` UPDATE + Redis blacklist 추가 (TTL = refresh 만료까지)
6. 새 Access + Refresh 발급
7. Lock 해제

> **race condition 시나리오:** 모바일 네트워크에서 같은 refresh token 2회 동시 발사 — Lock 없이는 한 번 rotation 후 두 번째 요청이 blacklist에 차단되어 401 → 사용자 강제 로그아웃. Distributed Lock으로 직렬화하여 첫 번째만 처리, 두 번째는 같은 결과 반환 또는 짧은 재시도.

**Errors:**
- 401 `REFRESH_TOKEN_EXPIRED`
- 401 `REFRESH_TOKEN_REVOKED` — Redis blacklist
- 401 `REFRESH_TOKEN_INVALID` — 서명·구조 오류 또는 DB 미존재
- 409 `RACE_CONDITION_DETECTED` — Lock 획득 실패 (재시도 권장)

### 4.5 POST /auth/logout — v1.1 인증 ❌

**Request:**
```http
POST /auth/logout
Content-Type: application/json

{
  "refreshToken": "eyJ..."
}
```

> **v1.1 변경:** `Authorization` 헤더 불필요. **refresh token만 검증**. Access token이 만료된 사용자도 로그아웃 가능 (refresh token으로 본인 확인 충분).

**Response 204 No Content**

**처리:**
- Refresh Token 서명·만료 검증 (만료된 것도 검증만 통과하면 OK — DB에 있어야 함)
- 만료되지 않은 Refresh: DB `revoked_at` UPDATE + Redis-WS `auth:refresh:revoked:{jti}` 등록
- Access Token: 만료(30분)까지 그대로 유효 — blacklist 없음 (단명이라 위험 낮음)
- 멱등성: 이미 revoke된 토큰을 다시 logout 시 204 그대로 응답 (no-op)

**Errors:**
- 401 `REFRESH_TOKEN_INVALID` — 서명 오류 또는 DB 미존재 (스푸핑 차단)
- 만료된 토큰은 **에러 아님** (이미 만료되어 무효화된 상태로 간주)

### 4.6 GET /auth/me

**Response 200 OK:**
```json
{
  "id":         5678,
  "email":      "user@example.com",
  "nickname":   "홍길동",
  "role":       "ROLE_USER",
  "status":     "ACTIVE",
  "createdAt":  "2026-05-12T03:21:11.456Z",
  "updatedAt":  "2026-05-26T08:14:33.001Z",
  "oauthLinks": [
    { "provider": "GOOGLE", "linkedAt": "2026-05-15T10:00:00Z" }
  ]
}
```

### 4.7 POST /auth/me/deactivate — 회원 탈퇴 (v1.1 변경)

> **v1.1 변경:** `DELETE /me { password }`는 RFC 7231 비표준 (DELETE body 일부 환경에서 strip). **`POST /me/deactivate { password }`로 변경**.

**Request:**
```http
POST /auth/me/deactivate
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "password": "P@ssw0rd123"     // 비밀번호 재확인 (소셜 전용은 confirmText 대체)
}
```

**Response 204 No Content**

**처리 시퀀스 (TX 안):**
1. bcrypt 검증 (소셜 전용 사용자는 `confirmText: "탈퇴"` 일치 검증)
2. `USERS.status = 'DEACTIVATED'`
3. `USERS.deleted_at = NOW()`
4. `USERS.email = 'u_{id}_deactivated_{epoch_ms}@deleted.local'` (마스킹 — 02번 § 2.2.1)
5. `REFRESH_TOKENS` 모두 `revoked_at` UPDATE
6. **AFTER_COMMIT** → Kafka publish `user.deactivated` (멱등성 키: `user.deactivated:{user_id}`)
7. AI Service 컨슈머 → 활성 세션 정리
8. Journal Service 컨슈머 → 데이터 처리 정책에 따라 (v1.0은 보존, v1.1 GDPR 검토)

### 4.8 POST /auth/oauth/google — JWK 직접 검증 (v1.1)

**Request:**
```json
{
  "idToken": "eyJ... (Google ID Token)"
}
```

**처리 (v1.1 정정):**
1. Google JWKS endpoint 캐시 조회 (`https://www.googleapis.com/oauth2/v3/certs`, 1시간 cache)
2. **ID Token JWT 직접 검증** (nimbus-jose-jwt) — 서명·iss(`accounts.google.com` 또는 `https://accounts.google.com`)·aud(우리 client_id)·exp 모두 검증
3. claim에서 `sub` (Google 사용자 ID), `email`, `email_verified`, `name` 추출
4. `OAUTH_LINKS`에서 (provider='GOOGLE', provider_user_id=sub) 조회
5. 매치되면 → 로그인. 없으면 → 새 USERS 생성 + OAUTH_LINKS 추가

> **v1.1 변경 이유:** Google `tokeninfo` endpoint는 추가 네트워크 round-trip + Google 정책상 production 환경 비권장. JWK 직접 검증이 표준이며 더 빠름.

**Response 200 OK:**
```json
{
  "accessToken":  "eyJ...",
  "refreshToken": "eyJ...",
  "tokenType":    "Bearer",
  "expiresIn":    1800,
  "user":     { "id": 5678, ... },
  "isNewUser": true
}
```

**Errors:**
- 401 `OAUTH_TOKEN_INVALID` — 서명·iss·aud·exp 검증 실패
- 502 `OAUTH_PROVIDER_ERROR` — JWKS endpoint 5xx (로컬 cache 만료된 상황)

### 4.9 발행하는 Kafka 이벤트

| 이벤트 | 토픽 | 시점 |
| --- | --- | --- |
| `user.deactivated` | `user.deactivated` | POST /me/deactivate 성공 (AFTER_COMMIT) |

---

## 5. Bible Service API

> **Owner:** 김태혁 / **Base URL:** `http://bible-service.qtai.svc.cluster.local:8080`
>
> **OpenAPI 파일:** `apis/bible/openapi.yaml`

### 5.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 5.2 | GET | `/bible/kr/{bookCode}/{chapter}/{verse}` | ✅ | 한국어 (개역한글) |
| 5.3 | GET | `/bible/en/{bookCode}/{chapter}/{verse}` | ✅ | 영어 (KJV PD) |
| 5.4 | GET | `/api/v1/commentary/{bookCode}/{chapter}/{verse}` | ✅ | 주석 (Matthew Henry PD + 더미한글) |
| 5.5 | GET | `/bible/books` | ✅ | 책 목록 조회 (66권) |

> **v1.1 단순화:** v1.0의 사설 통합 endpoint(`/api/v1/passages/...`)를 Bible Service에서 **제거**. 통합은 BFF가 책임 (Bible의 3개 endpoint를 병렬 호출). 03번 § 5.2 BFF UseCase 코드와 정합. 단일 책임 원칙 + endpoint 단위 캐시 일관성 ↑.

### 5.2 GET /bible/kr/{bookCode}/{chapter}/{verse}

**Path 파라미터:**
| 이름 | 타입 | 예 |
| --- | --- | --- |
| bookCode | string (3자) | `GEN`, `EXO`, `REV` (Paratext 표준 66권) |
| chapter | integer ≥ 1 | `1` |
| verse | integer ≥ 1 | `1` |

**Response 200 OK:**
```json
{
  "bookCode":  "GEN",
  "bookNameKr": "창세기",
  "chapter":    1,
  "verse":      1,
  "content":    "태초에 하나님이 천지를 창조하시니라",
  "version":    "REVISED",
  "language":   "ko"
}
```

**Errors:**
- 400 `BOOK_CODE_INVALID`
- 404 `PASSAGE_NOT_FOUND`

**캐시:**
- 키: `cache:passage:kr:{bookCode}:{ch}:{v}`
- TTL: **24h**
- **Hot 100 정의**: 사용자 활동 통계 기반 상위 100구절 (예: 시편 23편, 요한복음 3:16 등) — TTL 7일·preload 시작 시 ETL로 자동 적재. v1.0은 수동 목록 (`config/hot-passages.yml`).

### 5.3 GET /bible/en/{bookCode}/{chapter}/{verse}

**Response 200 OK:**
```json
{
  "bookCode":  "GEN",
  "bookNameEn": "Genesis",
  "chapter":    1,
  "verse":      1,
  "content":    "In the beginning God created the heaven and the earth.",
  "version":    "KJV",
  "language":   "en"
}
```

### 5.4 GET /api/v1/commentary/{bookCode}/{chapter}/{verse}

**Response 200 OK:**
```json
{
  "bookCode": "GEN",
  "chapter":  1,
  "verse":    1,
  "items": [
    {
      "id":       11,
      "source":   "MATTHEW_HENRY",
      "language": "en",
      "title":    "The creation of the world",
      "content":  "The Bible begins with..."
    },
    {
      "id":       12,
      "source":   "DUMMY_KR",
      "language": "ko",
      "title":    "창조의 시작",
      "content":  "성경은 창조로 시작합니다..."
    }
  ]
}
```

> **주의:** 한 구절에 0~N개 주석. 빈 배열 (`"items": []`) 가능 — 404 아님.

### 5.5 GET /bible/books

**Response 200 OK:**
```json
{
  "items": [
    { "code": "GEN", "nameKr": "창세기",   "nameEn": "Genesis",  "chapters": 50 },
    { "code": "EXO", "nameKr": "출애굽기", "nameEn": "Exodus",   "chapters": 40 }
  ]
}
```

> 정적 데이터 — 응답 캐시 24h. 페이지네이션 없음 (66권 고정).

### 5.6 발행하는 Kafka 이벤트

> **없음.** Bible Service는 정적 데이터 — 변경 이벤트 발행 X.

---

## 6. AI/RAG Service API

> **Owner:** 강상민 / **Base URL:** `http://ai-service.qtai.svc.cluster.local:8080`
>
> **OpenAPI 파일:** `apis/ai/openapi.yaml`

### 6.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 6.2 | POST | `/ai/sessions` | ✅ | 세션 시작 |
| 6.3 | POST | `/ai/sessions/{id}/turns` | ✅ | 대화 턴 추가 (**SSE 스트리밍**) |
| 6.4 | GET | `/ai/sessions/{id}` | ✅ | 세션 + 턴 조회 |
| 6.5 | GET | `/ai/sessions` | ✅ | 본인 세션 목록 (페이지네이션) |

### 6.2 POST /ai/sessions

**Request:**
```json
{
  "passage": {
    "bookCode": "GEN",
    "chapter":  1,
    "verse":    1
  },
  "initialStep": "A"
}
```

**OpenAPI schema (v1.1 — default 명시):**
```yaml
StartSessionRequest:
  type: object
  required: [passage]
  properties:
    passage: { $ref: '#/components/schemas/PassageRef' }
    initialStep:
      type: string
      enum: [A, B, C, D]
      default: A          # ⭐ schema default 명시
```

**Response 201 Created:**
```http
HTTP/1.1 201 Created
Location: /ai/sessions/9012
Content-Type: application/json

{
  "id":         9012,
  "userId":     5678,
  "passage":    { "bookId": 1, "bookCode": "GEN", "chapter": 1, "verse": 1 },
  "currentStep": "A",
  "status":     "IN_PROGRESS",
  "createdAt":  "2026-05-26T14:30:00.123Z"
}
```

### 6.3 POST /ai/sessions/{id}/turns — SSE 스트리밍

**Request:**
```http
POST /ai/sessions/9012/turns
Authorization: Bearer ...
Content-Type: application/json
Accept: text/event-stream

{
  "userMessage": "하나님이 천지를 창조하셨다는 게 어떤 의미인가요?"
}
```

**Response 200 OK (`Content-Type: text/event-stream`):**

```
:ok

event: turn_started
data: {"turnId": null, "step": "A", "timestamp": "2026-05-26T14:30:01.000Z"}

event: token
data: {"text": "이 구절은 "}

event: token
data: {"text": "창조의 첫 행위를 "}

event: token
data: {"text": "선언합니다. "}

event: rag_sources
data: {"sources": [
  {"type":"commentary","id":11,"source":"MATTHEW_HENRY","weight":0.82},
  {"type":"dummy_paper","id":3,"weight":0.71}
]}

event: turn_completed
data: {
  "turnId":           33,
  "step":             "A",
  "promptTemplateId": 7,
  "totalTokens":      245,
  "elapsedMs":        4123
}

event: end
data: [DONE]
```

**Event 종류 (§ 9.2 참조):**
- `turn_started` — 턴 시작 마킹
- `token` — 텍스트 토큰 (1개 이상 N개)
- `rag_sources` — 응답 후반부에 RAG 출처 (매 ASSISTANT 턴마다 필수 — 03번 § 3.3 신학 가드레일)
- `step_changed` — 단계 전환 (A→B 등)
- `turn_completed` — 턴 완료 + DB 적재 완료
- `end` — 스트림 종료 (마지막)
- `error` — 에러 (스트림 도중 발생 가능)

**SSE 종료 정책 (03번 § 1.3.2):**
- 첫 토큰 timeout: 5s
- 토큰 간 idle timeout: 30s
- 전체 max: 5분
- 클라이언트 연결 끊김 → `Flux.doFinally(SignalType.CANCEL)` → Anthropic 호출 즉시 중단 (토큰 비용 절약)
- **error → end 정책**: 도중 error 발생 시 `event: error` 후 항상 `event: end [DONE]` 발행 (정상 종료 신호). 클라이언트는 error 받으면 즉시 close해도 OK — 서버는 이미 이벤트 발행 완료.

**Errors (스트림 시작 전 — HTTP 응답):**
- 404 `SESSION_NOT_FOUND`
- 403 `SESSION_NOT_OWNED`
- 422 `SESSION_ALREADY_COMPLETED` — 이미 D 단계 완료된 세션
- 422 `PROMPT_TEMPLATE_NOT_ACTIVE`
- 502 `LLM_PROVIDER_ERROR`
- 504 `LLM_TIMEOUT`

**Errors (스트림 도중 — SSE event):**
```
event: error
data: {"code": "LLM_PROVIDER_ERROR", "detail": "Anthropic API 503 after 3 retries", "traceId": "..."}

event: end
data: [DONE]
```

### 6.4 GET /ai/sessions/{id}

**Response 200 OK:**
```json
{
  "id":          9012,
  "userId":      5678,
  "passage":     { "bookId": 1, "bookCode": "GEN", "chapter": 1, "verse": 1 },
  "currentStep": "C",
  "status":      "IN_PROGRESS",
  "summary":     null,
  "createdAt":   "2026-05-26T14:30:00.123Z",
  "updatedAt":   "2026-05-26T14:42:11.789Z",
  "turns": [
    {
      "id":               31,
      "role":             "SYSTEM",
      "step":             null,
      "content":          "",
      "contentRedacted":  true,
      "createdAt":        "2026-05-26T14:30:00.150Z"
    },
    {
      "id":               32,
      "role":             "USER",
      "step":             "A",
      "content":          "하나님이 천지를 창조하셨다는 게 어떤 의미인가요?",
      "contentRedacted":  false,
      "createdAt":        "2026-05-26T14:30:01.000Z"
    },
    {
      "id":               33,
      "role":             "ASSISTANT",
      "step":             "A",
      "content":          "이 구절은 창조의 첫 행위를 선언합니다...",
      "contentRedacted":  false,
      "promptTemplateId": 7,
      "ragSources":       [ {"type":"commentary","id":11,"weight":0.82} ],
      "createdAt":        "2026-05-26T14:30:05.123Z"
    }
  ]
}
```

> **v1.1 SYSTEM 턴 마스킹 schema:**
> - `content`: 항상 string — SYSTEM은 빈 문자열 (`""`)
> - `contentRedacted`: boolean — true면 클라이언트가 해당 턴을 화면에서 숨김 또는 placeholder 표시
> - **금지:** SYSTEM 턴 본문 노출. yaml schema에서 `contentRedacted: true`인 경우 클라이언트가 무시하도록 명시.

### 6.5 GET /ai/sessions

**Query:** `?status=COMPLETED&page=0&size=20&sort=createdAt,desc`

**Response 200 OK:**
```json
{
  "items": [
    {
      "id":          9012,
      "passage":     { "bookCode": "GEN", "chapter": 1, "verse": 1 },
      "currentStep": "D",
      "status":      "COMPLETED",
      "createdAt":   "2026-05-26T14:30:00Z"
    }
  ],
  "page": { "number": 0, "size": 20, "totalElements": 12, "totalPages": 1 }
}
```

> 본인 세션만 조회. user_id는 X-User-Id 헤더로 자동 필터링. `PageResponse<T>` (§ 2.7).

### 6.6 발행하는 Kafka 이벤트

| 이벤트 | 토픽 | 시점 | 멱등성 키 |
| --- | --- | --- | --- |
| `ai.session.completed` | `ai.session.completed` | D 단계 도달 시 (AFTER_COMMIT) | `ai.session.completed:{session_id}` |

### 6.7 컨슈머 토픽

| 토픽 | Consumer Group | 동작 |
| --- | --- | --- |
| `user.deactivated` | `ai-service-user-deactivation-consumer` | 해당 user의 IN_PROGRESS 세션 → status=ABANDONED 마킹 |
| `journal.creation.failed` ⭐v1.2 | `ai-service-saga-compensation-consumer` | AI_SESSIONS.status='COMPLETED_NO_JOURNAL' 마킹 (Saga 보상 — 03번 § 6.1) |

---

## 7. Journal Service API

> **Owner:** 이승욱 / **Base URL:** `http://journal-service.qtai.svc.cluster.local:8080`
>
> **OpenAPI 파일:** `apis/journal/openapi.yaml`

### 7.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 7.2 | GET | `/api/v1/journals` | ✅ | 본인 journal 목록 (페이지네이션) |
| 7.3 | GET | `/api/v1/journals/{id}` | ✅ | journal 단건 조회 |
| 7.4 | PATCH | `/api/v1/journals/{id}` | ✅ | journal 수정 (이벤트 소싱) |
| 7.5 | DELETE | `/api/v1/journals/{id}` | ✅ | journal 삭제 (Soft Delete) |
| 7.6 | POST | `/api/v1/journals/{id}/restore` | ✅ | soft-deleted 복원 (v1.1) |
| 7.7 | GET | `/api/v1/journals/{id}/events` | ✅ | 이벤트 로그 조회 (감사용) |

> **주의:** **`POST /api/v1/journals` (수동 생성) 없음 v1.0** — Journal은 AI 세션 완료(`ai.session.completed` Kafka 컨슈머)로 자동 DRAFT 생성만. 사용자는 **수정·발행만** 가능.

### 7.2 GET /api/v1/journals

**Query:** `?status=PUBLISHED&page=0&size=20&sort=publishedAt,desc`

**Response 200 OK:**
```json
{
  "items": [
    {
      "id":           12345,
      "passage":      { "bookCode": "GEN", "chapter": 1, "verse": 1 },
      "title":        "태초의 묵상",
      "status":       "PUBLISHED",
      "aiSessionId":  9012,
      "createdAt":    "2026-05-26T14:45:00Z",
      "publishedAt":  "2026-05-26T15:10:00Z",
      "updatedAt":    "2026-05-26T15:10:00Z"
    }
  ],
  "page": { "number": 0, "size": 20, "totalElements": 24, "totalPages": 2 }
}
```

> **본인 journal만** (X-User-Id 자동 필터). soft-deleted (`deleted_at IS NOT NULL`)는 기본 제외. `PageResponse<T>` (§ 2.7).

### 7.3 GET /api/v1/journals/{id}

**Response 200 OK:**
```json
{
  "id":           12345,
  "userId":       5678,
  "passage":      { "bookCode": "GEN", "chapter": 1, "verse": 1 },
  "title":        "태초의 묵상",
  "content":      "오늘 묵상에서 깨달은 것은...",
  "status":       "PUBLISHED",
  "aiSessionId":  9012,
  "lastEventSequence": 4,
  "createdAt":    "2026-05-26T14:45:00Z",
  "publishedAt":  "2026-05-26T15:10:00Z",
  "updatedAt":    "2026-05-26T15:10:00Z"
}
```

**Errors:**
- 404 `JOURNAL_NOT_FOUND`
- 403 `JOURNAL_NOT_OWNED`

### 7.4 PATCH /api/v1/journals/{id} — 수정 (이벤트 소싱)

**Request:**
```json
{
  "title":   "태초의 묵상 (수정)",
  "content": "수정된 내용",
  "status":  "PUBLISHED"
}
```

> **변경 가능 필드:** `title`, `content`, `status` (DRAFT → PUBLISHED only — v1.2 정정). 다른 필드는 무시.

**Response 200 OK:**
```json
{
  "id":           12345,
  "title":        "태초의 묵상 (수정)",
  "content":      "수정된 내용",
  "status":       "PUBLISHED",
  "lastEventSequence": 5,
  "updatedAt":    "2026-05-26T16:00:00Z"
}
```

**처리 시퀀스 (v1.1 — idempotency_key 자동 생성 명시):**
1. TX 시작
2. JOURNALS row 잠금 (`@Lock(PESSIMISTIC_WRITE)` — `findByIdLocked`)
3. `last_event_sequence + 1`
4. **idempotency_key 서버 자동 생성**: `journal.update:{ULID}` (`com.github.f4b6a3.ulid.UlidCreator`). HTTP 본문에 클라이언트 측 키 받지 않음 — § 2.11 멱등성 정책상 v1.0은 Kafka 컨슈머 측만 멱등성 보장
5. JOURNAL_EVENTS INSERT (eventType=`UPDATED` 또는 `PUBLISHED`, `idempotency_key UNIQUE`, `(journal_id, sequence) UNIQUE`)
6. JOURNALS read model 갱신
7. TX 커밋
8. **AFTER_COMMIT** → KafkaTemplate `journal.updated` (또는 `journal.created`/`journal.published`)

> **status 전이 규칙:** DRAFT → PUBLISHED 허용. PUBLISHED → DRAFT **금지** → 422 `INVALID_STATUS_TRANSITION`.

**Errors:**
- 404 `JOURNAL_NOT_FOUND`
- 403 `JOURNAL_NOT_OWNED`
- 409 `JOURNAL_LOCKED` — 동시 수정 충돌 (Lock timeout)
- 422 `INVALID_STATUS_TRANSITION` — PUBLISHED → DRAFT
- 422 `INVALID_EVENT_SEQUENCE` — UNIQUE 위반 (이론상 발생 안 해야 함, 발생 시 race)

### 7.5 DELETE /api/v1/journals/{id}

**Response 204 No Content**

**처리 (Soft Delete):**
1. TX 시작
2. JOURNALS row 잠금
3. `JOURNALS.deleted_at = NOW()`, `last_event_sequence + 1`
4. JOURNAL_EVENTS INSERT (eventType=`DELETED`, idempotency_key=`journal.delete:{journal_id}:{epoch_ms}`)
5. TX 커밋
6. **AFTER_COMMIT** → Kafka `journal.deleted`

**Errors:**
- 404 `JOURNAL_NOT_FOUND`
- 403 `JOURNAL_NOT_OWNED`

### 7.6 POST /api/v1/journals/{id}/restore (v1.1)

> v1.0 미구현. v1.1 ADR-0006 후속 작업.

### 7.7 GET /api/v1/journals/{id}/events

> 감사 목적. 본인 journal의 모든 이벤트 시퀀스 조회 — 02번 § 11.5 event_data 예시와 정합.

**Response 200 OK:**
```json
{
  "journalId": 12345,
  "events": [
    {
      "id":              101,
      "sequence":        1,
      "eventType":       "CREATED",
      "eventData":       {
        "title":        "AI가 작성한 초안 (제목 추천)",
        "content":      "...",
        "aiSessionId":  9012,
        "passage":      { "bookCode": "GEN", "chapter": 1, "verse": 1 }
      },
      "idempotencyKey":  "ai.session.completed:9012",
      "createdAt":       "2026-05-26T14:45:00Z"
    },
    {
      "id":              102,
      "sequence":        2,
      "eventType":       "UPDATED",
      "eventData":       { "title": "태초의 묵상 (수정)" },
      "idempotencyKey":  "journal.update:01HZX0K8YGBZ3SQ7H4M2N9R5W6",
      "createdAt":       "2026-05-26T15:00:00Z"
    },
    {
      "id":              103,
      "sequence":        3,
      "eventType":       "PUBLISHED",
      "eventData":       { "publishedAt": "2026-05-26T15:10:00Z" },
      "idempotencyKey":  "journal.update:01HZX0M3F2QPYW1KEH8C4D7T9V",
      "createdAt":       "2026-05-26T15:10:00Z"
    }
  ]
}
```

### 7.8 발행하는 Kafka 이벤트

| 이벤트 | 토픽 | 시점 | 멱등성 키 |
| --- | --- | --- | --- |
| `journal.created` | `journal.created` | AI 세션 컨슈머가 DRAFT 생성 시 (AFTER_COMMIT) | `ai.session.completed:{session_id}` |
| `journal.updated` | `journal.updated` | PATCH (AFTER_COMMIT) | `journal.update:{ULID}` |
| `journal.deleted` | `journal.deleted` | DELETE (AFTER_COMMIT) | `journal.delete:{journal_id}:{epoch_ms}` |
| `journal.creation.failed` ⭐v1.2 | `journal.creation.failed` | `ai.session.completed` 컨슈머 영구 실패 시 @DltHandler에서 발행 (Saga 보상) | `journal.creation.failed:{session_id}` |

### 7.9 컨슈머 토픽

| 토픽 | Consumer Group | 동작 |
| --- | --- | --- |
| `ai.session.completed` | `journal-service-ai-completion-consumer` | DRAFT Journal + JOURNAL_EVENTS (CREATED) 적재 |
| `user.activity.tracked` | `journal-service-activity-stats-consumer` | (v1.1) 통계 적재. v1.0 무시 |
| `user.deactivated` | `journal-service-user-deactivation-consumer` | (v1.0 보존, v1.1 GDPR 검토) |

---

## 8. BFF Aggregator API

> **Owner:** 강태오 / **Base URL:** `http://bff-aggregator.qtai.svc.cluster.local:8080`
>
> **OpenAPI 파일:** `apis/bff/openapi.yaml`

### 8.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 8.2 | GET | `/api/v1/me/dashboard` | ✅ | 통합 대시보드 (4 service 병렬) |
| 8.3 | GET | `/api/v1/passages/{bookCode}/{chapter}/{verse}` | ✅ | 입체 묵상 화면 (Bible 3개 endpoint 병렬) |
| 8.4 | WS | `/ws/notifications` | ✅ | 실시간 알림 (STOMP) |

### 8.2 GET /api/v1/me/dashboard — v1.1 호출 service 정확화

**처리:** **4 service 병렬 호출** (`CompletableFuture.allOf`):
1. **Auth Service** `/auth/me` → `user` (id, nickname)
2. **Journal Service** `/journals?size=5&sort=createdAt,desc` → `recentJournals` + `stats.journalCount`
3. **AI Service** `/ai/sessions?status=IN_PROGRESS&size=1&sort=updatedAt,desc` → `activeSession` (가장 최근 1개) + `stats.completedSessions` (별도 count query)
4. **BFF 자체 정적 매핑** → `todayPassage` (v1.2 정정 — § 5에 Bible Service `/bible/today` endpoint 없음. v1.0은 BFF가 수정 정적 테이블 조회 (요일별 추천 또는 Hot 100 random 1개). v1.1 Bible Service에 endpoint 추가 검토)

> **`activeSession` 정책 (v1.1):** 사용자가 다중 passage로 세션 동시 진행 가능하지만 대시보드는 **가장 최근 updatedAt IN_PROGRESS 세션 1개**만 노출. 전체 목록은 `/ai/sessions` 따로 호출.

> **stats.currentStreak / longestStreak:** v1.0은 Journal Service가 본인 journal 일자별 집계로 계산 (간단 SQL). v1.1에 별도 `user.activity.tracked` Kafka 컨슈머로 통계 테이블 분리.

**Response 200 OK:**
```json
{
  "user": {
    "id": 5678,
    "nickname": "홍길동"
  },
  "stats": {
    "journalCount":      24,
    "completedSessions":  18,
    "currentStreak":      3,
    "longestStreak":     12
  },
  "todayPassage": {
    "bookCode": "PSA",
    "chapter":  23,
    "verse":    1
  },
  "recentJournals": [
    { "id": 12345, "title": "태초의 묵상", "status": "PUBLISHED", "createdAt": "..." }
  ],
  "activeSession": {
    "id":           9012,
    "passage":      { "bookCode": "GEN", "chapter": 1, "verse": 1 },
    "currentStep":  "C",
    "updatedAt":    "2026-05-26T14:42:11.789Z"
  }
}
```

> 진행 중인 세션이 없으면 `"activeSession": null`.

**구현:** UseCase 1개 (`GetDashboardUseCase`) — 4 future 병렬. 어느 하나가 실패해도 partial 응답 (해당 필드만 null + 헤더 `X-Partial-Response: auth-service-down`).

### 8.3 GET /api/v1/passages/{bookCode}/{chapter}/{verse}

**처리 (v1.1 명시):** 03번 § 1.3.1 시나리오 1. **BFF가 Bible Service의 3개 endpoint를 병렬 직접 호출** (단일 책임 + 캐시 단위 명확):
1. `GET /bible/kr/{...}` → `kr`
2. `GET /bible/en/{...}` → `en`
3. `GET /api/v1/commentary/{...}` → `commentaries`

**Response 200 OK:**
```json
{
  "passage": { "bookCode": "GEN", "chapter": 1, "verse": 1 },
  "kr":  { "content": "태초에...", "version": "REVISED", "language": "ko" },
  "en":  { "content": "In the beginning...", "version": "KJV", "language": "en" },
  "commentaries": [
    { "id": 11, "source": "MATTHEW_HENRY", "title": "...", "content": "..." },
    { "id": 12, "source": "DUMMY_KR",      "title": "...", "content": "..." }
  ]
}
```

**사이드 이펙트 (사용자 활동 이벤트 발행):**
- `KafkaTemplate` → `user.activity.tracked` 발행 (Best-effort, 응답 본문에 영향 X)
- 페이로드: `{ userId, type: "READ_PASSAGE", book, chapter, verse, occurredAt }`
- 멱등성 키: `read.passage:{user_id}:{book}:{ch}:{v}:{epoch_minute}`

> **epoch_minute 분 경계 noted (v1.1):** 분 경계(59초→1초)에서 같은 user가 1초 차이로 두 번 접근 시 epoch_minute 다름 → 2회 적재 가능. v1.0 의도된 단순화 — 통계 정확성보다 단순성 우선. v1.1에 sliding window 검토.

### 8.4 WS /ws/notifications — STOMP WebSocket

> § 10 (WebSocket 표준) 참조.

### 8.5 발행하는 Kafka 이벤트

| 이벤트 | 토픽 | 시점 | 멱등성 키 |
| --- | --- | --- | --- |
| `user.activity.tracked` | `user.activity.tracked` | GET /passages/... 호출 시 (Best-effort) | `read.passage:{user_id}:{book}:{ch}:{v}:{epoch_minute}` |

### 8.6 컨슈머 토픽

| 토픽 | Consumer Group | 동작 |
| --- | --- | --- |
| `notification.requested` | `bff-notification-dispatcher-consumer` | Redis-WS 활성 세션 조회 → STOMP push (활성 시) / 폐기 (비활성 시) |
| `journal.created` | `bff-journal-notification-consumer` (선택 v1.1) | 알림 생성 |

> **Consumer Group 명명 표준 (03번 § 4.3 정합):** `{service}-{topic-purpose}-consumer`. BFF가 다중 Pod일 때 같은 group 내 1개 Pod만 메시지 수신 → Redis-WS pub/sub로 다른 Pod에 dispatch (§ 10.6).

---

## 9. SSE (Server-Sent Events) 표준

### 9.1 사용처

| Endpoint | 용도 |
| --- | --- |
| `POST /ai/sessions/{id}/turns` | AI 응답 토큰 스트리밍 (§ 6.3) |

### 9.2 Event 종류 (§ 6.3 상세)

| Event | data 페이로드 | 빈도 | 의미 |
| --- | --- | --- | --- |
| `turn_started` | `{ "turnId": null, "step": "A", "timestamp": "..." }` | 1회 | 턴 처리 시작 (DB 적재 전 → turnId null) |
| `token` | `{ "text": "..." }` | N회 | LLM 토큰 (1~수백) |
| `step_changed` | `{ "from": "A", "to": "B" }` | 0~1회 | 단계 전환 감지 |
| `rag_sources` | `{ "sources": [{ "type": ..., "id": ..., "weight": ... }] }` | 1회 | **ASSISTANT 턴마다 필수** (신학 가드레일) |
| `turn_completed` | `{ "turnId": 33, "step": "A", "promptTemplateId": 7, "totalTokens": 245, "elapsedMs": 4123 }` | 1회 | DB 적재 완료 후 |
| `error` | `{ "code": "...", "detail": "...", "traceId": "..." }` | 0~1회 | 도중 에러 |
| `end` | `[DONE]` | 1회 (마지막) | 스트림 종료 신호 (error 후에도 항상 발행) |

### 9.3 헤더 / 응답 표준

```http
Content-Type: text/event-stream; charset=utf-8
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

### 9.4 Timeout / 종료 정책 + Spring 표준 heartbeat

| 항목 | 값 |
| --- | --- |
| 첫 토큰 timeout | 5s (이후 504 `LLM_TIMEOUT`) |
| 토큰 간 idle timeout | 30s |
| 전체 max | 5분 |
| heartbeat (idle 시) | 15s마다 SSE 주석 라인 |
| 클라이언트 끊김 | `Flux.doFinally(SignalType.CANCEL)` → Anthropic 호출 즉시 dispose |

**Spring Reactor SSE 표준 — `ServerSentEvent.comment()`:**

```java
@PostMapping(value = "/sessions/{id}/turns", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
public Flux<ServerSentEvent<Object>> stream(@PathVariable Long id, @RequestBody TurnRequest req) {
    Flux<ServerSentEvent<Object>> events = continueConversationUseCase.stream(id, req);

    // 15s마다 heartbeat (clean shutdown 친화적)
    Flux<ServerSentEvent<Object>> heartbeat = Flux.interval(Duration.ofSeconds(15))
        .map(i -> ServerSentEvent.builder().comment("keep-alive").build());

    return Flux.merge(events, heartbeat)
        .takeUntil(e -> "end".equals(e.event()))    // end 도달 시 heartbeat 정지
        .doFinally(sig -> {
            if (sig == SignalType.CANCEL) {
                anthropicCall.dispose();
            }
        });
}
```

### 9.5 Flutter 구현 표준 (v1.1 — 라이브러리 fix)

```dart
// pubspec.yaml — 권장 (v1.0 시점 verified)
dependencies:
  dio: ^5.4.0
  flutter_client_sse: ^2.0.1     // 또는 dio_sse: ^1.x (둘 다 검증됨)

// 사용 예 (flutter_client_sse 기준)
SSEClient.subscribeToSSE(
  method: SSERequestType.POST,
  url: 'https://api.qtai.app/ai/sessions/$id/turns',
  header: {
    'Authorization': 'Bearer $accessToken',
    'Accept':        'text/event-stream',
    'Content-Type':  'application/json',
  },
  body: { 'userMessage': msg },
).listen((event) {
  switch (event.event) {
    case 'token':       /* 텍스트 누적 */
    case 'rag_sources': /* 출처 표시 */
    case 'turn_completed': /* 입력창 다시 활성 */
    case 'error':       /* SnackBar */
    case 'end':         SSEClient.unsubscribeFromSSE();
  }
});

// 화면 dispose 시 SSEClient.unsubscribeFromSSE() 필수 — 서버 SSE cancel 트리거
```

### 9.6 Gateway 패스스루 표준 + 금지 filter (v1.1)

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: ai-sse
          uri: http://ai-service:8080
          predicates:
            - Path=/ai/sessions/*/turns
            - Method=POST
          filters:
            - PreserveHostHeader
            - SetResponseHeader=X-Accel-Buffering, no
            # 금지된 filter (응답 buffering 또는 body 변환 → SSE 끊김):
            # - ModifyResponseBody
            # - RemoveJsonAttributesResponseBody
            # - JsonToGrpc
            # - GzipMessageBody (응답에 한해)
```

> **금지 filter 목록 (v1.1):** SSE 라우트에는 **응답 본문을 buffering하거나 변환하는 filter 사용 금지**. 위 4개는 SSE 스트림을 깨뜨림.

---

## 10. WebSocket (STOMP) 표준

### 10.1 사용처

| Endpoint | 용도 |
| --- | --- |
| `WS /ws/notifications` | 서버 → 클라이언트 실시간 알림 (BFF Aggregator) |

### 10.2 핸드셰이크 + 인증 (v1.1 — STOMP CONNECT 헤더)

> **v1.1 변경:** v1.0의 query param token (`?token=...`)은 referer 헤더·서버 access log·브라우저 history에 노출됨 — HTTPS여도 위험. **v1.0부터 STOMP CONNECT 프레임 헤더로 변경**.

```
[클라이언트] WS connect: wss://api.qtai.app/ws/notifications     (prod)
                        ws://localhost:8080/ws/notifications     (dev)

[Gateway]  WS handshake (HTTP GET + Upgrade) → 인증 ❌ 단순 패스스루
           ⭐ v1.2 — Gateway는 WebSocket handshake에 JWT 필터 적용 X (§ 3 라우팅 표)
           ✋ handshake는 GET HTTP이고 STOMP CONNECT 프레임은 아직 도착 전이라
              JWT 헤더가 없음. 이 단계에 인증 강제 시 401로 연결 차단됨.

[클라이언트] STOMP CONNECT 프레임:
  CONNECT
  accept-version:1.2
  host:api.qtai.app
  Authorization:Bearer eyJhbGc...
  
  ^@

[BFF]      STOMP CONNECT 수신 → Authorization 헤더 검증 (RS256 공개키)
           성공 시 → Redis-WS 등록:
             SADD ws:session:{user_id} {session_id}
             SET  ws:session:{session_id}:meta {"user_id":..., "podName":...} EX 86400
           실패 시 → STOMP ERROR 프레임 발행 + WS 종료
           성공 완료 시 → CONNECTED 프레임 응답
```

> **wss vs ws (v1.1):** prod는 wss (TLS 종료는 ingress 또는 Gateway), dev는 ws OK.

### 10.3 STOMP 프레임 표준

**구독:**
```
SUBSCRIBE
id:sub-0
destination:/user/queue/notifications

^@
```

**서버 → 클라이언트 push 예 (notification.requested 컨슈머가 수신):**
```
MESSAGE
destination:/user/queue/notifications
content-type:application/json
message-id:msg-12345

{
  "id":         "ntf_01HZX...",
  "type":       "JOURNAL_AI_DRAFT_READY",
  "title":      "AI가 묵상 초안을 작성했어요",
  "body":       "GEN 1:1 묵상 초안이 준비됐어요. 확인해보세요.",
  "deeplink":   "/journals/12345",
  "metadata":   { "journalId": 12345, "aiSessionId": 9012 },
  "createdAt":  "2026-05-26T15:10:00Z"
}
```

### 10.4 알림 type 표 (v1.0) + 확장 절차

| type | 트리거 | 페이로드 metadata |
| --- | --- | --- |
| `JOURNAL_AI_DRAFT_READY` | AI 세션 완료 → Journal DRAFT 생성 | `journalId`, `aiSessionId` |
| `JOURNAL_PUBLISHED` | (선택) 본인 journal published | `journalId` |
| `STREAK_MILESTONE` | (v1.1) 연속 묵상 달성 | `streak` |

> **확장 절차 (v1.1):** 새 type 추가 시
> 1. Producer Service의 `notification.requested` 토픽에 새 type 페이로드 발행 코드 추가
> 2. 본 § 10.4 표 + Schema Registry `notification.requested-value` schema 업데이트 (BACKWARD 호환)
> 3. Flutter 클라이언트 type 분기 추가
> 4. PR 머지 — 1·2·3을 같은 PR에 묶어 atomicity 보장

### 10.5 Ping / 재연결

| 항목 | 값 |
| --- | --- |
| Heartbeat (서버 → 클라이언트) | 30s |
| Heartbeat (클라이언트 → 서버) | 30s |
| 재연결 backoff | exponential 1s → max 30s |
| 재연결 후 미수신 알림 | v1.0 받지 못함 (stateless WS — ADR-0012). v1.1에 NOTIFICATION_LOG 도입 후 미수신 동기화 |

### 10.6 Pod 다중 인스턴스 처리 (v1.1 다이어그램 정확화)

```
[Producer Service] ─Kafka publish─▶ notification.requested
                                          │
                                          ▼
                  ┌──────────────────────────────────────────┐
                  │ Consumer Group: bff-notification-        │
                  │                 dispatcher-consumer       │
                  │ (Pod-A 또는 Pod-B 중 1개만 메시지 수신)   │
                  └──────────────────────────────────────────┘
                                          │ (Pod-A가 수신했다고 가정)
                                          ▼
        Pod-A: Redis-WS GET ws:session:{user_id}:meta
                                          │
                          ┌───────────────┴───────────────┐
                          ▼ (해당 세션 podName=Pod-A)      ▼ (podName=Pod-B)
                  Pod-A 자체 STOMP push        Pod-A: Redis-WS PUBLISH
                  (사용자에게 직접 전달)         channel: ws:notify:{user_id}
                                                          │
                                                          ▼
                                              Pod-B: SUBSCRIBE 콜백
                                              → 자기 STOMP 세션에 push
```

> **핵심:**
> - Consumer Group은 1 토픽당 N Pod 중 1개만 메시지 수신 (Kafka 보장)
> - 하지만 그 사용자의 WS 세션이 다른 Pod에 있을 수 있음 → Redis-WS 메타로 podName 조회
> - 다른 Pod이면 Redis pub/sub로 dispatch
> - 같은 Pod이면 직접 push

---

## 11. OpenAPI 3.1 yaml 디렉토리 + Spectral 룰

### 11.1 디렉토리

```
apis/
├── auth/openapi.yaml
├── bible/openapi.yaml
├── ai/openapi.yaml
├── journal/openapi.yaml
└── bff/openapi.yaml
```

> Gateway는 OpenAPI 안 만듦 — 라우팅만이라 본 문서 § 3 표가 정답.

### 11.2 OpenAPI 골격 표준 (예: auth) — v1.1 info.contact 추가

```yaml
openapi: 3.1.0
info:
  title: QT-AI Auth Service
  version: 1.0.0
  description: |
    회원·JWT·OAuth Service.
    Owner: 이지윤
  contact:                          # ⭐ v1.1 — Spectral 룰 info-contact: error 통과용
    name: 이지윤 (Auth Service Owner)
    email: kang.sangmin@example.com  # 임시; W0에 실제 contact로 교체
servers:
  - url: https://api.qtai.app
    description: Production (via Gateway)
  - url: http://localhost:4011        # ⭐ v1.1 — § 12.2 포트와 일관
    description: Local Prism mock (auth)

tags:
  - name: auth-public
  - name: auth-private

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  schemas:
    ProblemDetail:
      type: object
      required: [type, title, status, code, traceId, timestamp]
      properties:
        type:      { type: string, format: uri }
        title:     { type: string }
        status:    { type: integer }
        detail:    { type: string }
        instance:  { type: string }
        code:      { type: string }
        traceId:   { type: string }
        timestamp: { type: string, format: date-time }
        errors:
          type: array
          items: { $ref: '#/components/schemas/FieldError' }
    FieldError:
      type: object
      properties:
        field:   { type: string }
        code:    { type: string }
        message: { type: string }
    LoginRequest:
      type: object
      required: [email, password]
      properties:
        email:    { type: string, format: email, maxLength: 254 }
        password: { type: string, minLength: 8, maxLength: 72 }
    LoginResponse:
      type: object
      required: [accessToken, refreshToken, tokenType, expiresIn, user]
      properties:
        accessToken:  { type: string }
        refreshToken: { type: string }
        tokenType:    { type: string, const: Bearer }
        expiresIn:    { type: integer }
        user:         { $ref: '#/components/schemas/UserSummary' }
    UserSummary:
      type: object
      required: [id, email, nickname]
      properties:
        id:       { type: integer, format: int64 }
        email:    { type: string }
        nickname: { type: string }

paths:
  /auth/login:
    post:
      tags: [auth-public]
      operationId: login
      summary: 로그인
      security: []
      requestBody:
        required: true
        content:
          application/json:
            schema: { $ref: '#/components/schemas/LoginRequest' }
      responses:
        '200':
          description: 로그인 성공
          content:
            application/json:
              schema: { $ref: '#/components/schemas/LoginResponse' }
              example:
                accessToken:  "eyJhbGc..."
                refreshToken: "eyJhbGc..."
                tokenType:    Bearer
                expiresIn:    1800
                user: { id: 5678, email: "user@example.com", nickname: "홍길동" }
        '401':
          description: INVALID_CREDENTIALS
          content:
            application/problem+json:
              schema: { $ref: '#/components/schemas/ProblemDetail' }
        '429':
          description: RATE_LIMITED
          headers:
            Retry-After: { schema: { type: integer } }
          content:
            application/problem+json:
              schema: { $ref: '#/components/schemas/ProblemDetail' }
```

### 11.3 Spectral 룰 (`.spectral.yaml`) — v1.1 함수 정정

```yaml
extends:
  - "spectral:oas"
rules:
  # 모든 endpoint operationId 필수
  operation-operationId: error

  # 모든 endpoint summary 필수
  operation-description: warn
  operation-summary: error

  # 모든 4xx/5xx 응답에 application/problem+json 사용 (v1.1 정정 — truthy 함수)
  problem-json-on-errors:
    description: 4xx/5xx 응답은 application/problem+json + ProblemDetail 사용
    severity: error
    given: $.paths[*][*].responses[?(@property.match(/^[45]/))].content
    then:
      field: "application/problem+json"
      function: truthy

  # 인증 필요 endpoint는 security 명시
  operation-security-defined: error

  # snake_case 금지 (응답 본문 필드는 camelCase)
  schema-property-camelcase:
    description: schema property는 camelCase
    severity: warn
    given: $..properties[*]~
    then:
      function: pattern
      functionOptions:
        match: '^[a-z][a-zA-Z0-9]*$'

  # 모든 schema에 example 권장
  schema-example: warn

  # contact 정보 (info.contact) 필수
  info-contact: error
```

### 11.4 PR 머지 게이트 (03번 § 10.3 정합) — v1.1 .spectral.yaml 위치 명시

> **`.spectral.yaml` 위치:** **모노레포 루트** (`./.spectral.yaml`). Spectral CLI는 working dir에서 자동 탐색.

```yaml
# .github/workflows/ci.yml — lint job 안에
- name: Spectral OpenAPI lint
  working-directory: ${{ github.workspace }}
  run: |
    npx @stoplight/spectral-cli lint apis/auth/openapi.yaml
    npx @stoplight/spectral-cli lint apis/bible/openapi.yaml
    npx @stoplight/spectral-cli lint apis/ai/openapi.yaml
    npx @stoplight/spectral-cli lint apis/journal/openapi.yaml
    npx @stoplight/spectral-cli lint apis/bff/openapi.yaml
```

> Spectral error 1개라도 발견 시 머지 차단.

---

## 12. Mock 서버 (Prism) 가동 절차

### 12.1 목적

> Flutter (김지민)와 BFF (강태오)의 작업 unblock. 백엔드 코드 0줄에서도 OpenAPI yaml만 있으면 Mock 응답 가능.

### 12.2 가동 명령

```bash
# 5개 service 동시 가동 (각자 다른 포트, § 11.2 servers URL과 일관)
npm install -g @stoplight/prism-cli@^5

prism mock apis/auth/openapi.yaml    --port 4011 &
prism mock apis/bible/openapi.yaml   --port 4012 &
prism mock apis/ai/openapi.yaml      --port 4013 &
prism mock apis/journal/openapi.yaml --port 4014 &
prism mock apis/bff/openapi.yaml     --port 4015 &
```

### 12.3 Flutter `dev` 환경 base URL

```dart
// flutter-app/lib/config/env.dart
class Env {
  static const String baseUrl = String.fromEnvironment(
    'BASE_URL',
    defaultValue: 'http://localhost:4015',  // BFF mock (가장 자주 호출)
  );
}

// 빌드 시:
// flutter run --dart-define=BASE_URL=http://localhost:4015
```

### 12.4 Mock 응답 정확도

> **Prism 동작:** OpenAPI `responses[].content.application/json.example` 또는 `examples` 사용. 없으면 `schema`에서 자동 생성 (이상한 값 가능).

**원칙:** 모든 endpoint의 200/201/204 응답에 **`example` 필수** — 본 문서 § 4~8의 응답 예시를 yaml에 그대로 박제.

### 12.5 W1 일정 + Mock ↔ 실제 일치 검증 (v1.1)

| 요일 | 산출물 |
| --- | --- |
| 월 5/18 | OpenAPI 골격 5개 작성 (operationId만) |
| 화 5/19 | request·response schema + example 작성 → **Spectral lint 통과** |
| 화 5/19 ~ | Prism mock 5포트 가동 → Flutter `dev` 환경 연결 → 김지민 코딩 시작 |
| 금 5/22 | Mock ↔ 실제 백엔드 1개 service 응답 일치 검증 |

**일치 검증 방법 (v1.1):**

**옵션 A — `prism proxy` 모드:**
```bash
# 실제 백엔드 호출하면서 OpenAPI 스키마 위반 감지
prism proxy apis/auth/openapi.yaml http://auth-service:8080 --port 4011 --errors
# 응답이 schema와 다르면 콘솔에 경고 출력
```

**옵션 B — `dredd` (응답 자동 검증):**
```bash
npm install -g dredd
dredd apis/auth/openapi.yaml http://auth-service:8080 --hookfiles=./hooks.js
# 모든 endpoint를 호출하고 응답이 schema에 맞는지 자동 assertion
```

W1 5/22에 강태오 + 1명이 Auth 또는 Bible service 1개 대상으로 검증 후 결과 #qtai-api 채널에 공유.

---

## 13. 1차(HMS) 실패 패턴 ↔ API 가드레일

| 1차 실패 | MSA에서 증폭 | 본 문서 가드레일 |
| --- | --- | --- |
| API 응답 일관성 부재 (envelope 혼용) | 5 service × envelope 종류 → 클라이언트 분기 폭증 | § 2.3 envelope 사용 안 함 + § 2.4 ProblemDetail 표준화 |
| 에러 응답 형식 제각각 | 5 service × 에러 형식 환각 | § 2.4 RFC 7807 ProblemDetail + § 2.6 도메인 코드 표 (28개) + Spectral 룰로 강제 |
| HTTP status 잘못 사용 (200 + success:false) | 5 service × status 잘못 | § 2.5 표 + 머지 리뷰 체크 + § 2.5 503 매핑 책임 명시 |
| 인증 헤더 직접 검증 누락 | 5 service × 인증 누락 가능 | § 2.1 Gateway 단일 검증 + § 3 라우팅 표 + ADR-0012 |
| 페이지네이션 형식 제각각 | 5 service × 다른 응답 | § 2.7 Custom `PageResponse<T>` 표준 |
| (신규) **OpenAPI 없는 endpoint 머지** | 클라이언트와 어긋남 | § 11.4 Spectral 룰 + PR 머지 게이트 |
| (신규) **breaking change 무통보** | 클라이언트 깨짐 | § 1.3 v2 분기 정책 + ADR 발행 + #qtai-api Slack |
| (신규) SSE timeout 미설정 → 영원히 hang | LLM 비용 폭증 + 사용자 경험 ↓ | § 9.4 timeout 표 + Spring SSE 표준 + `Flux.doFinally(CANCEL)` |
| (신규) WebSocket 인증 누락 | 다른 사용자에게 알림 누출 | § 10.2 STOMP CONNECT 헤더 + JWT 검증 + Redis-WS user_id 격리 |
| (신규) Rate limit 없어 brute-force | login 무차별 시도 | § 2.10 endpoint별 표 — login 5/min |
| (신규) Refresh Token Rotation race | 모바일 이중 발사 → 강제 로그아웃 | § 4.4 Redis Distributed Lock |
| (신규) DELETE body strip | 비밀번호 검증 누락 | § 4.7 POST /me/deactivate로 변경 |
| (신규) OAuth tokeninfo round-trip | 추가 latency + provider 정책 위배 | § 4.8 JWK 직접 검증 |
| (신규) Gateway SSE buffering filter | SSE 스트림 깨짐 | § 9.6 금지 filter 목록 |

---

## 14. 작성 체크리스트 + W1 Lock-in 검증

### 14.1 본 문서 작성 체크리스트

```
[x] § 1  API 설계 정책 + URL 구조 + 버전 관리 + Service Owner + OAS 3.1 호환성 매트릭스 + Slack 채널
[x] § 2  공통 표준 (인증·트레이싱·envelope·ProblemDetail·HTTP code + 503 매핑 책임·도메인 코드 28개·PageResponse<T>·필터·CORS·Rate Limit Lua·멱등성 UX·시간)
[x] § 3  Gateway 라우팅 표 (15+ routes + 필터 체인) — v1.1 변경 마킹
[x] § 4  Auth API 7 endpoints (logout 인증 ❌ + POST /me/deactivate + Refresh race lock + OAuth JWK)
[x] § 5  Bible API 4 endpoints (사설 통합 endpoint 제거 — BFF가 3개 직접)
[x] § 6  AI API 4 endpoints + SSE 7개 event + initialStep schema default + SYSTEM 마스킹 schema + 컨슈머 group
[x] § 7  Journal API 6 endpoints + idempotency_key 자동 생성 + events 02번 정합 + 컨슈머 group
[x] § 8  BFF API 3 endpoints + 4 service 정확화 + activeSession 정책 + epoch_minute 분 경계
[x] § 9  SSE 표준 (Spring Reactor 표준 heartbeat + Flutter 라이브러리 fix + 금지 filter)
[x] § 10 WebSocket 표준 (STOMP CONNECT 헤더 + 알림 type 확장 절차 + Pod 다중 다이어그램 정확화)
[x] § 11 OpenAPI 디렉토리 + 골격 표준 (info.contact 추가) + Spectral 룰 (truthy 함수) + .spectral.yaml 위치
[x] § 12 Prism mock v5+ 가동 + Mock ↔ 실제 일치 검증 (proxy / dredd)
[x] § 13 1차 실패 ↔ API 가드레일 매핑 14개 (1차 5 + MSA 신규 9)
```

### 14.2 W1 Lock-in 항목 #2 검증 (03번 § 2.2)

W1 5/22 금 회고 시 다음 점검:

- [ ] `apis/{service}/openapi.yaml` 5개 모두 존재 (auth/bible/ai/journal/bff)
- [ ] Spectral lint 5개 모두 통과 (CI 그린)
- [ ] **info.contact** 5개 모두 작성 — Spectral `info-contact: error` 통과
- [ ] **모든 4xx/5xx 응답에 `application/problem+json`** 명시 — Spectral `problem-json-on-errors: error` 통과
- [ ] Prism mock v5+ 5 포트 동시 가동 가능 — `prism mock apis/bff/openapi.yaml --port 4015` 응답 200
- [ ] Flutter `dev` 환경에서 BFF mock에 GET /api/v1/me/dashboard 호출 → 본 문서 § 8.2 example 응답 수신
- [ ] **`PageResponse<T>` Custom DTO** 5 service 공통 module에 1개 박제 — Journal·AI 응답 검증
- [ ] 5개 service의 모든 endpoint에 operationId + summary 있음
- [ ] 인증 필요 endpoint는 `security: [{ bearerAuth: [] }]` 명시
- [ ] **WS 인증은 STOMP CONNECT 헤더** — query param token 사용 X (브라우저 dev tools 검증)
- [ ] **Refresh Distributed Lock** — 시뮬레이션: 같은 refresh로 동시 2회 호출 → 1개만 200, 다른 1개는 동일 결과 또는 409

### 14.3 본 문서와 OpenAPI yaml 정합

> **단일 진실 원천:** 본 문서 § 4~8이 정답. `apis/*/openapi.yaml`은 본 문서를 yaml로 변환한 것.
>
> **불일치 발견 시:** ADR 발행 → 본 문서 + yaml 동시 PR + 5명 owner 모두 review.

---

## 📋 v1.0 → v1.1 패치 36항목 요약

**🔴 필수 수정 12개**
1. § 2.6 도메인 에러 코드 표 — 5개 추가 (ACCOUNT_DEACTIVATED·REFRESH_TOKEN_INVALID·OAUTH_TOKEN_INVALID·SESSION_ALREADY_COMPLETED·INVALID_STATUS_TRANSITION)
2. § 2.7 페이지네이션 — Custom `PageResponse<T>` DTO 명시 (Spring Data Page 기본 직렬화 ≠ 04번 정의)
3. § 2.10 Rate Limiter — Spring Cloud Gateway 내장 RedisRateLimiter (Lua) 정확화
4. § 4.5 logout 인증 ❌ — refresh token만 검증 (access 만료 후에도 logout 가능)
5. § 4.7 DELETE body → POST /me/deactivate 변경 (RFC 7231 비표준 회피)
6. § 4.8 OAuth Google — `tokeninfo` → JWK 직접 검증
7. § 5/§ 8 `/passages` 흐름 통일 — BFF가 Bible 3개 endpoint 직접 호출 (사설 통합 제거)
8. § 10.2 WebSocket — query param token → STOMP CONNECT 헤더 (HTTPS여도 위험)
9. § 11.2 yaml 예시 `info.contact` 추가 (자기 룰 위반 해결)
10. § 11.3 Spectral `problem-json-on-errors` 룰 — `function: truthy`로 정정
11. § 11.2 servers URL ↔ § 12.2 포트 일관성 (auth=4011, bible=4012, ai=4013, journal=4014, bff=4015)
12. § 2.5 503 Circuit Breaker — Custom Exception Handler 매핑 책임 명시

**🟡 일관성 보강 12개**
13. § 8.2 dashboard "4 service 정확화" + activeSession "최근 1개" 정책
14. § 4.4 Refresh Rotation — Redis Distributed Lock (race 방지)
15. § 7.4 PATCH idempotency_key — 서버 자동 생성 명시 (`journal.update:{ULID}`)
16. § 6.2 initialStep — OpenAPI schema `default: A` 명시
17. § 3 `/passages` wildcard → 정확 패턴으로 변경
18. § 10.6 Pod 다중 다이어그램 정확화 (Consumer Group + Redis pub/sub dispatch)
19. § 6.4 SYSTEM 턴 — `contentRedacted: true` schema 추가
20. § 9.5 Flutter SSE — `flutter_client_sse: ^2.0.1` (또는 dio_sse) verified 버전
21. § 9.6 SSE 패스스루 — 금지 filter 4개 명시
22. § 9.4 SSE heartbeat — Spring `ServerSentEvent.comment()` 표준 사용
23. § 8.6 BFF Notification 컨슈머 group — `bff-notification-dispatcher-consumer`
24. § 7.7 events 응답 — 02번 § 11.5 event_data 예시와 정합

**🟢 선택적 개선 12개**
25. § 1.4 Slack 채널 (#qtai-api / #qtai-deploy / #qtai-incident) — W0 5/13까지 강태오 생성
26. § 4.2 `PASSWORD_TOO_WEAK` 코드 추가
27. § 6.3 SSE error → end 클라이언트 close 정책 명시
28. § 8.3 멱등성 키 epoch_minute 분 경계 noted
29. § 10.4 알림 type 확장 절차 (4단계 PR atomicity)
30. § 10.2 wss/ws 환경별 명시
31. § 1.1 SpringDoc 자동 생성 안 씀 명시 (Spec-First 강제)
32. § 11.4 `.spectral.yaml` 위치 — 모노레포 루트
33. § 12.5 Mock 검증 도구 — `prism proxy --errors` / `dredd`
34. § 1.1 OAS 3.1 의존성 호환성 매트릭스 (Spectral 6+, Prism 5+, Swagger UI 5+)
35. § 5.2 Hot 100 정의 — 사용자 활동 기반 상위 100구절 + 수동 목록 v1.0
36. § 2.11 Idempotency-Key UX 영향 — Flutter button debounce v1.0, Idempotency-Key 헤더 v1.1 검토

---

> **다음 작성 문서:** `05_보안_명세서.md` — JWT 키 관리·OWASP Top 10·OAuth 흐름·시크릿 운영 절차·NetworkPolicy·Logback masking 룰
