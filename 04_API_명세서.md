# 📖 QT-AI (큐티 AI 앱) — API 명세서 v1.0

> **문서 버전:** v1.0
> **작성일:** 2026-05-06
> **연관 문서:** [01_프로젝트_계획서 v1.3](./01_프로젝트_계획서.md) / [02_ERD_문서 v1.1.1](./02_ERD_문서.md) / [03_아키텍처_정의서 v1.1](./03_아키텍처_정의서.md)
> **W1 Lock-in 산출물:** 본 문서 + `apis/{service}/openapi.yaml` × 5 (Spectral lint 통과 + Prism mock 가동) — 03번 § 2.2
> **목적:** 6명이 W1 종료 시점에 동일한 API 계약 위에서 병렬로 코드를 작성할 수 있도록 모든 endpoint·DTO·에러·페이로드를 박제. 한 번 동결되면 W2 이후 수정은 ADR 발행 + 영향 범위 PR 일괄 동시 머지로만.

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-06 | 강태오 | 초기 작성 — 5 service OpenAPI 골격 + 공통 표준 (헤더·에러·페이징·CORS·Rate Limit) + Gateway 라우팅 표 + SSE/WebSocket 페이로드 + Spectral 룰 + Prism mock 가동 절차 + 1차 실패 패턴 ↔ API 가드레일 매핑 |

---

## 목차

