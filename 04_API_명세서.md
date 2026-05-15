# API 명세서 — QT-AI v2.3 기준

> **문서 버전:** v0.2
> **작성일:** 2026-05-15
> **기준 문서:** `07_요구사항_정의서.md` v2.3
> **문서 역할:** 외부 공개 HTTP API와 내부 Java Interface 계약 관리
> **연관 문서:** `00_문서_역할_분리표.md`, `01_프로젝트_계획서.md`, `02_ERD_문서.md`, `03_아키텍처_정의서.md`, `07_요구사항_정의서.md`, `05_시퀀스_다이어그램.md`, `06_화면_기능_정의서.md`, `18_코드_품질_게이트.md`, `22_구현_저장소_반영_체크리스트.md`, `23_도메인_용어사전.md`, `25_기능_명세서.md`

---

## 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v0.1 | 2026-05-15 | Codex | `07_요구사항_정의서.md` v2.3 기준으로 API 명세서 초안 작성 |
| v0.2 | 2026-05-15 | Codex | Today QT 캐시 상태 필드, 인증 API, 묵상·익명 나눔 API, 찬양 상세 응답, 관리자 API 상세 보강 |

---

## 1. 문서 목적과 경계

이 문서는 QT-AI v1의 API 계약을 정의한다.

외부 공개 API는 Flutter 앱, 관리자 화면, 외부 클라이언트가 호출하는 HTTP API다. 내부 도메인 인터페이스는 단일 `qtai-server` Modular Monolith 내부에서 도메인 간 호출에 사용하는 Java Interface다.

| 구분 | 이 문서에서 관리 | 다른 문서에서 관리 |
| --- | --- | --- |
| 외부 공개 API | `/api/v1/**` 경로, 메서드, 권한, 요청/응답 요약 | 기능 요구사항 원본은 `07_요구사항_정의서.md` |
| 내부 도메인 인터페이스 | Port 이름, 호출 주체, 제공 도메인, 목적 | 도메인 경계 상세는 `03_아키텍처_정의서.md` |
| 에러 응답 | 공통 에러 포맷, 주요 상태 코드 | 품질 검증은 `18_코드_품질_게이트.md` |
| 금지 API | 사용자용 AI Q&A, SSE, 교회 인증 API 제외 기준 | 제외 근거는 `07_요구사항_정의서.md` |

문서 간 충돌이 발생하면 기능 포함 여부와 사용자 노출 기준은 `07_요구사항_정의서.md` v2.3을 우선한다.

---

## 2. API 설계 원칙

| 원칙 | 기준 |
| --- | --- |
| 기본 prefix | 모든 외부 공개 API는 `/api/v1`로 시작한다. |
| 응답 형식 | JSON을 기본으로 한다. |
| 인증 | `PUBLIC` API는 비로그인 접근을 허용하고, 로그인 사용자 API는 `USER`, 관리자 API는 `ADMIN` 권한을 요구한다. |
| 시스템 작업 | 배치/AI 내부 작업은 사용자 API가 아니라 `SYSTEM` 작업으로 기록한다. |
| 사용자 요청 경로 LLM 금지 | 외부 공개 API 처리 중 LLM을 직접 호출하지 않는다. |
| 내부 인터페이스 분리 | 도메인 간 호출은 HTTP가 아니라 Java Interface와 DTO로 수행한다. |
| A 테이블 보호 | 최신 한국어 주석 A 테이블은 사용자 API에 노출하지 않는다. |
| 시뮬레이터 상태 | 오늘 QT와 시뮬레이터 조회 API는 `READY`, `MISSING`, `FAILED`, `DISABLED` 상태를 사용한다. |
| 캐시 상태 표현 | Today QT 응답은 `cache` 객체로 캐시 적중·이전 캐시 제공·다음 갱신 시각을 명시한다. |
| 교회 인증 제외 | 회원가입·로그인·마이페이지·관리자 API 어디에도 교회 인증 경로를 만들지 않는다. |

---

## 3. 공통 규격

### 3.1 인증 헤더

| 항목 | 값 |
| --- | --- |
| Header | `Authorization: Bearer {accessToken}` |
| 인증 방식 | JWT |
| 공개 접근 | `PUBLIC` API는 헤더 없이 호출 가능 |
| 일반 사용자 권한 | `USER` |
| 관리자 권한 | `ADMIN` |
| 시스템 작업 | HTTP 사용자 API가 아니라 내부 배치/관리자 트리거로 수행 |

### 3.2 공통 에러 응답

```json
{
  "timestamp": "2026-05-15T09:00:00+09:00",
  "status": 400,
  "code": "VALIDATION_ERROR",
  "message": "요청 값이 올바르지 않습니다.",
  "path": "/api/v1/journals",
  "traceId": "trace-id"
}
```

| HTTP Status | code 예시 | 의미 |
| --- | --- | --- |
| 400 | `VALIDATION_ERROR` | 요청 파라미터 또는 본문 검증 실패 |
| 401 | `UNAUTHORIZED` | 인증 없음 또는 토큰 오류 |
| 403 | `FORBIDDEN` | 권한 부족 |
| 404 | `NOT_FOUND` | 대상 리소스 없음 |
| 409 | `CONFLICT` | 상태 충돌 또는 중복 요청 |
| 429 | `RATE_LIMITED` | 요청 제한 초과 |
| 500 | `INTERNAL_ERROR` | 서버 내부 오류 |

### 3.3 페이징 응답

목록 조회 API는 필요 시 아래 형식을 사용한다.

```json
{
  "items": [],
  "page": 0,
  "size": 20,
  "totalElements": 0,
  "totalPages": 0,
  "hasNext": false
}
```

### 3.4 캐시 상태 공통 필드

