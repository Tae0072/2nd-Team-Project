# API 명세서 — QT-AI v2.3 기준

> **문서 버전:** v0.1
> **작성일:** 2026-05-15
> **기준 문서:** `07_요구사항_정의서.md` v2.3
> **문서 역할:** 외부 공개 HTTP API와 내부 Java Interface 계약 관리
> **연관 문서:** `00_문서_역할_분리표.md`, `01_프로젝트_계획서.md`, `02_ERD_문서.md`, `03_아키텍처_정의서.md`, `07_요구사항_정의서.md`, `05_시퀀스_다이어그램.md`, `06_화면_기능_정의서.md`, `18_코드_품질_게이트.md`, `22_구현_저장소_반영_체크리스트.md`, `23_도메인_용어사전.md`, `25_기능_명세서.md`

---

## 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v0.1 | 2026-05-15 | Codex | `07_요구사항_정의서.md` v2.3 기준으로 API 명세서 초안 작성 |

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

---

## 4. 외부 공개 API 목록

| 기능 | Method | Path | 권한 | 담당 도메인 |
| --- | --- | --- | --- | --- |
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
| 시뮬레이터 상태/클립 조회 | GET | `/api/v1/simulator/{bookCode}/{ch}/{v}` | `PUBLIC` | bff |
| 찬양 큐레이션 리스트 조회 | GET | `/api/v1/songs/curated` | `PUBLIC` | bff |
| 내 찬양 목록 조회 | GET | `/api/v1/me/songs` | `USER` | bff |
| 내 찬양 저장 | POST | `/api/v1/me/songs/{songId}` | `USER` | bff |
| 내 찬양 제거 | DELETE | `/api/v1/me/songs/{songId}` | `USER` | bff |
| 알림 목록 | GET | `/api/v1/me/notifications` | `USER` | bff |
| 관리자 운영 API | GET/POST/PATCH/DELETE | `/api/v1/admin/**` | `ADMIN` | bff |
| 관리자 찬양 큐레이션 CRUD | GET/POST/PATCH/DELETE | `/api/v1/admin/songs/**` | `ADMIN` | bff |
| 관리자 AI 산출물 재생성 | POST | `/api/v1/admin/ai/regenerate` | `ADMIN` | bff |

---

## 5. 사용자 API 상세

### 5.1 오늘 QT 조회

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/qt/today` |
| 권한 | `PUBLIC` |
| 설명 | 오늘 QT 본문, 해설 진입점, 묵상 DRAFT 진입점, 시뮬레이터 상태를 반환한다. |

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
    "verseEnd": 10
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
    "todayJournalId": null
  },
  "simulator": {
    "status": "READY",
    "clipId": 10,
    "disabledReason": null
  }
}
```

**계약 기준**

| 항목 | 기준 |
| --- | --- |
| 오늘 QT 100% | 본문, 해설 진입점, 묵상 진입점, 시뮬레이터 상태값이 정상 응답해야 한다. |
| 해설 본문 | 오늘 QT 미리보기 응답에는 해설 본문을 직접 싣지 않는다. 실제 해설 열람은 `USER` 권한 API로 분리한다. |
| 시뮬레이터 클립 | 모든 본문에 실제 클립이 있어야 한다는 뜻은 아니다. |
| 00:00~04:00 | 04:00 KST 배치 전에는 이전에 준비된 캐시를 조회할 수 있다. |
| 비로그인 접근 | 오늘 QT 미리보기는 비로그인 접근을 허용한다. 묵상 DRAFT 생성, 해설 열람, 찬양 저장, 묵상 달력 조회는 로그인 필요 상태를 반환하거나 로그인으로 유도한다. |
| LLM 호출 | 이 API 처리 중 LLM을 호출하지 않는다. |

### 5.2 성경 본문 조회

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
  "verses": [
    {
      "verse": 1,
      "koText": "한글 성경 본문",
      "enText": "English Bible text"
    }
  ]
}
```

### 5.3 본문 해설 조회

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
  "explanation": "차분하고 상세한 정보 전달형 해설",
  "terms": [],
  "sources": []
}
```

**노출 금지**

| 데이터 | 사용자 API 노출 |
| --- | --- |
| A 최신 한국어 주석 | 금지 |
| B 영어 원문 주석 | 금지 |
| C 사용자 노출 해설 | 허용 |

### 5.4 묵상 노트 생성/조회