1. [개요 · API 설계 정책](#1-개요--api-설계-정책)
2. [공통 표준 (Cross-cutting Standards)](#2-공통-표준-cross-cutting-standards)
3. [Gateway 라우팅 표](#3-gateway-라우팅-표)
4. [Auth/User Service API](#4-authuser-service-api) — 강상민
5. [Bible Service API](#5-bible-service-api) — 김태혁
6. [AI/RAG Service API](#6-airag-service-api) — 이지윤
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
| **Mock 서버** | Prism — Flutter 작업 unblock 용 (03번 § 2.2) |
| **Spec-First** | OpenAPI yaml 먼저 → 코드 후. yaml 없는 endpoint 머지 차단 |

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
| Auth | `/api/v1/auth/...` | Gateway → Auth Service |
| Bible | `/api/v1/bible/...` | Gateway → Bible Service (직접) 또는 BFF → Bible |
| AI | `/api/v1/ai/...` | Gateway → AI Service |
| Journal | `/api/v1/journals/...` | Gateway → Journal Service |
| BFF (Aggregate) | `/api/v1/me/...`, `/api/v1/passages/...` | Gateway → BFF Aggregator |
| WebSocket | `/ws/...` | Gateway → BFF Aggregator (STOMP) |

> **`/passages` 충돌 주의:** Bible Service 내부에도 `GET /api/v1/passages/{book}/{ch}/{v}` 엔드포인트가 있음 (KR + EN + Commentary 통합용). BFF가 가능하면 그쪽을 호출하는 것이 자연스럽지만, 본 명세 v1.0에서는 **공개 `/api/v1/passages/...`는 BFF 어그리게이션 (KR + EN + Commentary + 사용자 활동 이벤트 발행)**, **Bible 내부 통합 엔드포인트는 BFF에서만 호출하는 사설 형태**로 구분. Gateway 라우팅 표(§ 3)에 명시.

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
| 변경 시 다른 service owner에게 통보 | 본인 (Slack #qtai-api 채널) |
| Breaking change 시 ADR 발행 | 본인 + 강태오 + 영향 받는 owner |

---

## 2. 공통 표준 (Cross-cutting Standards)

### 2.1 인증 헤더

| 헤더 | 값 | 적용 |
| --- | --- | --- |
| `Authorization` | `Bearer {access_token}` | 보호된 엔드포인트 모두 |
| `X-User-Id` | `{user_id}` | **내부 전용**. Gateway가 JWT 검증 후 주입. 외부 클라이언트가 보내면 Gateway가 strip. NetworkPolicy로 외부 spoofing 차단 (03번 § 9.4) |

**인증이 필요 없는 엔드포인트** (`security: []`):
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `POST /api/v1/auth/oauth/google`
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

> **표준:** Spring Boot 3.x ProblemDetail (`application/problem+json`).

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

**필수 확장 필드:**
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

### 2.6 도메인 에러 코드 표 (v1.0)

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
| Auth | `REFRESH_TOKEN_EXPIRED` | 401 | refresh token 만료 |
| Auth | `REFRESH_TOKEN_REVOKED` | 401 | Redis blacklist 차단 |
| Auth | `OAUTH_PROVIDER_ERROR` | 502 | Google OAuth 서버 오류 |
| Bible | `PASSAGE_NOT_FOUND` | 404 | 좌표가 잘못됨 (예: 창세기 100장) |
| Bible | `BOOK_CODE_INVALID` | 400 | 책 코드 잘못됨 |
| AI | `SESSION_NOT_FOUND` | 404 | AI 세션 없음 |
| AI | `SESSION_NOT_OWNED` | 403 | 본인 세션 아님 |
| AI | `LLM_PROVIDER_ERROR` | 502 | Anthropic API 5xx |
| AI | `LLM_TIMEOUT` | 504 | 첫 토큰 timeout |
| AI | `PROMPT_TEMPLATE_NOT_ACTIVE` | 422 | 검수 안 된 프롬프트 |
| Journal | `JOURNAL_NOT_FOUND` | 404 | journal 없음 |
| Journal | `JOURNAL_NOT_OWNED` | 403 | 본인 journal 아님 |
| Journal | `JOURNAL_LOCKED` | 409 | 동시 수정 충돌 (`@Lock(PESSIMISTIC_WRITE)`) |
| Journal | `INVALID_EVENT_SEQUENCE` | 422 | 이벤트 sequence 충돌 |

### 2.7 페이지네이션 표준

**쿼리 파라미터:**
| 이름 | 기본값 | 의미 |
| --- | --- | --- |
| `page` | 0 | 페이지 번호 (0-based) |
| `size` | 20 | 페이지 크기 (max 100) |
| `sort` | `createdAt,desc` | 정렬 (`field,asc`/`desc`, 다중 가능) |

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

> **이유:** Spring Data `Page<T>` 직렬화 결과를 그대로 사용. envelope의 일관성 위배 아님 (collection 응답은 본질적으로 multi-resource).

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

### 2.10 Rate Limiting 정책 (Gateway)

| 대상 | 제한 | 식별자 |
| --- | --- | --- |
| 비로그인 (anonymous) | 60 req/min | client IP |
| ROLE_USER 일반 endpoint | 600 req/min | user_id |
| AI Service `/ai/sessions/*` | 60 req/min, 동시 SSE 3개 | user_id |
| Auth `/auth/login` | 5 req/min | client IP (brute-force 방지) |
| Auth `/auth/register` | 3 req/min | client IP |

**구현:** Spring Cloud Gateway Redis Rate Limiter (Bucket4j). 초과 시 `429 Too Many Requests` + `Retry-After: <seconds>` 헤더.

### 2.11 멱등성 (Idempotency)

| 메서드 | 멱등 |
| --- | --- |
| GET, HEAD, PUT, DELETE | 자동 멱등 (HTTP 표준) |
| POST | 기본 비멱등. 외부 결제·중요 생성은 `Idempotency-Key` 헤더 (v1.1 검토) |

> **v1.0 멱등성 적용 범위:** Kafka 컨슈머만 (DB UNIQUE — ADR-0007). HTTP는 자연 멱등 메서드만 신뢰.

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
| auth-public | `/api/v1/auth/register` | POST | auth-service | ❌ | |
| auth-public | `/api/v1/auth/login` | POST | auth-service | ❌ | Rate 5/min |
| auth-public | `/api/v1/auth/refresh` | POST | auth-service | ❌ | |
| auth-public | `/api/v1/auth/oauth/google` | POST | auth-service | ❌ | |
| auth-private | `/api/v1/auth/logout` | POST | auth-service | ✅ | |
| auth-private | `/api/v1/auth/me` | GET, DELETE | auth-service | ✅ | |
| bible | `/api/v1/bible/**` | GET | bible-service | ✅ | 직접 호출 (단일 자원) |
| bible-aggregate | `/api/v1/passages/**` | GET | **bff-aggregator** | ✅ | 통합 (KR+EN+Comm) |
| commentary | `/api/v1/commentary/**` | GET | bible-service | ✅ | 직접 호출 |
| ai | `/api/v1/ai/sessions` | POST | ai-service | ✅ | |
| ai-sse | `/api/v1/ai/sessions/*/turns` | POST | ai-service | ✅ | **SSE 패스스루** |
| ai | `/api/v1/ai/sessions/*` | GET | ai-service | ✅ | |
| journal | `/api/v1/journals/**` | GET, PATCH, DELETE | journal-service | ✅ | |
| me | `/api/v1/me/**` | GET | bff-aggregator | ✅ | 대시보드 |
| ws | `/ws/**` | WebSocket | bff-aggregator | ✅ | STOMP 패스스루 |
| health | `/actuator/health` | GET | gateway 자체 | ❌ | |

**Gateway 필터 체인:**
```
[전역 Pre 필터]
  1. TraceId 발급/전파 (W3C)
  2. X-User-Id strip (외부에서 들어오면 제거)
  3. JWT 검증 (RS256, 공개키 K8s Secret)
  4. JWT → X-User-Id 헤더 주입 (내부용)
  5. Rate Limit (Redis Bucket4j)

[라우팅]

[전역 Post 필터]
  1. 응답 시간 메트릭
  2. 에러 매핑 (업스트림 5xx → ProblemDetail)
```

---

## 4. Auth/User Service API

> **Owner:** 강상민 / **Base URL:** `http://auth-service.qtai.svc.cluster.local:8080` / **Public:** `https://api.qtai.app/api/v1/auth/...`
>
> **OpenAPI 파일:** `apis/auth/openapi.yaml`

### 4.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 4.2 | POST | `/api/v1/auth/register` | ❌ | 회원가입 |
| 4.3 | POST | `/api/v1/auth/login` | ❌ | 로그인 |
| 4.4 | POST | `/api/v1/auth/refresh` | ❌ | 토큰 갱신 |
| 4.5 | POST | `/api/v1/auth/logout` | ✅ | 로그아웃 (Refresh blacklist) |
| 4.6 | GET | `/api/v1/auth/me` | ✅ | 내 정보 조회 |
| 4.7 | DELETE | `/api/v1/auth/me` | ✅ | 회원 탈퇴 (Soft Delete + email 마스킹) |
| 4.8 | POST | `/api/v1/auth/oauth/google` | ❌ | Google OAuth 로그인 |

### 4.2 POST /api/v1/auth/register

**Request:**
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email":    "user@example.com",
  "password": "P@ssw0rd123",
  "nickname": "홍길동"
}
```

**Validation:**
- `email`: RFC 5321, max 254
- `password`: min 8, max 72 (bcrypt 한계), 영문 + 숫자 + 특수문자 1개 이상
- `nickname`: min 2, max 50

**Response 201 Created:**
```http
HTTP/1.1 201 Created
Location: /api/v1/auth/me
Content-Type: application/json

{
  "id":       5678,
  "email":    "user@example.com",
  "nickname": "홍길동",
  "createdAt": "2026-05-12T03:21:11.456Z"
}
```

**Errors:**
- 400 `VALIDATION_FAILED` — 입력 검증 실패
- 409 `EMAIL_ALREADY_EXISTS` — 활성(`status='ACTIVE'`) 사용자 중 동일 이메일 존재 (탈퇴된 사용자는 마스킹되어 충돌 안 남 — 02번 § 2.2.1)

### 4.3 POST /api/v1/auth/login

**Request:**
```http
POST /api/v1/auth/login
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

### 4.4 POST /api/v1/auth/refresh

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

**처리 시퀀스 (03번 § 11.3):**
1. JWT 서명·만료 검증
2. `token_hash` DB 조회 → 존재·활성 확인
3. **Redis-WS** `auth:refresh:revoked:{jti}` 조회 → 없어야 통과
4. Token Rotation: 기존 토큰 `revoked_at` UPDATE + Redis blacklist 추가 (TTL = refresh 만료까지)
5. 새 Access + Refresh 발급

**Errors:**
- 401 `REFRESH_TOKEN_EXPIRED`
- 401 `REFRESH_TOKEN_REVOKED` — Redis blacklist
- 401 `REFRESH_TOKEN_INVALID` — 서명·구조 오류

### 4.5 POST /api/v1/auth/logout

**Request:**
```http
POST /api/v1/auth/logout
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "refreshToken": "eyJ..."
}
```

**Response 204 No Content**

**처리:**
- Access Token: 만료(30분)까지 그대로 유효 — blacklist 없음 (단명이라 위험 낮음)
- Refresh Token: DB `revoked_at` UPDATE + Redis-WS `auth:refresh:revoked:{jti}` 등록

### 4.6 GET /api/v1/auth/me

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

### 4.7 DELETE /api/v1/auth/me — 회원 탈퇴

**Request:**
```http
DELETE /api/v1/auth/me
Authorization: Bearer {accessToken}
Content-Type: application/json

{
  "password": "P@ssw0rd123"     // 비밀번호 재확인 (소셜 전용은 confirmText 대체)
}
```

**Response 204 No Content**

**처리 시퀀스 (TX 안):**
1. bcrypt 검증
2. `USERS.status = 'DEACTIVATED'`
3. `USERS.deleted_at = NOW()`
4. `USERS.email = 'u_{id}_deactivated_{epoch_ms}@deleted.local'` (마스킹 — 02번 § 2.2.1)
5. `REFRESH_TOKENS` 모두 `revoked_at` UPDATE
6. **AFTER_COMMIT** → Kafka publish `user.deactivated` (멱등성 키: `user.deactivated:{user_id}`)
7. AI Service 컨슈머 → 활성 세션 정리
8. Journal Service 컨슈머 → 데이터 처리 정책에 따라 (v1.0은 보존, v1.1 GDPR 검토)

### 4.8 POST /api/v1/auth/oauth/google

**Request:**
```json
{
  "idToken": "eyJ... (Google ID Token)"
}
```

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

**처리:**
1. Google `tokeninfo` endpoint로 ID Token 검증
2. `OAUTH_LINKS`에서 (provider, provider_user_id) 조회
3. 매치되면 → 로그인. 없으면 → 새 USERS 생성 + OAUTH_LINKS 추가

**Errors:**
- 401 `OAUTH_TOKEN_INVALID`
- 502 `OAUTH_PROVIDER_ERROR`

### 4.9 발행하는 Kafka 이벤트

| 이벤트 | 토픽 | 시점 |
| --- | --- | --- |
| `user.deactivated` | `user.deactivated` | DELETE /me 성공 (AFTER_COMMIT) |

---

## 5. Bible Service API

> **Owner:** 김태혁 / **Base URL:** `http://bible-service.qtai.svc.cluster.local:8080`
>
> **OpenAPI 파일:** `apis/bible/openapi.yaml`

### 5.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 5.2 | GET | `/api/v1/bible/kr/{bookCode}/{chapter}/{verse}` | ✅ | 한국어 (개역한글) |
| 5.3 | GET | `/api/v1/bible/en/{bookCode}/{chapter}/{verse}` | ✅ | 영어 (KJV PD) |
| 5.4 | GET | `/api/v1/commentary/{bookCode}/{chapter}/{verse}` | ✅ | 주석 (Matthew Henry PD + 더미한글) |
| 5.5 | GET | `/api/v1/passages/{bookCode}/{chapter}/{verse}` | ✅ | **사설 통합** — BFF에서만 호출 |
| 5.6 | GET | `/api/v1/bible/books` | ✅ | 책 목록 조회 (66권) |

> § 5.5는 BFF Aggregator의 공개 `/api/v1/passages/...`(§ 8.3)와 다름. 본 endpoint는 Bible Service 내부 통합 — BFF가 호출. Gateway는 외부에서 본 엔드포인트로 직접 라우팅 X.

### 5.2 GET /api/v1/bible/kr/{bookCode}/{chapter}/{verse}

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

**캐시:** Redis-Cache `cache:passage:kr:{bookCode}:{ch}:{v}` TTL 24h. Hot 100 별도.

### 5.3 GET /api/v1/bible/en/{bookCode}/{chapter}/{verse}

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

### 5.5 GET /api/v1/passages/{bookCode}/{chapter}/{verse}  (사설)

> **호출자:** BFF Aggregator만. 직접 외부 호출 차단 (Gateway 라우트 없음).

**Response 200 OK:**
```json
{
  "passage": {
    "bookCode": "GEN",
    "chapter":  1,
    "verse":    1
  },
  "kr": { ... 5.2 응답 본문 ... },
  "en": { ... 5.3 응답 본문 ... },
  "commentaries": [ ... 5.4 응답의 items ... ]
}
```

**구현:** Bible Service 내부에서 3개 query 병렬. Redis 캐시 활용 (각각 cache hit/miss).

### 5.6 GET /api/v1/bible/books

**Response 200 OK:**
```json
{
  "items": [
    { "code": "GEN", "nameKr": "창세기",   "nameEn": "Genesis",  "chapters": 50 },
    { "code": "EXO", "nameKr": "출애굽기", "nameEn": "Exodus",   "chapters": 40 },
    ...
  ]
}
```

> 정적 데이터 — 응답 캐시 24h. 페이지네이션 없음 (66권 고정).

### 5.7 발행하는 Kafka 이벤트

> **없음.** Bible Service는 정적 데이터 — 변경 이벤트 발행 X.

---

## 6. AI/RAG Service API

> **Owner:** 이지윤 / **Base URL:** `http://ai-service.qtai.svc.cluster.local:8080`
>
> **OpenAPI 파일:** `apis/ai/openapi.yaml`

### 6.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 6.2 | POST | `/api/v1/ai/sessions` | ✅ | 세션 시작 |
| 6.3 | POST | `/api/v1/ai/sessions/{id}/turns` | ✅ | 대화 턴 추가 (**SSE 스트리밍**) |
| 6.4 | GET | `/api/v1/ai/sessions/{id}` | ✅ | 세션 + 턴 조회 |
| 6.5 | GET | `/api/v1/ai/sessions` | ✅ | 본인 세션 목록 (페이지네이션) |

### 6.2 POST /api/v1/ai/sessions

**Request:**
```json
{
  "passage": {
    "bookCode": "GEN",
    "chapter":  1,
    "verse":    1
  },
  "initialStep": "A"     // A/B/C/D — 시작 단계, default "A"
}
```

**Response 201 Created:**
```http
HTTP/1.1 201 Created
Location: /api/v1/ai/sessions/9012
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

### 6.3 POST /api/v1/ai/sessions/{id}/turns — SSE 스트리밍

**Request:**
```http
POST /api/v1/ai/sessions/9012/turns
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
- `end` — 스트림 종료
- `error` — 에러 (스트림 도중 발생 가능)

**SSE 종료 정책 (03번 § 1.3.2):**
- 첫 토큰 timeout: 5s
- 토큰 간 idle timeout: 30s
- 전체 max: 5분
- 클라이언트 연결 끊김 → `Flux.doFinally(SignalType.CANCEL)` → Anthropic 호출 즉시 중단 (토큰 비용 절약)

**Errors (스트림 시작 전):**
- 404 `SESSION_NOT_FOUND`
- 403 `SESSION_NOT_OWNED`
- 422 `SESSION_ALREADY_COMPLETED`
- 422 `PROMPT_TEMPLATE_NOT_ACTIVE`
- 502 `LLM_PROVIDER_ERROR`
- 504 `LLM_TIMEOUT`

**Errors (스트림 도중):**
```
event: error
data: {"code": "LLM_PROVIDER_ERROR", "detail": "Anthropic API 503 after 3 retries", "traceId": "..."}

event: end
data: [DONE]
```

### 6.4 GET /api/v1/ai/sessions/{id}

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
      "content":          "(system prompt — 마스킹: 'REDACTED' 또는 빈 문자열)",
      "createdAt":        "2026-05-26T14:30:00.150Z"
    },
    {
      "id":               32,
      "role":             "USER",
      "step":             "A",
      "content":          "하나님이 천지를 창조하셨다는 게 어떤 의미인가요?",
      "createdAt":        "2026-05-26T14:30:01.000Z"
    },
    {
      "id":               33,
      "role":             "ASSISTANT",
      "step":             "A",
      "content":          "이 구절은 창조의 첫 행위를 선언합니다...",
      "promptTemplateId": 7,
      "ragSources":       [ {"type":"commentary","id":11,"weight":0.82}, ... ],
      "createdAt":        "2026-05-26T14:30:05.123Z"
    }
  ]
}
```

> **금지:** SYSTEM 턴의 `content` 본문 노출 X. 클라이언트는 SYSTEM 턴 자체를 안 보여줘도 됨 (응답에는 포함하되 `"content": ""` 또는 응답에서 필터링).

### 6.5 GET /api/v1/ai/sessions

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
    },
    ...
  ],
  "page": { "number": 0, "size": 20, "totalElements": 12, "totalPages": 1 }
}
```

> 본인 세션만 조회. user_id는 X-User-Id 헤더로 자동 필터링.

### 6.6 발행하는 Kafka 이벤트

| 이벤트 | 토픽 | 시점 | 멱등성 키 |
| --- | --- | --- | --- |
| `ai.session.completed` | `ai.session.completed` | D 단계 도달 시 (AFTER_COMMIT) | `ai.session.completed:{session_id}` |

### 6.7 컨슈머 토픽

| 토픽 | 동작 |
| --- | --- |
| `user.deactivated` | 해당 user의 IN_PROGRESS 세션 → status=ABANDONED 마킹 |

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
    },
    ...
  ],
  "page": { ... }
}
```

> **본인 journal만** (X-User-Id 자동 필터). soft-deleted (`deleted_at IS NOT NULL`)는 기본 제외.

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
  "title":   "태초의 묵상 (수정)",      // 선택
  "content": "수정된 내용",             // 선택
  "status":  "PUBLISHED"               // 선택 (DRAFT → PUBLISHED 전환)
}
```