Today QT처럼 캐시 정책이 사용자 경험에 영향을 주는 API는 응답에 `cache` 객체를 포함한다.

```json
{
  "cache": {
    "cacheStatus": "HIT",
    "source": "CACHE",
    "servedQtDate": "2026-05-15",
    "refreshedAt": "2026-05-15T04:18:00+09:00",
    "expiresAt": "2026-05-16T04:00:00+09:00",
    "nextRefreshAt": "2026-05-16T04:00:00+09:00",
    "staleReason": null
  }
}
```

| 필드 | 값 |
| --- | --- |
| `cacheStatus` | `HIT`, `MISS`, `STALE_FALLBACK`, `EMPTY` |
| `source` | `CACHE`, `DB_FALLBACK` |
| `servedQtDate` | 실제 응답에 실린 QT 콘텐츠 날짜. 00:00~04:00 KST에는 전날 날짜일 수 있다. |
| `staleReason` | `BEFORE_COLLECTION_WINDOW`, `COLLECTION_FAILED`, `CACHE_REFRESH_FAILED`, `NO_CACHE` 중 하나 또는 `null` |

`STALE_FALLBACK`은 장애가 아니라 의도된 이전 캐시 제공 상태일 수 있다. 00:00~04:00 KST 구간에는 성서 유니온 새 본문 공개와 우리 시스템 04:00 수집 배치 사이의 정책상 이전 캐시를 유지한다.

---

## 4. 외부 공개 API 목록

| 기능 | Method | Path | 권한 | 담당 도메인 |
| --- | --- | --- | --- | --- |
| Google 로그인 URL 조회 | GET | `/api/v1/auth/google/authorize` | `PUBLIC` | gatewayauth |
| Google 로그인 토큰 교환 | POST | `/api/v1/auth/google/token` | `PUBLIC` | gatewayauth |
| Access Token 재발급 | POST | `/api/v1/auth/refresh` | `PUBLIC` | gatewayauth |
| 로그아웃 | POST | `/api/v1/auth/logout` | `USER` | gatewayauth |
| 내 계정/세션 조회 | GET | `/api/v1/me` | `USER` | gatewayauth |
| 입체 묵상 화면 | GET | `/api/v1/passages/{bookCode}/{chapter}/{verse}` | `PUBLIC` | bff |
| 대시보드 | GET | `/api/v1/me/dashboard` | `USER` | bff |
| 성경 목록 | GET | `/api/v1/bible/books` | `PUBLIC` | bff |
| 성경 본문 조회 | GET | `/api/v1/bible/passages` | `PUBLIC` | bff |
| 본문 해설 | GET | `/api/v1/explanations/{bookCode}/{ch}/{v}` | `USER` | bff |
| 오늘 QT | GET | `/api/v1/qt/today` | `PUBLIC` | bff |
| 오늘 QT 묵상 DRAFT 생성/조회 | POST | `/api/v1/journals/today` | `USER` | bff |
| 묵상 노트 목록 | GET | `/api/v1/journals` | `USER` | bff |
| 묵상 노트 단건 | GET | `/api/v1/journals/{id}` | `USER` | bff |
| 묵상 노트 수정 | PATCH | `/api/v1/journals/{id}` | `USER` | bff |
| 묵상 노트 삭제 | DELETE | `/api/v1/journals/{id}` | `USER` | bff |
| 묵상 노트 이벤트 로그 | GET | `/api/v1/journals/{id}/events` | `USER` | bff |
| 묵상 달력 | GET | `/api/v1/journals/calendar` | `USER` | bff |
| 묵상 노트 날짜별 조회 | GET | `/api/v1/journals?date=YYYY-MM-DD` | `USER` | bff |
| 묵상 익명 공유 생성 | POST | `/api/v1/journals/{id}/share` | `USER` | bff |
| 묵상 익명 공유 해제 | DELETE | `/api/v1/journals/{id}/share` | `USER` | bff |
| 익명 나눔 목록 | GET | `/api/v1/shares` | `PUBLIC` | bff |
| 익명 나눔 상세 | GET | `/api/v1/shares/{shareId}` | `PUBLIC` | bff |
| 익명 나눔 좋아요 | POST/DELETE | `/api/v1/shares/{shareId}/likes` | `USER` | bff |
| 익명 나눔 댓글 | GET/POST | `/api/v1/shares/{shareId}/comments` | `PUBLIC/USER` | bff |
| 익명 나눔 댓글 삭제 | DELETE | `/api/v1/shares/{shareId}/comments/{commentId}` | `USER` | bff |
| 익명 나눔 신고 | POST | `/api/v1/shares/{shareId}/reports` | `USER` | bff |
| 시뮬레이터 상태/클립 조회 | GET | `/api/v1/simulator/{bookCode}/{ch}/{v}` | `PUBLIC` | bff |
| 찬양 큐레이션 리스트 조회 | GET | `/api/v1/songs/curated` | `PUBLIC` | bff |
| 내 찬양 목록 조회 | GET | `/api/v1/me/songs` | `USER` | bff |
| 내 찬양 저장 | POST | `/api/v1/me/songs/{songId}` | `USER` | bff |
| 내 찬양 제거 | DELETE | `/api/v1/me/songs/{songId}` | `USER` | bff |
| 알림 목록 | GET | `/api/v1/me/notifications` | `USER` | bff |
| 관리자 대시보드 요약 | GET | `/api/v1/admin/dashboard` | `ADMIN` | bff |
| 관리자 QT 범위 CRUD | GET/POST/PATCH/DELETE | `/api/v1/admin/qt-ranges/**` | `ADMIN` | bff |
| 관리자 성경 데이터 상태 | GET | `/api/v1/admin/bible/**` | `ADMIN` | bff |
| 관리자 해설 C 관리 | GET/POST/PATCH | `/api/v1/admin/explanations/**` | `ADMIN` | bff |
| 관리자 AI 산출물 로그 | GET | `/api/v1/admin/ai/runs/**` | `ADMIN` | bff |
| 관리자 AI 산출물 재생성 | POST | `/api/v1/admin/ai/regenerate` | `ADMIN` | bff |
| 관리자 시뮬레이터 상태 관리 | GET/PATCH | `/api/v1/admin/simulator/**` | `ADMIN` | bff |
| 관리자 익명 나눔 신고 관리 | GET/PATCH/DELETE | `/api/v1/admin/reports/**` | `ADMIN` | bff |
| 관리자 찬양 큐레이션 CRUD | GET/POST/PATCH/DELETE | `/api/v1/admin/songs/**` | `ADMIN` | bff |
| 관리자 감사 로그 조회 | GET | `/api/v1/admin/audit-logs` | `ADMIN` | bff |