| 항목 | 내용 |
| --- | --- |
| Method | POST |
| Path | `/api/v1/journals/today` |
| 권한 | `USER` |
| 설명 | 오늘 QT에 대한 묵상 DRAFT를 생성하거나 기존 DRAFT를 반환한다. |

**Response 200**

```json
{
  "journalId": 100,
  "qtId": "2026-05-15",
  "status": "DRAFT",
  "sections": {
    "feeling": "",
    "memoryVerse": "",
    "application": "",
    "prayer": ""
  },
  "updatedAt": "2026-05-15T09:00:00+09:00"
}
```

### 5.5 묵상 노트 수정

| 항목 | 내용 |
| --- | --- |
| Method | PATCH |
| Path | `/api/v1/journals/{id}` |
| 권한 | `USER` |
| 설명 | 본인 묵상 노트를 수정한다. |

**Request**

```json
{
  "feeling": "느낀 점",
  "memoryVerse": "기억할 구절",
  "application": "적용할 점",
  "prayer": "기도"
}
```

**Response 200**

```json
{
  "journalId": 100,
  "status": "SAVED",
  "updatedAt": "2026-05-15T09:10:00+09:00"
}
```

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
  ]
}
```

### 5.7 시뮬레이터 상태/클립 조회

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
  "disabledReason": null
}
```

| status | 의미 | UI 처리 |
| --- | --- | --- |
| `READY` | 재생 가능한 클립 있음 | 보기 버튼 활성화 |
| `MISSING` | 아직 생성된 클립 없음 | 보기 버튼 비활성화 |
| `FAILED` | 생성 실패 | 보기 버튼 비활성화 |
| `DISABLED` | MVP에서 지원하지 않는 본문 | 보기 버튼 비활성화 |