> **변경 가능 필드:** `title`, `content`, `status` (DRAFT ↔ PUBLISHED). 다른 필드는 무시.

**Response 200 OK:**
```json
{
  "id":           12345,
  "title":        "태초의 묵상 (수정)",
  "content":      "수정된 내용",
  "status":       "PUBLISHED",
  "lastEventSequence": 5,         // +1 (UPDATED 또는 PUBLISHED 이벤트 적재)
  "updatedAt":    "2026-05-26T16:00:00Z"
}
```

**처리 시퀀스 (03번 § 5.4):**
1. TX 시작
2. JOURNALS row 잠금 (`@Lock(PESSIMISTIC_WRITE)` — `findByIdLocked`)
3. `last_event_sequence + 1`
4. JOURNAL_EVENTS INSERT (eventType=`UPDATED` 또는 `PUBLISHED`, `idempotency_key UNIQUE`, `(journal_id, sequence) UNIQUE`)
5. JOURNALS read model 갱신
6. TX 커밋
7. **AFTER_COMMIT** → KafkaTemplate `journal.updated` (또는 `journal.created`/`journal.published`)

**Errors:**
- 404 `JOURNAL_NOT_FOUND`
- 403 `JOURNAL_NOT_OWNED`
- 409 `JOURNAL_LOCKED` — 동시 수정 충돌
- 422 `INVALID_STATUS_TRANSITION` — 예: PUBLISHED → DRAFT 금지
- 422 `INVALID_EVENT_SEQUENCE` — UNIQUE 위반 (멱등성 차단)