---

## 5. 사용자 API 상세

### 5.1 인증·세션 API

인증은 `gatewayauth` 도메인에서 처리한다. Google OAuth 기반으로 계정을 생성·연결하며, 별도 Auth Service를 두지 않는다.

| 기능 | Method | Path | 권한 | 설명 |
| --- | --- | --- | --- | --- |
| Google 로그인 URL 조회 | GET | `/api/v1/auth/google/authorize` | `PUBLIC` | Web/Admin 로그인 시작용 authorization URL 반환 |
| Google 로그인 토큰 교환 | POST | `/api/v1/auth/google/token` | `PUBLIC` | Google authorization code 또는 ID token을 서비스 JWT로 교환 |
| Access Token 재발급 | POST | `/api/v1/auth/refresh` | `PUBLIC` | Refresh Token으로 Access Token 재발급 |
| 로그아웃 | POST | `/api/v1/auth/logout` | `USER` | Refresh Token `jti`를 블랙리스트 캐시에 등록 |
| 내 계정/세션 조회 | GET | `/api/v1/me` | `USER` | 현재 로그인 사용자와 권한 조회 |

**POST `/api/v1/auth/google/token` Request**

```json
{
  "provider": "GOOGLE",
  "authorizationCode": "google-auth-code",
  "idToken": null,
  "redirectUri": "https://admin.example.com/oauth/callback"
}
```

**Response 200**

```json
{
  "accessToken": "jwt-access-token",
  "accessTokenExpiresIn": 1800,
  "refreshToken": "jwt-refresh-token",
  "refreshTokenExpiresIn": 1209600,
  "tokenType": "Bearer",
  "user": {
    "userId": 10,
    "displayName": "사용자",
    "email": "user@example.com",
    "role": "USER",
    "status": "ACTIVE"
  }
}
```

**인증 계약 기준**

| 항목 | 기준 |
| --- | --- |
| Access Token | 30분(1800s), RS256 |
| Refresh Token | 14일, `jti` 기준 블랙리스트 캐시 관리 |
| 소프트 로그인 | Today QT 미리보기, 성경 목록, 성경 본문, 찬양 큐레이션 조회는 비로그인 허용 |
| 로그인 필수 | 해설 열람, 묵상 저장, 찬양 저장, 공유 작성·반응, 묵상 달력 조회 |
| 교회 인증 | 화면·버튼·API·DB 필드 모두 만들지 않는다. |

### 5.2 오늘 QT 조회

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/qt/today` |
| 권한 | `PUBLIC` |
| 설명 | 오늘 QT 본문, 해설 진입점, 묵상 DRAFT 진입점, 시뮬레이터 상태, 캐시 상태를 반환한다. |

**Response 200**

```json
{
  "qtId": "2026-05-15",
  "date": "2026-05-15",
  "range": {
    "bookCode": "GEN",
    "chapterStart": 1,
    "verseStart": 1,
    "chapterEnd": 1,
    "verseEnd": 10,
    "startOrdinal": 1,
    "endOrdinal": 10
  },
  "passages": [
    {
      "verseKey": "GEN.1.1",
      "koText": "한글 성경 본문",
      "enText": "English Bible text"
    }
  ],
  "explanation": {
    "available": true,
    "loginRequired": true,
    "path": "/api/v1/explanations/GEN/1/1"
  },
  "journal": {
    "loginRequired": true,
    "draftAvailable": false,
    "todayJournalId": null,
    "path": "/api/v1/journals/today"
  },
  "simulator": {
    "status": "READY",
    "clipId": 10,
    "disabledReason": null
  },
  "cache": {
    "cacheStatus": "HIT",
    "source": "CACHE",
    "servedQtDate": "2026-05-15",
    "refreshedAt": "2026-05-15T04:18:00+09:00",
    "expiresAt": "2026-05-16T04:00:00+09:00",
    "nextRefreshAt": "2026-05-16T04:00:00+09:00",
    "staleReason": null
  }
}
```

**계약 기준**

| 항목 | 기준 |
| --- | --- |
| Today QT 100% | 본문, 해설 진입점, 묵상 진입점, 시뮬레이터 상태값이 정상 응답해야 한다. |
| 해설 본문 | Today QT 미리보기 응답에는 해설 본문을 직접 싣지 않는다. 실제 해설 열람은 `USER` 권한 API로 분리한다. |
| 시뮬레이터 클립 | 모든 본문에 실제 클립이 있어야 한다는 뜻은 아니다. |
| 00:00~04:00 | 04:00 KST 배치 전에는 `STALE_FALLBACK`으로 이전 캐시를 조회할 수 있다. |
| 캐시 없음 | 기존 캐시도 없으면 `cacheStatus=EMPTY`, `staleReason=NO_CACHE`와 함께 준비 중 상태를 반환한다. |
| LLM 호출 | 이 API 처리 중 LLM을 호출하지 않는다. |

### 5.3 성경 본문 조회

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/bible/passages` |
| 권한 | `PUBLIC` |
| Query | `bookCode`, `chapter`, `verseStart`, `verseEnd` |
| 설명 | 자체 DB에 적재된 한/영 성경 본문을 절 단위로 조회한다. |