### 5.8 찬양 큐레이션 조회

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/songs/curated` |
| 권한 | `PUBLIC` |
| 설명 | 운영자가 사전 등록한 찬양 큐레이션 리스트를 조회한다. |

**Response 200**

```json
{
  "items": [
    {
      "songId": 1,
      "title": "찬양 제목",
      "artist": "아티스트",
      "sourceName": "출처명",
      "attribution": "출처 표기",
      "isSaved": false
    }
  ]
}
```

**제약**

| 항목 | 기준 |
| --- | --- |
| AI 추천 | 사용하지 않음 |
| 직접 URL 입력 | 사용자에게 제공하지 않음 |
| 가사/음원 저장 | 저장하지 않음 |

### 5.9 내 찬양 목록 저장/제거

| 기능 | Method | Path | 권한 |
| --- | --- | --- | --- |
| 내 찬양 목록 조회 | GET | `/api/v1/me/songs` | `USER` |
| 내 찬양 저장 | POST | `/api/v1/me/songs/{songId}` | `USER` |
| 내 찬양 제거 | DELETE | `/api/v1/me/songs/{songId}` | `USER` |

### 5.10 알림 목록

| 항목 | 내용 |
| --- | --- |
| Method | GET |
| Path | `/api/v1/me/notifications` |
| 권한 | `USER` |
| 설명 | 인앱 폴링 방식으로 알림 목록을 조회한다. |

---

## 6. 관리자 API 상세

관리자 API는 모두 `ADMIN` 권한을 요구한다. 관리자 작업 중 데이터 변경은 감사 로그 대상이다.

### 6.1 관리자 운영 API 그룹

| 기능 | Method | Path | 설명 |
| --- | --- | --- | --- |
| 오늘 QT 본문 범위 관리 | GET/POST/PATCH/DELETE | `/api/v1/admin/qt/**` | QT 본문 범위 등록·수정·삭제 |
| 성경 데이터 상태 조회 | GET | `/api/v1/admin/bible/**` | JSON 적재 누락 등 확인 |
| 해설 C 테이블 관리 | GET/POST/PATCH | `/api/v1/admin/explanations/**` | 사용자 노출 해설 관리 |
| AI 산출물 로그 조회 | GET | `/api/v1/admin/ai/runs` | 생성·검증·반려 로그 조회 |
| 익명 나눔 신고 관리 | GET/PATCH/DELETE | `/api/v1/admin/reports/**` | 신고 조회, 삭제 또는 비공개 처리 |
| 찬양 큐레이션 CRUD | GET/POST/PATCH/DELETE | `/api/v1/admin/songs/**` | 운영자 사전 큐레이션 관리 |
| 감사 로그 조회 | GET | `/api/v1/admin/audit-logs` | 관리자 작업 감사 로그 조회 |

### 6.2 관리자 AI 산출물 재생성

| 항목 | 내용 |
| --- | --- |
| Method | POST |
| Path | `/api/v1/admin/ai/regenerate` |
| 권한 | `ADMIN` |
| 설명 | 특정 본문의 해설 또는 시뮬레이터 산출물 재생성을 요청한다. |

**Request**

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

**계약 기준**

| 항목 | 기준 |
| --- | --- |
| 기존 산출물 | 덮어쓰지 않고 새 version으로 저장 |
| 실행 주체 | `ADMIN` 요청으로 접수, 실제 배치/AI 작업은 `SYSTEM`으로 기록 |
| 사용자 요청 경로 | 일반 사용자 API에서 LLM 호출 금지 |

### 6.3 관리자 감사 로그 대상

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
| bff | `BibleQueryPort` | bible | 오늘 QT 본문·성경 본문 조회 |
| bff | `ExplanationQueryPort` | bible | C 테이블 해설 조회 |
| bff | `JournalCommandPort` | bible/journal | 묵상 노트 생성·수정·삭제 |
| bff | `JournalQueryPort` | bible/journal | 묵상 노트 조회, 묵상 달력 조회 |
| bff | `SongCommandPort` | bible/songs | 내 찬양 저장·삭제 |
| bff | `SongQueryPort` | bible/songs | 큐레이션 찬양·내 찬양 목록 조회 |
| bff | `SimulatorQueryPort` | simulator | 시뮬레이터 상태·클립 조회 |
| bff | `AiRegenerateCommandPort` | ai | 관리자 AI 산출물 재생성 요청 |
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
| 사용자 AI API 금지 | `/ai/sessions/**`, SSE endpoint 생성 금지 |
| 관리자 API 권한 | `/api/v1/admin/**`은 `ADMIN` 필요 |
| A 테이블 노출 금지 | 사용자 응답 DTO에 A 테이블 원문 포함 금지 |
| 시뮬레이터 상태 | `READY`, `MISSING`, `FAILED`, `DISABLED` 중 하나 |
| 내부 Interface | 다른 도메인 Entity/Service import 금지 |

---

## 11. 다음 작업

| 순서 | 작업 | 목적 |
| --- | --- | --- |
| 1 | 전체 문서 정합성 최종 점검 | 분리 문서 전체가 `07` v2.3과 충돌하지 않는지 확인 |
| 완료 | `00_개발_일정_총괄표.md` 작성 | 분리된 산출물 기준으로 전체 일정표 정리 완료 |
| 완료 | `07_요구사항_정의서.md` 슬림화 | 기능·비기능·화면 요구사항만 남기도록 정리 완료 |

---

## 12. 현재 상태

| 항목 | 상태 |
| --- | --- |
| 기준 요구사항 | `07_요구사항_정의서.md` v2.3 유지 |
| 개발 일정 총괄표 | `00_개발_일정_총괄표.md` v0.1 작성 완료 |
| 프로젝트 계획서 | `01_프로젝트_계획서.md` v0.1 작성 완료 |
| ERD 문서 | `02_ERD_문서.md` v0.1 작성 완료 |
| 구현 저장소 반영 체크리스트 | `22_구현_저장소_반영_체크리스트.md` v0.1 작성 완료 |
| 기능 명세서 | `25_기능_명세서.md` v0.1 작성 완료 |
| 화면 기능 정의서 | `06_화면_기능_정의서.md` v0.1 작성 완료 |
| 시퀀스 다이어그램 | `05_시퀀스_다이어그램.md` v0.1 작성 완료 |
| 아키텍처 정의서 | `03_아키텍처_정의서.md` v0.1 작성 완료 |
| API 명세서 | 이 문서에서 v0.1로 신규 작성 |
| 도메인 용어사전 | `23_도메인_용어사전.md` v0.1 작성 완료 |
| 품질 게이트 | `18_코드_품질_게이트.md` v2.4 재점검 완료 |
| Git 규칙 | `09_Git_규칙.md` v2.4 재점검 완료 |
| 전체 문서 정합성 최종 점검 | 진행 완료 |
| 실제 `07` 슬림화 | 진행 완료 |
| 다음 권장 작업 | 커밋/푸시 |