### 7.5 DELETE /api/v1/journals/{id}

**Response 204 No Content**

**처리 (Soft Delete):**
1. TX 시작
2. `JOURNALS.deleted_at = NOW()`, `last_event_sequence + 1`
3. JOURNAL_EVENTS INSERT (eventType=`DELETED`)
4. TX 커밋
5. **AFTER_COMMIT** → Kafka `journal.deleted`

**Errors:**
- 404 `JOURNAL_NOT_FOUND`
- 403 `JOURNAL_NOT_OWNED`

### 7.6 POST /api/v1/journals/{id}/restore (v1.1)

> v1.0 미구현. v1.1 ADR-0006 후속 작업.

### 7.7 GET /api/v1/journals/{id}/events

> 감사 목적. 본인 journal의 모든 이벤트 (CREATED → UPDATED → ... → DELETED) 시퀀스 조회.

**Response 200 OK:**
```json
{
  "journalId": 12345,
  "events": [
    {
      "id":              101,
      "sequence":        1,
      "eventType":       "CREATED",
      "eventData":       { "title": "...", "content": "...", "aiSessionId": 9012 },
      "idempotencyKey":  "ai.session.completed:9012",
      "createdAt":       "2026-05-26T14:45:00Z"
    },
    {
      "id":              102,
      "sequence":        2,
      "eventType":       "UPDATED",
      "eventData":       { "title": "(updated)" },
      "idempotencyKey":  "user.update:abc123",
      "createdAt":       "2026-05-26T15:00:00Z"
    },
    ...
  ]
}
```