**Response 200**

```json
{
  "bookCode": "GEN",
  "chapter": 1,
  "source": {
    "translationName": "TBD",
    "attribution": "출처 표기",
    "redistributionAllowed": true
  },
  "verses": [
    {
      "verse": 1,
      "koText": "한글 성경 본문",
      "enText": "English Bible text"
    }
  ]
}
```

개역개정, ESV, NIV 본문은 저장·응답·테스트 데이터로 사용하지 않는다.

### 5.4 본문 해설 조회

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/explanations/{bookCode}/{ch}/{v}` |
| 권한 | `USER` |
| 설명 | 사용자 노출용 C 테이블 해설을 조회한다. |

**Response 200**

```json
{
  "bookCode": "GEN",
  "chapter": 1,
  "verse": 1,
  "title": "본문 해설",
  "summary": "초심자도 이해할 수 있는 요약",
  "background": "배경 설명",
  "explanation": "차분하고 상세한 정보 전달형 해설",
  "terms": [],
  "sources": [
    {
      "sourceType": "B_PUBLIC_DOMAIN",
      "sourceLabel": "출처명",
      "attribution": "출처 표기"
    }
  ]
}
```

| 데이터 | 사용자 API 노출 |
| --- | --- |
| A 최신 한국어 주석 | 금지 |
| B 영어 원문 주석 | 금지 |
| C 사용자 노출 해설 | 허용 |

### 5.5 묵상 노트 API

| 기능 | Method | Path | 권한 | 설명 |
| --- | --- | --- | --- | --- |
| 오늘 QT DRAFT 생성/조회 | POST | `/api/v1/journals/today` | `USER` | 오늘 QT 기준 멱등 생성 또는 기존 DRAFT 반환 |
| 묵상 목록 | GET | `/api/v1/journals` | `USER` | 날짜 역순 목록. `date` 쿼리로 특정 날짜 조회 가능 |
| 묵상 단건 | GET | `/api/v1/journals/{id}` | `USER` | 본인 묵상 상세 조회 |
| 묵상 수정 | PATCH | `/api/v1/journals/{id}` | `USER` | 4개 섹션 자동 저장 |
| 묵상 삭제 | DELETE | `/api/v1/journals/{id}` | `USER` | 본인 묵상 삭제 |
| 묵상 이벤트 로그 | GET | `/api/v1/journals/{id}/events` | `USER` | 생성·수정·삭제 이벤트 조회 |

**묵상 공통 Response**

```json
{
  "journalId": 100,
  "qtId": "2026-05-15",
  "qtDate": "2026-05-15",
  "status": "DRAFT",
  "visibility": "PRIVATE",
  "sections": {
    "feeling": "",
    "memoryVerse": "",
    "application": "",
    "prayer": ""
  },
  "share": null,
  "createdAt": "2026-05-15T09:00:00+09:00",
  "updatedAt": "2026-05-15T09:00:00+09:00"
}
```

**PATCH `/api/v1/journals/{id}` Request**

```json
{
  "feeling": "느낀 점",
  "memoryVerse": "기억할 구절",
  "application": "적용할 점",
  "prayer": "기도"
}
```

묵상은 오늘 QT 기준으로만 생성한다. 자유 본문용 수동 생성 API는 만들지 않는다. 생성·수정·삭제 후에는 묵상 달력 캐시 무효화 이벤트를 Spring `ApplicationEventPublisher`로 발행한다.

### 5.6 묵상 달력 조회

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/journals/calendar` |
| 권한 | `USER` |
| Query | `year`, `month` |
| 설명 | 월별 묵상 기록 여부를 달력 형태로 조회한다. |

**Response 200**

```json
{
  "year": 2026,
  "month": 5,
  "days": [
    {
      "date": "2026-05-15",
      "hasJournal": true,
      "journalId": 100
    }
  ],
  "refreshedAt": "2026-05-15T09:10:00+09:00"
}
```

### 5.7 익명 나눔 API

| 기능 | Method | Path | 권한 | 설명 |
| --- | --- | --- | --- | --- |
| 묵상 공유 생성 | POST | `/api/v1/journals/{id}/share` | `USER` | 본인 묵상을 익명 나눔으로 공개 |
| 묵상 공유 해제 | DELETE | `/api/v1/journals/{id}/share` | `USER` | 공유 상태를 비공개로 되돌림 |
| 공유 글 목록 | GET | `/api/v1/shares` | `PUBLIC` | 공개 상태 공유 글 목록 |
| 공유 글 상세 | GET | `/api/v1/shares/{shareId}` | `PUBLIC` | 작성자 정보 없이 상세 조회 |
| 좋아요 | POST | `/api/v1/shares/{shareId}/likes` | `USER` | 좋아요 추가 |
| 좋아요 취소 | DELETE | `/api/v1/shares/{shareId}/likes` | `USER` | 좋아요 취소 |
| 댓글 목록 | GET | `/api/v1/shares/{shareId}/comments` | `PUBLIC` | 댓글 목록 조회 |
| 댓글 작성 | POST | `/api/v1/shares/{shareId}/comments` | `USER` | 댓글 작성 |
| 댓글 삭제 | DELETE | `/api/v1/shares/{shareId}/comments/{commentId}` | `USER` | 본인 댓글 삭제 |
| 신고 | POST | `/api/v1/shares/{shareId}/reports` | `USER` | 관리자 확인 대상 신고 생성 |

**공유 글 Response**

```json
{
  "shareId": 500,
  "qtDate": "2026-05-15",
  "range": {
    "bookCode": "GEN",
    "chapterStart": 1,
    "verseStart": 1,
    "chapterEnd": 1,
    "verseEnd": 10
  },
  "sections": {
    "feeling": "공유된 느낀 점",
    "memoryVerse": "공유된 기억할 구절",
    "application": "공유된 적용",
    "prayer": "공유된 기도"
  },
  "likeCount": 3,
  "commentCount": 1,
  "likedByMe": false,
  "sharedAt": "2026-05-15T10:00:00+09:00"
}
```

공유 화면에서는 `userId`, `displayName`, `email` 등 작성자 식별 정보를 노출하지 않는다. 팔로우, 랭킹, 실시간 댓글 피드, 세분화된 공개 범위는 v1에서 제외한다.

### 5.8 시뮬레이터 상태/클립 조회

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/simulator/{bookCode}/{ch}/{v}` |
| 권한 | `PUBLIC` |
| 설명 | 본문 범위에 대한 시뮬레이터 상태와 클립 정보를 조회한다. |

**Response 200**

```json
{
  "bookCode": "GEN",
  "chapter": 1,
  "verse": 1,
  "status": "READY",
  "clipId": 10,
  "clipUrl": "/media/simulator/10",
  "disabledReason": null,
  "updatedAt": "2026-05-15T04:25:00+09:00"
}
```

| status | 의미 | UI 처리 |
| --- | --- | --- |
| `READY` | 재생 가능한 클립 있음 | 보기 버튼 활성화 |
| `MISSING` | 아직 생성된 클립 없음 | 보기 버튼 비활성화 |
| `FAILED` | 생성 실패 | 보기 버튼 비활성화 |
| `DISABLED` | MVP에서 지원하지 않는 본문 | 보기 버튼 비활성화 |

### 5.9 찬양 큐레이션·내 찬양 목록

| 기능 | Method | Path | 권한 | 설명 |
| --- | --- | --- | --- | --- |
| 찬양 큐레이션 조회 | GET | `/api/v1/songs/curated` | `PUBLIC` | 운영자 사전 큐레이션 목록 |
| 내 찬양 목록 조회 | GET | `/api/v1/me/songs` | `USER` | 저장한 큐레이션 곡 목록 |
| 내 찬양 저장 | POST | `/api/v1/me/songs/{songId}` | `USER` | 큐레이션 곡 저장 |
| 내 찬양 제거 | DELETE | `/api/v1/me/songs/{songId}` | `USER` | 저장한 곡 제거 |

**Response 200**

```json
{
  "items": [
    {
      "songId": 1,
      "title": "찬양 제목",
      "artist": "아티스트",
      "externalRef": {
        "provider": "TBD",
        "refId": "external-id"
      },
      "sourceName": "출처명",
      "attribution": "출처 표기",
      "isSaved": false
    }
  ]
}
```

AI 추천, 가사 저장, 음원 파일 저장, 사용자 직접 YouTube URL 입력 API는 만들지 않는다. 사용자 라이브러리는 `songId` 등 참조 정보만 보관한다.

### 5.10 알림 목록

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/me/notifications` |
| 권한 | `USER` |
| 설명 | 인앱 폴링 방식으로 알림 목록을 조회한다. |

**Response 200**

```json
{
  "items": [
    {
      "notificationId": 900,
      "type": "REPORT_RESULT",
      "title": "신고 처리 안내",
      "body": "관리자 확인이 완료되었습니다.",
      "readAt": null,
      "createdAt": "2026-05-15T11:00:00+09:00"
    }
  ],
  "hasNext": false
}
```

---

## 6. 관리자 API 상세

관리자 API는 모두 `ADMIN` 권한을 요구한다. 관리자 작업 중 데이터 변경은 감사 로그 대상이다.

### 6.1 관리자 공통 정책

| 항목 | 기준 |
| --- | --- |
| 권한 | `/api/v1/admin/**` 전체 `ADMIN` 필요 |
| 감사 로그 | 데이터 변경, AI 재생성, 신고 처리, 사용자 제재·권한 변경은 `admin_audit_logs`에 기록 |
| 시스템 작업 | 배치·AI 실제 실행은 `SYSTEM` 작업으로 기록 |
| 사용자 요청 경로 LLM 금지 | 관리자 재생성 요청은 접수 API일 뿐, 일반 사용자 요청 중 LLM을 호출하지 않는다. |
| A 테이블 | 사용자 API와 화면에는 노출하지 않는다. 관리자·배치 검증 범위에서만 접근한다. |

### 6.2 관리자 API 목록