### 7.8 발행하는 Kafka 이벤트

| 이벤트 | 토픽 | 시점 | 멱등성 키 |
| --- | --- | --- | --- |
| `journal.created` | `journal.created` | AI 세션 컨슈머가 DRAFT 생성 시 (AFTER_COMMIT) | `ai.session.completed:{session_id}` |
| `journal.updated` | `journal.updated` | PATCH (AFTER_COMMIT) | `journal.update:{ulid}` |
| `journal.deleted` | `journal.deleted` | DELETE (AFTER_COMMIT) | `journal.delete:{journal_id}:{epoch}` |

### 7.9 컨슈머 토픽

| 토픽 | 동작 |
| --- | --- |
| `ai.session.completed` | DRAFT Journal + JOURNAL_EVENTS (CREATED) 적재 (멱등성 키 `ai.session.completed:{session_id}`) |
| `user.activity.tracked` | (v1.1) 통계 적재 또는 활동 history. v1.0 무시. |
| `user.deactivated` | (v1.0 보존, v1.1 GDPR 검토) |

---

## 8. BFF Aggregator API

> **Owner:** 강태오 / **Base URL:** `http://bff-aggregator.qtai.svc.cluster.local:8080`
>
> **OpenAPI 파일:** `apis/bff/openapi.yaml`