| 기능 | Method | Path | 우선순위 | 설명 |
| --- | --- | --- | --- | --- |
| 대시보드 요약 | GET | `/api/v1/admin/dashboard` | P0 | 총 묵상 횟수, AI 배치 처리량, 신고 대기 수, Today QT 캐시 상태 |
| QT 범위 목록/등록 | GET/POST | `/api/v1/admin/qt-ranges` | P0 | 오늘 QT 본문 범위 관리 |
| QT 범위 수정/삭제 | PATCH/DELETE | `/api/v1/admin/qt-ranges/{qtRangeId}` | P0 | 범위 수정·삭제 |
| 성경 소스 조회 | GET | `/api/v1/admin/bible/sources` | P0 | JSON 소스, 라이선스, 재배포 가능 여부 확인 |
| 성경 적재 상태 조회 | GET | `/api/v1/admin/bible/import-status` | P0 | 책·장·절 누락, 적재 상태 확인 |
| 해설 C 목록/등록 | GET/POST | `/api/v1/admin/explanations` | P0 | 사용자 노출 해설 관리 |
| 해설 C 수정 | PATCH | `/api/v1/admin/explanations/{explanationId}` | P0 | 사용자 노출 해설 수정 |
| AI 실행 로그 목록 | GET | `/api/v1/admin/ai/runs` | P0 | 생성·검증·반려 로그 조회 |
| AI 실행 로그 상세 | GET | `/api/v1/admin/ai/runs/{runId}` | P0 | 본문 범위, 프롬프트 버전, 편집자 검증 결과 |
| AI 산출물 재생성 | POST | `/api/v1/admin/ai/regenerate` | P0 | 해설 또는 시뮬레이터 재생성 접수 |
| 시뮬레이터 상태 목록 | GET | `/api/v1/admin/simulator/clips` | P0 | 본문별 상태 조회 |
| 시뮬레이터 상태 수정 | PATCH | `/api/v1/admin/simulator/clips/{clipId}` | P0 | `DISABLED` 등 운영 상태 조정 |
| 신고 목록 | GET | `/api/v1/admin/reports` | P0 | 익명 나눔 신고 목록 |
| 신고 처리 | PATCH | `/api/v1/admin/reports/{reportId}` | P0 | 처리 상태 변경, 공유 글 비공개 |
| 공유 글 관리자 삭제 | DELETE | `/api/v1/admin/shares/{shareId}` | P0 | 신고 대응 삭제 또는 비공개 처리 |
| 찬양 목록/등록 | GET/POST | `/api/v1/admin/songs` | P0 | 운영자 큐레이션 곡 메타데이터 관리 |
| 찬양 수정/삭제 | PATCH/DELETE | `/api/v1/admin/songs/{songId}` | P0 | 곡 메타데이터 수정·삭제 |
| 감사 로그 조회 | GET | `/api/v1/admin/audit-logs` | P0 | 관리자 작업 이력 조회 |
| 사용자 관리 | GET/PATCH | `/api/v1/admin/users/**` | P1 | 사용자 상태·권한 관리. 계정 탈퇴는 MVP 제외 |
| 공지사항 관리 | GET/POST/PATCH | `/api/v1/admin/notices/**` | P1 | 공지 등록·수정 |

### 6.3 관리자 대시보드 요약

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/admin/dashboard` |
| 권한 | `ADMIN` |

**Response 200**

```json
{
  "totalJournalCount": 1200,
  "aiBatchRunsToday": 4,
  "pendingReportCount": 3,
  "todayQt": {
    "qtId": "2026-05-15",
    "cacheStatus": "HIT",
    "refreshedAt": "2026-05-15T04:18:00+09:00",
    "nextRefreshAt": "2026-05-16T04:00:00+09:00"
  }
}
```

인기 구절 Top N 통계는 수집하거나 표시하지 않는다.

### 6.4 QT 범위 관리

**POST `/api/v1/admin/qt-ranges` Request**

```json
{
  "qtDate": "2026-05-15",
  "bookCode": "GEN",
  "chapterStart": 1,
  "verseStart": 1,
  "chapterEnd": 1,
  "verseEnd": 10,
  "publishedAt": "2026-05-15T00:00:00+09:00"
}
```

본문 텍스트는 수집하지 않고 범위 정보만 저장한다. 등록·수정·삭제는 감사 로그 필수 대상이며, 캐시 교체는 배치 또는 관리자 운영 절차에서 별도로 수행한다.

### 6.5 성경 데이터 상태 조회

| 기능 | Method | Path | 설명 |
| --- | --- | --- | --- |
| 소스 조회 | GET | `/api/v1/admin/bible/sources` | Repo URL, 라이선스, 번역본명, 출처 표기, 재배포 가능 여부 |
| 적재 상태 | GET | `/api/v1/admin/bible/import-status` | 책·장·절 누락, 마지막 적재 시각 |

개역개정, ESV, NIV는 저장·응답·테스트 데이터로 사용하지 않는다.

### 6.6 해설 C 관리

| 기능 | Method | Path | 설명 |
| --- | --- | --- | --- |
| 목록 조회 | GET | `/api/v1/admin/explanations` | `qtDate`, `status` 조건 조회 |
| 등록 | POST | `/api/v1/admin/explanations` | 사용자 노출 C 해설 등록 |
| 수정 | PATCH | `/api/v1/admin/explanations/{explanationId}` | C 해설 수정 |

**PATCH Request**

```json
{
  "summary": "수정된 요약",
  "background": "수정된 배경",
  "terms": [],
  "explanation": "수정된 사용자 노출 해설",
  "status": "PUBLISHED"
}
```

A 테이블 원문은 사용자 API로 노출하지 않는다. C 테이블 하단에는 출처(`sources`)를 표시한다.

### 6.7 AI 산출물 로그·재생성

| 기능 | Method | Path | 설명 |
| --- | --- | --- | --- |
| AI run 목록 | GET | `/api/v1/admin/ai/runs` | `qtDate`, `runType`, `status` 조건 조회 |
| AI run 상세 | GET | `/api/v1/admin/ai/runs/{runId}` | 프롬프트 버전, 입력 해시, 검증 결과 |
| 재생성 접수 | POST | `/api/v1/admin/ai/regenerate` | 해설 또는 시뮬레이터 재생성 요청 |

**POST `/api/v1/admin/ai/regenerate` Request**

```json
{
  "qtId": "2026-05-15",
  "target": "EXPLANATION",
  "reason": "관리자 수동 재생성"
}
```

**Response 202**

```json
{
  "runId": 300,
  "status": "PENDING",
  "message": "재생성 요청이 접수되었습니다."
}
```

| 항목 | 기준 |
| --- | --- |
| target | `EXPLANATION`, `SIMULATOR` |
| 기존 산출물 | 덮어쓰지 않고 새 version으로 저장 |
| 실행 주체 | `ADMIN` 요청으로 접수, 실제 배치/AI 작업은 `SYSTEM`으로 기록 |
| LLM 호출 | 사용자 요청 경로에서 호출하지 않는다. |

### 6.8 시뮬레이터 상태 관리

| 기능 | Method | Path | 설명 |
| --- | --- | --- | --- |
| 상태 목록 | GET | `/api/v1/admin/simulator/clips` | `qtDate`, `status` 조건 조회 |
| 상태 수정 | PATCH | `/api/v1/admin/simulator/clips/{clipId}` | `DISABLED` 전환, 실패 사유 보정 |

**PATCH Request**

```json
{
  "status": "DISABLED",
  "failureReason": "운영 판단으로 v1 노출 제외"
}
```

`READY`가 아닌 `MISSING`, `FAILED`, `DISABLED`는 사용자 화면에서 버튼 비활성화 상태로 내려간다.

### 6.9 신고·익명 나눔 관리

| 기능 | Method | Path | 설명 |
| --- | --- | --- | --- |
| 신고 목록 | GET | `/api/v1/admin/reports` | `status`, `reason` 조건 조회 |
| 신고 처리 | PATCH | `/api/v1/admin/reports/{reportId}` | `RESOLVED`, `REJECTED`, `HIDDEN` 처리 |
| 공유 글 삭제/비공개 | DELETE | `/api/v1/admin/shares/{shareId}` | 관리자 판단으로 비공개 또는 삭제 |

**PATCH Request**

```json
{
  "status": "HIDDEN",
  "action": "HIDE_SHARE",
  "memo": "신고 검토 후 비공개 처리"
}
```

신고 처리와 공유 글 삭제·비공개 처리는 감사 로그 필수 대상이다.

### 6.10 찬양 큐레이션 관리

| 기능 | Method | Path | 설명 |
| --- | --- | --- | --- |
| 목록 | GET | `/api/v1/admin/songs` | 곡 메타데이터 목록 |
| 등록 | POST | `/api/v1/admin/songs` | 운영자 큐레이션 곡 등록 |
| 수정 | PATCH | `/api/v1/admin/songs/{songId}` | 곡 메타데이터 수정 |
| 삭제 | DELETE | `/api/v1/admin/songs/{songId}` | 큐레이션 비활성화 또는 삭제 |

**POST Request**

```json
{
  "title": "찬양 제목",
  "artist": "아티스트",
  "externalRef": {
    "provider": "TBD",
    "refId": "external-id"
  },
  "metadata": {
    "theme": "묵상"
  },
  "status": "ACTIVE"
}
```

서버·관리자 DB에는 찬양 가사와 음원 파일을 저장하지 않는다. 사용자 직접 URL 입력은 제공하지 않는다.

### 6.11 감사 로그 조회

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/admin/audit-logs` |
| Query | `actorId`, `action`, `targetType`, `from`, `to`, `page`, `size` |