### 8.1 Endpoint 요약

| # | Method | Path | 인증 | 설명 |
| --- | --- | --- | --- | --- |
| 8.2 | GET | `/api/v1/me/dashboard` | ✅ | 통합 대시보드 |
| 8.3 | GET | `/api/v1/passages/{bookCode}/{chapter}/{verse}` | ✅ | 입체 묵상 화면 (KR + EN + Commentary) |
| 8.4 | WS | `/ws/notifications` | ✅ | 실시간 알림 (STOMP) |

### 8.2 GET /api/v1/me/dashboard

**처리:** 5 service 병렬 호출 후 어그리게이션.

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
    { "id": 12345, "title": "태초의 묵상", "status": "PUBLISHED", "createdAt": "..." },
    ...    /* 최근 5개 */
  ],
  "activeSession": null    /* 또는 진행 중인 AI 세션 1개 */
}
```

**구현:** UseCase 1개 (`GetDashboardUseCase`) — 5 future 병렬 (`CompletableFuture.allOf`).

### 8.3 GET /api/v1/passages/{bookCode}/{chapter}/{verse}

**처리:** 03번 § 1.3.1 시나리오 1.

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
- 멱등성 키: `read.passage:{user_id}:{book}:{ch}:{v}:{epoch_minute}` (분 단위 dedup)

### 8.4 WS /ws/notifications — STOMP WebSocket

> § 10 (WebSocket 표준) 참조.

### 8.5 발행하는 Kafka 이벤트

| 이벤트 | 토픽 | 시점 |
| --- | --- | --- |
| `user.activity.tracked` | `user.activity.tracked` | GET /passages/... 호출 시 (Best-effort) |

### 8.6 컨슈머 토픽

| 토픽 | 동작 |
| --- | --- |
| `notification.requested` | Redis-WS 활성 세션 조회 → STOMP push (활성 시) / 폐기 (비활성 시) |
| `journal.created` | (선택 v1.1) 알림 |

---

## 9. SSE (Server-Sent Events) 표준

### 9.1 사용처

| Endpoint | 용도 |
| --- | --- |
| `POST /api/v1/ai/sessions/{id}/turns` | AI 응답 토큰 스트리밍 (§ 6.3) |

### 9.2 Event 종류 (§ 6.3 상세)

| Event | data 페이로드 | 빈도 | 의미 |
| --- | --- | --- | --- |
| `turn_started` | `{ "turnId": null, "step": "A", "timestamp": "..." }` | 1회 | 턴 처리 시작 (DB 적재 전 → turnId null) |
| `token` | `{ "text": "..." }` | N회 | LLM 토큰 (1~수백) |
| `step_changed` | `{ "from": "A", "to": "B" }` | 0~1회 | 단계 전환 감지 |
| `rag_sources` | `{ "sources": [{ "type": ..., "id": ..., "weight": ... }] }` | 1회 | **ASSISTANT 턴마다 필수** (신학 가드레일) |
| `turn_completed` | `{ "turnId": 33, "step": "A", "promptTemplateId": 7, "totalTokens": 245, "elapsedMs": 4123 }` | 1회 | DB 적재 완료 후 |
| `error` | `{ "code": "...", "detail": "...", "traceId": "..." }` | 0~1회 | 도중 에러 |
| `end` | `[DONE]` | 1회 (마지막) | 스트림 종료 신호 |

### 9.3 헤더 / 응답 표준

```http
Content-Type: text/event-stream; charset=utf-8
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

### 9.4 Timeout / 종료 정책

| 항목 | 값 |
| --- | --- |
| 첫 토큰 timeout | 5s (이후 504 `LLM_TIMEOUT`) |
| 토큰 간 idle timeout | 30s |
| 전체 max | 5분 |
| heartbeat (idle 시) | 15s마다 `:keep-alive\n\n` 주석 라인 |
| 클라이언트 끊김 | `Flux.doFinally(SignalType.CANCEL)` → Anthropic 호출 즉시 dispose |

### 9.5 Flutter 구현 표준