### 6.12 관리자 감사 로그 대상

| 대상 작업 | 감사 로그 필요 |
| --- | --- |
| 오늘 QT 본문 범위 등록/수정/삭제 | 필수 |
| 해설 C 테이블 수정 | 필수 |
| AI 재생성 트리거 | 필수 |
| 찬양 큐레이션 등록/수정/삭제 | 필수 |
| 익명 나눔 삭제/비공개 처리 | 필수 |
| 사용자 제재 또는 권한 변경 | 필수 |

---

## 7. 내부 도메인 인터페이스

내부 도메인 인터페이스는 HTTP API가 아니다. `qtai-server` 내부에서 도메인 간 호출을 위해 사용하는 Java Interface이며, 다른 도메인의 Entity/Service/Repository 직접 import를 대신한다.

| 호출 주체 | 인터페이스 | 제공 도메인 | 목적 |
| --- | --- | --- | --- |
| bff | `AuthCommandPort` | gatewayauth | Google 토큰 교환, refresh, logout |
| bff | `AuthQueryPort` | gatewayauth | 현재 사용자·권한 조회 |
| bff | `BibleQueryPort` | bible | 오늘 QT 본문·성경 본문 조회 |
| bff | `ExplanationQueryPort` | bible | C 테이블 해설 조회 |
| bff | `JournalCommandPort` | bible/journal | 묵상 노트 생성·수정·삭제 |
| bff | `JournalQueryPort` | bible/journal | 묵상 노트 조회, 묵상 달력 조회 |
| bff | `ShareCommandPort` | bible/journal | 익명 공유 생성·해제, 좋아요, 댓글, 신고 |
| bff | `ShareQueryPort` | bible/journal | 익명 나눔 목록·상세·댓글 조회 |
| bff | `SongCommandPort` | bible/songs | 내 찬양 저장·삭제 |
| bff | `SongQueryPort` | bible/songs | 큐레이션 찬양·내 찬양 목록 조회 |
| bff | `SimulatorQueryPort` | simulator | 시뮬레이터 상태·클립 조회 |
| bff | `AiRegenerateCommandPort` | ai | 관리자 AI 산출물 재생성 요청 |
| bff/admin | `AdminDashboardQueryPort` | bible/ai/simulator | 관리자 대시보드 지표 조립 |
| bff/admin | `AdminAuditCommandPort` | admin | 관리자 변경 작업 감사 로그 기록 |
| ai | `ExplanationSavePort` | bible | C 테이블 해설 저장 |
| ai | `AiRunLogPort` | ai | AI 실행 이력 저장 |
| simulator | `SimulatorClipSavePort` | simulator | 시뮬레이터 클립·상태 저장 |