```dart
// pubspec.yaml
dependencies:
  dio: ^5.x
  dio_sse: ^x.y.z   // 또는 flutter_client_sse

// 사용 예
final controller = SseController(
  url: 'https://api.qtai.app/api/v1/ai/sessions/$id/turns',
  headers: { 'Authorization': 'Bearer $accessToken', 'Accept': 'text/event-stream' },
  body: jsonEncode({ 'userMessage': msg }),
);

controller.stream.listen((event) {
  switch (event.event) {
    case 'token':       /* 텍스트 누적 */
    case 'rag_sources': /* 출처 표시 */
    case 'turn_completed': /* 입력창 다시 활성 */
    case 'error':       /* SnackBar */
    case 'end':         controller.close();
  }
});

// 화면 dispose 시 controller.close() 필수 — 서버 SSE cancel 트리거
```

### 9.6 Gateway 패스스루 표준

```yaml
# Spring Cloud Gateway
spring:
  cloud:
    gateway:
      routes:
        - id: ai-sse
          uri: http://ai-service:8080
          predicates:
            - Path=/api/v1/ai/sessions/*/turns
            - Method=POST
          filters:
            - PreserveHostHeader
            # SSE 패스스루용: 응답 버퍼링 비활성
            - SetResponseHeader=X-Accel-Buffering, no
```

---

## 10. WebSocket (STOMP) 표준

### 10.1 사용처

| Endpoint | 용도 |
| --- | --- |
| `WS /ws/notifications` | 서버 → 클라이언트 실시간 알림 (BFF Aggregator) |

### 10.2 핸드셰이크 + 인증

```
[클라이언트] WS connect: wss://api.qtai.app/ws/notifications?token={accessToken}
[Gateway]  → JWT 검증 (RS256) → BFF Aggregator로 패스스루
[BFF]      STOMP CONNECT 프레임 수신 → Redis-WS 등록
                                        SADD ws:session:{user_id} {session_id}
                                        SET  ws:session:{session_id}:meta {...}
```

> **인증 방식:** Subprotocol 또는 첫 STOMP CONNECT 프레임 헤더에 `Authorization: Bearer ...` 권장. v1.0은 단순화 위해 query param 허용 (HTTPS이라 평문 노출 위험은 낮음). v1.1에 `Sec-WebSocket-Protocol: bearer.{token}` 권장으로 변경 검토.

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

### 10.4 알림 type 표 (v1.0)

| type | 트리거 | 페이로드 metadata |
| --- | --- | --- |
| `JOURNAL_AI_DRAFT_READY` | AI 세션 완료 → Journal DRAFT 생성 | `journalId`, `aiSessionId` |
| `JOURNAL_PUBLISHED` | (선택) 본인 journal published | `journalId` |
| `STREAK_MILESTONE` | (v1.1) 연속 묵상 달성 | `streak` |

### 10.5 Ping / 재연결

| 항목 | 값 |
| --- | --- |
| Heartbeat (서버 → 클라이언트) | 30s |
| Heartbeat (클라이언트 → 서버) | 30s |
| 재연결 backoff | exponential 1s → max 30s |
| 재연결 후 미수신 알림 | v1.0 받지 못함 (stateless WS — ADR-0012). v1.1에 NOTIFICATION_LOG 도입 후 미수신 동기화 |

### 10.6 Pod 다중 인스턴스 처리 (Redis-WS pub/sub)

```
Producer Service ─Kafka publish─▶ notification.requested
                                        │
                                        ▼
                  BFF Pod-A 또는 Pod-B 컨슈머 (다른 instance도 수신 가능)
                                        │
                            Redis-WS에서 SMEMBERS ws:session:{user_id} 조회
                                        │
                  ┌───────────────────┐ │ ┌───────────────────┐
                  ▼                   ▼ │ ▼                   ▼
            Pod-A에 있는           Redis-WS pub/sub: ws:notify:{user_id}
            세션이라면 직접 push   Pod-B는 자기에 있는 세션이면 push
```

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

### 11.2 OpenAPI 골격 표준 (예: auth)

```yaml
openapi: 3.1.0
info:
  title: QT-AI Auth Service
  version: 1.0.0
  description: |
    회원·JWT·OAuth Service.
    Owner: 강상민
servers:
  - url: https://api.qtai.app
    description: Production (via Gateway)
  - url: http://localhost:4010
    description: Local Prism mock

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
  /api/v1/auth/login:
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

### 11.3 Spectral 룰 (`.spectral.yaml`)

```yaml
extends:
  - "spectral:oas"
rules:
  # 모든 endpoint operationId 필수
  operation-operationId: error

  # 모든 endpoint summary 필수
  operation-description: warn
  operation-summary: error

  # 모든 4xx/5xx 응답에 ProblemDetail 사용 (custom rule)
  problem-json-on-errors:
    description: 4xx/5xx 응답은 application/problem+json + ProblemDetail 사용
    severity: error
    given: $.paths[*][*].responses[?(@property.match(/^[45]/))]
    then:
      field: content
      function: schema
      functionOptions:
        schema:
          type: object
          required: ["application/problem+json"]

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

### 11.4 PR 머지 게이트 (03번 § 10.3 정합)

```yaml
# .github/workflows/ci.yml — lint job 안에
- name: Spectral OpenAPI lint
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
# 5개 service 동시 가동 (각자 다른 포트)
npm install -g @stoplight/prism-cli

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

### 12.5 W1 일정 (03번 § 2.6)

| 요일 | 산출물 |
| --- | --- |
| 월 5/18 | OpenAPI 골격 5개 작성 (operationId만) |
| 화 5/19 | request·response schema + example 작성 → **Spectral lint 통과** |
| 화 5/19 ~ | Prism mock 5포트 가동 → Flutter `dev` 환경 연결 → 김지민 코딩 시작 |
| 금 5/22 | Mock ↔ 실제 백엔드 1개 service 응답 일치 검증 (강태오 + 1명) |

---

## 13. 1차(HMS) 실패 패턴 ↔ API 가드레일

| 1차 실패 | MSA에서 증폭 | 본 문서 가드레일 |
| --- | --- | --- |
| API 응답 일관성 부재 (envelope 혼용) | 5 service × envelope 종류 → 클라이언트 분기 폭증 | § 2.3 envelope 사용 안 함 + § 2.4 ProblemDetail 표준화 |
| 에러 응답 형식 제각각 | 5 service × 에러 형식 환각 | § 2.4 RFC 7807 ProblemDetail + § 2.6 도메인 코드 표 + Spectral 룰로 강제 |
| HTTP status 잘못 사용 (200 + success:false) | 5 service × status 잘못 | § 2.5 표 + 머지 리뷰 체크 |
| 인증 헤더 직접 검증 누락 | 5 service × 인증 누락 가능 | § 2.1 Gateway 단일 검증 + § 3 라우팅 표 + ADR-0012 |
| 페이지네이션 형식 제각각 | 5 service × 다른 응답 | § 2.7 Spring Data Page 표준 |
| (신규) **OpenAPI 없는 endpoint 머지** | 클라이언트와 어긋남 | § 11.4 Spectral 룰 + PR 머지 게이트 |
| (신규) **breaking change 무통보** | 클라이언트 깨짐 | § 1.3 v2 분기 정책 + ADR 발행 |
| (신규) SSE timeout 미설정 → 영원히 hang | LLM 비용 폭증 + 사용자 경험 ↓ | § 9.4 timeout 표 + `Flux.doFinally(CANCEL)` |
| (신규) WebSocket 인증 누락 | 다른 사용자에게 알림 누출 | § 10.2 Gateway JWT 검증 + Redis-WS user_id 격리 |
| (신규) Rate limit 없어 brute-force | login 무차별 시도 | § 2.10 endpoint별 표 — login 5/min |

---

## 14. 작성 체크리스트 + W1 Lock-in 검증

### 14.1 본 문서 작성 체크리스트

```
[x] § 1  API 설계 정책 + URL 구조 + 버전 관리 + Service Owner
[x] § 2  공통 표준 (인증·트레이싱·envelope·ProblemDetail·HTTP code·도메인 코드·페이지네이션·필터·CORS·Rate Limit·멱등성·시간)
[x] § 3  Gateway 라우팅 표 (15 routes + 필터 체인)
[x] § 4  Auth API 8 endpoints + Kafka 발행
[x] § 5  Bible API 5 endpoints (사설 통합 분리)
[x] § 6  AI API 4 endpoints + SSE 7개 event + 컨슈머
[x] § 7  Journal API 6 endpoints (POST 없음 명시) + 이벤트 소싱 시퀀스 + Kafka 발행/컨슈머
[x] § 8  BFF API 3 endpoints + WebSocket
[x] § 9  SSE 표준 (event 표 + timeout + Flutter 구현 + Gateway 패스스루)
[x] § 10 WebSocket 표준 (STOMP + 인증 + 타입 표 + Pod 다중)
[x] § 11 OpenAPI 디렉토리 + 골격 표준 (auth 예시) + Spectral 룰 + 머지 게이트
[x] § 12 Prism mock 가동 절차 + W1 일정
[x] § 13 1차 실패 ↔ API 가드레일 매핑
```

### 14.2 W1 Lock-in 항목 #2 검증 (03번 § 2.2)

W1 5/22 금 회고 시 다음 점검:

- [ ] `apis/{service}/openapi.yaml` 5개 모두 존재 (auth/bible/ai/journal/bff)
- [ ] Spectral lint 5개 모두 통과 (CI 그린)
- [ ] Prism mock 5 포트 동시 가동 가능 — `prism mock apis/bff/openapi.yaml --port 4015` 응답 200
- [ ] Flutter `dev` 환경에서 BFF mock에 GET /api/v1/me/dashboard 호출 → 본 문서 § 8.2 example 응답 수신
- [ ] 5개 service의 모든 4xx/5xx 응답에 ProblemDetail (`application/problem+json`) 사용
- [ ] 5개 service의 모든 endpoint에 operationId + summary 있음
- [ ] 인증 필요 endpoint는 `security: [{ bearerAuth: [] }]` 명시

### 14.3 본 문서와 OpenAPI yaml 정합

> **단일 진실 원천:** 본 문서 § 4~8이 정답. `apis/*/openapi.yaml`은 본 문서를 yaml로 변환한 것.
>
> **불일치 발견 시:** ADR 발행 → 본 문서 + yaml 동시 PR + 5명 owner 모두 review.

---

> **다음 작성 문서:** `05_보안_명세서.md` — JWT 키 관리·OWASP Top 10·OAuth 흐름·시크릿 운영 절차·NetworkPolicy·Logback masking 룰