### 7.1 내부 인터페이스 작성 규칙

| 규칙 | 기준 |
| --- | --- |
| 위치 | 각 도메인의 `api/` 패키지에 둔다. |
| DTO | 도메인 접두어 + `Request`/`Response`를 사용한다. |
| 금지 | Entity, Service, Repository를 다른 도메인에 노출하지 않는다. |
| HTTP 혼동 금지 | 내부 Interface 이름에 HTTP 경로를 넣지 않는다. |

---

## 8. 삭제 또는 금지된 API

아래 API는 v1에서 만들지 않는다.

| 금지 API | 이유 |
| --- | --- |
| `POST /ai/sessions` | 사용자 AI Q&A 제거 |
| `POST /ai/sessions/{id}/turns` | SSE 스트리밍 제거 |
| `POST /ai/sessions/{id}/complete` | 사용자 요청 경로 LLM 호출 금지 |
| `GET /ai/sessions/{id}` | 사용자 AI 세션 없음 |
| `GET /ai/sessions` | 사용자 AI 세션 없음 |
| 교회 인증 관련 모든 경로 | 교회 인증은 MVP 완전 제외 |
| 사용자 직접 YouTube URL 등록 API | 찬양 범위 과확장 및 저작권 리스크 |
| 사용자 AI 찬양 추천 API | 운영자 사전 큐레이션으로 대체 |

---

## 9. OpenAPI 산출물 관리

추후 구현 저장소에서는 도메인별 OpenAPI 파일을 둘 수 있다.

| 파일 | 범위 |
| --- | --- |
| `apis/bff/openapi.yaml` | `/api/v1/**` 외부 공개 API |
| `apis/admin/openapi.yaml` | `/api/v1/admin/**` 관리자 API |

OpenAPI 산출물은 이 문서의 외부 공개 API 목록과 충돌하면 안 된다. 내부 Java Interface는 OpenAPI 대상이 아니다.

---

## 10. 품질 게이트 연계

| 검사 항목 | 기준 |
| --- | --- |
| `/api/v1` prefix | 외부 공개 API는 `/api/v1`로 통일 |
| 소프트 로그인 | 오늘 QT 미리보기, 성경 목록, 성경 본문, 찬양 큐레이션 조회는 비로그인 접근 허용 |
| 인증 API | Google OAuth, refresh, logout, `/api/v1/me` 기준을 F-04와 일치 |
| Today QT 캐시 | `cache.cacheStatus`, `servedQtDate`, `nextRefreshAt`, `staleReason` 포함 |
| 익명 나눔 | ERD의 `anonymous_shares`, `share_comments`, `share_likes`, `share_reports`와 API 매핑 |
| 사용자 AI API 금지 | `/ai/sessions/**`, SSE endpoint 생성 금지 |
| 관리자 API 권한 | `/api/v1/admin/**`은 `ADMIN` 필요 |
| 관리자 P0 API | QT 범위, 성경 상태, C 해설, AI 로그, 신고, 찬양, 감사 로그, 대시보드 명세 포함 |
| A 테이블 노출 금지 | 사용자 응답 DTO에 A 테이블 원문 포함 금지 |
| 시뮬레이터 상태 | `READY`, `MISSING`, `FAILED`, `DISABLED` 중 하나 |
| 내부 Interface | 다른 도메인 Entity/Service import 금지 |

---

## 11. 다음 작업

| 순서 | 작업 | 목적 |
| --- | --- | --- |
| 완료 | `03_아키텍처_정의서.md` Port 명칭 정합성 확인 | API·ERD와 내부 Java Interface 이름을 맞춤 |
| 완료 | `25_기능_명세서.md`, `22_구현_저장소_반영_체크리스트.md` 정합화 | API 계약이 기능 명세와 구현 저장소 체크리스트에 반영됨 |
| 완료 | `00_개발_일정_총괄표.md` 작성 | 분리된 산출물 기준으로 전체 일정표 정리 완료 |
| 완료 | `07_요구사항_정의서.md` 슬림화 | 기능·비기능·화면 요구사항만 남기도록 정리 완료 |

---

## 12. 현재 상태

| 항목 | 상태 |
| --- | --- |
| 기준 요구사항 | `07_요구사항_정의서.md` v2.3 유지 |
| 개발 일정 총괄표 | `00_개발_일정_총괄표.md` v0.1 작성 완료 |
| 프로젝트 계획서 | `01_프로젝트_계획서.md` v0.1 작성 완료 |
| ERD 문서 | `02_ERD_문서.md` v0.2 명칭·상태값 정합화 완료 |
| 구현 저장소 반영 체크리스트 | `22_구현_저장소_반영_체크리스트.md` v0.2 정합화 완료 |
| 기능 명세서 | `25_기능_명세서.md` v0.2 정합화 완료 |
| 화면 기능 정의서 | `06_화면_기능_정의서.md` v0.2 API 매핑 반영 완료 |
| 시퀀스 다이어그램 | `05_시퀀스_다이어그램.md` v0.2 흐름 반영 완료 |
| 아키텍처 정의서 | `03_아키텍처_정의서.md` v0.2 정합화 완료 |
| API 명세서 | 이 문서에서 v0.2로 보강 완료 |
| 도메인 용어사전 | `23_도메인_용어사전.md` v0.1 작성 완료 |
| 품질 게이트 | `18_코드_품질_게이트.md` v2.4 재점검 완료 |
| Git 규칙 | `09_Git_규칙.md` v2.4 재점검 완료 |
| 전체 문서 정합성 최종 점검 | 진행 완료 |
| 실제 `07` 슬림화 | 진행 완료 |
| 다음 권장 작업 | 별도 구현 GitHub 기준 실제 담당 경로와 PR 단위 확정 |
