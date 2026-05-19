# QT-AI API 명세서 v1.4

> **문서 버전:** v1.3  
> **작성일:** 2026-05-17  
> **기준 문서:** `01.요구사항명세서_현재완성v1.md`, `02_ERD_문서_v2.md`, `04_화면정의서.md`, `03_화면설계_스토리보드.md`  
> **작성 관점:** 백엔드 API 설계, 화면-API-ERD 연결성, 인증/권한, 예외 처리
> **v1.3 보강 범위:** 관리자 찬양/공지 API 상세화, 노트 수정 계약 보강, 나눔 삭제 ERD 정합성 보정, 하단 연결성 표 잔여 필드명 정리

---

## 목차
1. 공통 규칙
2. 인증 및 권한
3. 화면별 필요 API 목록
4. 도메인별 API 명세
5. 페이징/검색/정렬
6. 상태 코드 및 에러 응답
7. 감사 로그/AI 검증/평가 셋 API
8. ERD 테이블 연결성
9. 전체 API 요약
10. 변경 이력

---

## 1. 공통 규칙

### 1.1 Base URL

| 환경 | URL |
|---|---|
| 개발 | `http://localhost:8080` |
| 운영 | `https://api.qt-ai.example.com` |

### 1.2 API Prefix

| 구분 | Prefix | 설명 |
|---|---|---|
| 사용자 API | `/api/v1` | 모바일/웹 클라이언트 사용자 기능 |
| 관리자 API | `/api/v1/admin` | 관리자 콘솔 |
| 시스템 API | `/api/v1/system` | 배치/검증 agent 전용 |
| OAuth 콜백 | `/oauth2` | 소셜 로그인 콜백 |

### 1.3 인증 방식

- 클라이언트 API는 Bearer Access Token 기반으로 설계한다.
- Refresh Token은 서버 저장 또는 HttpOnly Cookie 중 하나로 구현한다. MVP에서는 HttpOnly Cookie 방식을 권장한다.
- 카카오 로그인 성공 후 서비스 자체 Access Token/Refresh Token을 발급한다.
- 관리자 API는 일반 회원 토큰에 `ADMIN` 권한과 `admin_users.admin_role`이 모두 확인되어야 접근 가능하다.
- 시스템 API는 사용자 토큰이 아니라 `service_accounts` 기반의 서버 간 인증 토큰을 사용한다.

### 1.4 공통 응답 형식

```json
{
  "success": true,
  "data": {},
  "error": null,
  "timestamp": "2026-05-17T10:00:00+09:00",
  "traceId": "01HX..."
}
```

> 이하 각 API의 JSON 예시는 특별히 `success`, `data`, `error`, `timestamp`, `traceId`를 명시하지 않는 한 공통 응답 envelope의 `data` 객체만 표시한다. 프론트 mock과 QA fixture를 만들 때는 1.4/1.5의 envelope로 감싸서 사용한다. `204 No Content` 응답은 envelope를 사용하지 않는다.

### 1.5 공통 에러 응답 형식

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "입력값이 올바르지 않습니다.",
    "fields": {
      "nickname": "닉네임은 2~30자여야 합니다."
    }
  },
  "timestamp": "2026-05-17T10:00:00+09:00",
  "traceId": "01HX..."
}
```

### 1.6 페이징 응답 형식

```json
{
  "success": true,
  "data": {
    "content": [],
    "page": 0,
    "size": 20,
    "totalElements": 125,
    "totalPages": 7,
    "first": true,
    "last": false,
    "sort": "createdAt,desc"
  },
  "error": null,
  "timestamp": "2026-05-17T10:00:00+09:00",
  "traceId": "01HX..."
}
```

### 1.7 공통 요청 헤더

| Header | 필수 | 설명 |
|---|---:|---|
| `Authorization: Bearer {accessToken}` | 인증 API 필수 | 사용자/관리자 인증 |
| `X-Request-Id` | 선택 | 클라이언트 요청 추적 ID |
| `Idempotency-Key` | 선택 | 중복 생성 방지가 필요한 POST 요청 |
| `Accept-Language` | 선택 | `ko`, `en` |

---

## 2. 인증 및 권한

### 2.1 역할 코드

| 역할 | 설명 | 주요 권한 |
|---|---|---|
| `ANONYMOUS` | 비로그인 사용자 | 로그인 시작만 가능 |
| `USER` | 일반 회원 | QT 조회, 성경 조회, 노트 작성, 나눔, 댓글, 좋아요, 신고, AI Q&A |
| `ADMIN` | 관리자 계정 소유 회원 | 관리자 콘솔 접근 가능 |
| `OPERATOR` | 운영 관리자 | QT 관리, 신고 처리, 공지 발행, 사용자 제재 |
| `REVIEWER` | 검증 관리자 | AI 산출물 승인/반려/숨김, 평가 케이스 관리 |
| `CONTENT_CREATOR` | 자체 제작자 | 검증용 자료와 콘텐츠 제작 메타 관리 |
| `SUPER_ADMIN` | 최고 관리자 | 전체 관리자 기능 |
| `SYSTEM_BATCH` | 시스템 배치 | AI 생성, 검증, 상태 변경, 감사 로그 기록 |

### 2.2 권한 매트릭스

| 리소스/기능 | USER | OPERATOR | REVIEWER | CONTENT_CREATOR | SYSTEM_BATCH |
|---|---:|---:|---:|---:|---:|
| 오늘 QT/성경 조회 | 가능 | 가능 | 가능 | 가능 | 가능 |
| 본인 노트 | 본인만 | 불가 | 불가 | 불가 | 제한적 처리 |
| 나눔 게시글 조회 | 공개 글만 | 가능 | 가능 | 불가 | 제한적 처리 |
| 나눔/댓글/좋아요/신고 생성 | 가능 | 가능 | 가능 | 불가 | 불가 |
| QT 본문 관리 | 불가 | 가능 | 불가 | 불가 | 가능 |
| AI 산출물 승인/반려 | 불가 | 조회 가능 | 가능 | 불가 | 자동 검증 가능 |
| 검증용 주석 원문 | 불가 | 불가 | 제한 조회 | 가능 | 검증 경로에서만 가능 |
| 평가 셋/평가 케이스 | 불가 | 조회 가능 | 가능 | 가능 | 가능 |
| 감사 로그 조회 | 불가 | 가능 | 가능 | 불가 | 생성 가능 |

### 2.3 인증 API

#### 2.3.1 카카오 로그인 시작

- **Method + URL:** `GET /oauth2/authorization/kakao`
- **인증:** 불필요
- **Response:** 카카오 인증 페이지 redirect
- **연결 화면:** A-02

#### 2.3.2 OAuth 콜백

- **Method + URL:** `GET /oauth2/callback/kakao?code={code}&state={state}`
- **인증:** 불필요
- **처리:** 카카오 사용자 식별자 확인 후 `members`, `member_auth_providers` 생성 또는 조회
- **Response 예시:**

```json
{
  "success": true,
  "data": {
    "accessToken": "eyJ...",
    "refreshTokenExpiresAt": "2026-06-16T10:00:00+09:00",
    "member": {
      "id": 10,
      "nickname": null,
      "role": "USER",
      "status": "ACTIVE",
      "onboardingRequired": true
    }
  },
  "error": null
}
```

#### 2.3.3 토큰 재발급

- **Method + URL:** `POST /api/v1/auth/token/refresh`
- **인증:** Refresh Token
- **Response:** 신규 Access Token

#### 2.3.4 로그아웃

- **Method + URL:** `POST /api/v1/auth/logout`
- **인증:** USER
- **처리:** Refresh Token 폐기
- **Response:** `204 No Content`

---

## 3. 화면별 필요 API 목록

| 화면 ID | 화면명 | 필요 API |
|---|---|---|
| A-01 | 스플래시 | `GET /api/v1/me/session` |
| A-02 | 카카오 로그인 | `GET /oauth2/authorization/kakao`, `GET /oauth2/callback/kakao` |
| A-03 | 닉네임 설정 | `GET /api/v1/members/nickname/check`, `PATCH /api/v1/me/profile` |
| A-04 | QT 튜토리얼 | `GET /api/v1/tutorial`, `POST /api/v1/me/tutorial/complete` |
| Q-01 | 오늘 QT 기본 | `GET /api/v1/qt/today`, `GET /api/v1/qt/{qtPassageId}` |
| Q-02 | 요약/해설/단어 | `GET /api/v1/qt/{qtPassageId}/study-content` |
| Q-03 | 시뮬레이터 | `GET /api/v1/qt/{qtPassageId}/simulator-clips/{clipId}` |
| Q-04 | AI 질문 | `POST /api/v1/ai/qa-requests`, `GET /api/v1/ai/qa-requests/{requestId}`, `POST /api/v1/reports` |
| Q-05 | TTS | 서버 저장 없음. 클라이언트 TTS 우선. 필요 시 `POST /api/v1/tts/play-events` |
| Q-06 | QT 노트 작성 | `GET /api/v1/notes/draft`, `POST /api/v1/notes`, `PATCH /api/v1/notes/{noteId}` |
| Q-07 | QT 노트 저장 완료 | `GET /api/v1/notes/{noteId}`, `POST /api/v1/notes/{noteId}/share` |
| B-01 | 일반 성경 조회 | `GET /api/v1/bible/books`, `GET /api/v1/bible/verses` |
| B-02 | 절 선택 상태 | `GET /api/v1/bible/verses`, 클라이언트 상태 관리 |
| B-03 | 설교 노트 작성 | `POST /api/v1/notes`, `PATCH /api/v1/notes/{noteId}` |
| N-01 | 노트 목록 | `GET /api/v1/notes` |
| N-02 | 개인 노트 카테고리 선택 | 클라이언트 라우팅, `GET /api/v1/note-categories` |
| N-03 | 개인 노트 작성 | `POST /api/v1/notes` |
| N-04 | 노트 상세/수정 | `GET /api/v1/notes/{noteId}`, `PATCH /api/v1/notes/{noteId}`, `DELETE /api/v1/notes/{noteId}` |
| S-01 | 나눔 피드 | `GET /api/v1/sharing-posts`, `POST /api/v1/sharing-posts/{postId}/like`, `DELETE /api/v1/sharing-posts/{postId}/like` |
| S-02 | 나눔 상세 | `GET /api/v1/sharing-posts/{postId}`, `GET /api/v1/sharing-posts/{postId}/comments`, `POST /api/v1/sharing-posts/{postId}/comments` |
| S-03 | 신고 바텀시트 | `POST /api/v1/reports` |
| M-01 | 마이페이지 대시보드 | `GET /api/v1/me/dashboard` |
| M-02 | 알림 목록 | `GET /api/v1/notifications`, `PATCH /api/v1/notifications/{notificationId}/read` |
| M-03 | 내 찬양 목록 | `GET /api/v1/praise-songs`, `GET /api/v1/me/praise-songs`, `POST /api/v1/me/praise-songs` |
| M-04 | 회원 정보/탈퇴 | `GET /api/v1/me`, `POST /api/v1/me/withdraw` |
| M-05 | 내 나눔 관리 | `GET /api/v1/me/sharing-posts`, `PATCH /api/v1/sharing-posts/{postId}/hide`, `DELETE /api/v1/sharing-posts/{postId}` |
| AD-01 | 관리자 대시보드 | `GET /api/v1/admin/dashboard` |
| AD-02 | 오늘 QT 관리 | `GET /api/v1/admin/qt-passages`, `POST /api/v1/admin/qt-passages`, `PATCH /api/v1/admin/qt-passages/{id}` |
| AD-03 | AI 산출물 검증 | `GET /api/v1/admin/ai/assets`, `POST /api/v1/admin/ai/assets/{assetId}/approve`, `POST /api/v1/admin/ai/assets/{assetId}/reject` |
| AD-04 | 신고 처리 | `GET /api/v1/admin/reports`, `POST /api/v1/admin/reports/{reportId}/resolve` |
| AD-05 | 찬양 큐레이션 | `GET /api/v1/admin/praise-songs`, `POST /api/v1/admin/praise-songs`, `PATCH /api/v1/admin/praise-songs/{id}` |
| AD-06 | 시스템 공지 | `GET /api/v1/admin/notices`, `POST /api/v1/admin/notices`, `POST /api/v1/admin/notices/{id}/publish` |
| AD-07 | 감사 로그 | `GET /api/v1/admin/audit-logs` |
| AD-08 | AI 운영 모니터링 | `GET /api/v1/admin/ai/monitoring` |

---

## 4. 도메인별 API 명세

## 4.1 회원/프로필 API

### 4.1.1 내 세션 조회

- **Method + URL:** `GET /api/v1/me/session`
- **인증:** 선택. 토큰이 없으면 비로그인 상태 반환
- **연결 화면:** A-01
- **ERD:** `members`, `admin_users`

```json
{
  "authenticated": true,
  "memberId": 10,
  "role": "USER",
  "adminRole": null,
  "status": "ACTIVE",
  "nickname": "하늘QT",
  "tutorialCompleted": true
}
```

### 4.1.2 내 정보 조회

- **Method + URL:** `GET /api/v1/me`
- **인증:** USER
- **연결 화면:** M-04
- **ERD:** `members`, `member_auth_providers`, `admin_users`

```json
{
  "id": 10,
  "nickname": "하늘QT",
  "role": "USER",
  "status": "ACTIVE",
  "tutorialCompletedAt": "2026-05-17T08:00:00+09:00",
  "withdrawnAt": null,
  "legalRetentionUntil": null,
  "authProviders": [
    {
      "provider": "KAKAO",
      "connectedAt": "2026-05-17T07:50:00+09:00"
    }
  ],
  "admin": null,
  "createdAt": "2026-05-17T07:50:00+09:00"
}
```

- **실패 코드:** `401 TOKEN_EXPIRED`, `403 FORBIDDEN`, `404 NOT_FOUND`

### 4.1.3 튜토리얼 콘텐츠 조회

- **Method + URL:** `GET /api/v1/tutorial`
- **인증:** USER
- **연결 화면:** A-04
- **ERD:** 별도 테이블 없음. 정적 콘텐츠 또는 설정 파일 기반

```json
{
  "version": "2026.05",
  "steps": [
    {
      "order": 1,
      "title": "오늘의 QT 읽기",
      "body": "오늘 본문을 읽고 필요한 도움 기능을 선택합니다.",
      "actionType": "NEXT"
    },
    {
      "order": 2,
      "title": "묵상 기록하기",
      "body": "느낀 점, 기억할 구절, 적용할 점, 기도를 남깁니다.",
      "actionType": "COMPLETE"
    }
  ]
}
```

### 4.1.4 닉네임 중복 확인

- **Method + URL:** `GET /api/v1/members/nickname/check?nickname=하늘QT`
- **인증:** USER
- **ERD:** `members.nickname`

```json
{
  "available": true,
  "reason": null
}
```

### 4.1.5 내 프로필 수정

- **Method + URL:** `PATCH /api/v1/me/profile`
- **인증:** USER
- **ERD:** `members`

```json
{
  "nickname": "하늘QT"
}
```

```json
{
  "id": 10,
  "nickname": "하늘QT",
  "role": "USER",
  "status": "ACTIVE",
  "tutorialCompletedAt": null
}
```

### 4.1.6 튜토리얼 완료

- **Method + URL:** `POST /api/v1/me/tutorial/complete`
- **인증:** USER
- **ERD:** `members.tutorial_completed_at`
- **Response:** `204 No Content`

### 4.1.7 회원 탈퇴

- **Method + URL:** `POST /api/v1/me/withdraw`
- **인증:** USER
- **ERD:** `members`, `notes`, `sharing_posts`, `notifications`, `ai_qa_requests`
- **처리:** `members.status=WITHDRAWN`, `withdrawn_at`, `legal_retention_until` 기록. 법적 보존 대상 외 개인 데이터는 삭제 또는 비식별화한다.

```json
{
  "confirmText": "탈퇴 후 복구할 수 없음을 확인합니다."
}
```

---

## 4.2 성경/QT API

### 4.2.1 성경 권 목록 조회

- **Method + URL:** `GET /api/v1/bible/books`
- **인증:** USER
- **ERD:** `bible_books`

```json
[
  {
    "id": 1,
    "testament": "OLD",
    "code": "GENESIS",
    "koreanName": "창세기",
    "englishName": "Genesis",
    "displayOrder": 1
  }
]
```

### 4.2.2 성경 절 조회

- **Method + URL:** `GET /api/v1/bible/verses?bookCode=GENESIS&chapter=1`
- **인증:** USER
- **ERD:** `bible_books`, `bible_verses`
- **쿼리 파라미터:**

| 파라미터 | 필수 | 형식 | 설명 |
|---|---|---|---|
| `bookCode` | 필수 | string | `bible_books.code` (예: `GENESIS`, `ROMANS`) |
| `chapter` | 필수 | int | 장 번호 |
| `verseFrom` | 선택 | int | 시작 절. 생략하면 장 전체 조회 |
| `verseTo` | 선택 | int | 끝 절. `verseFrom` 단독 지정 시 해당 절만 조회. `verseFrom <= verseTo` 강제 |

`verseFrom`/`verseTo`는 노트 본문에서 `@`멘션 본문 자동 삽입(`07` §6.4.1, F-03/F-16)을 위해 추가된 범위 조회 지원이다. 단일 인용 범위 상한(예: 50절)은 후속 정책에서 확정한다.

```json
{
  "book": {
    "code": "GENESIS",
    "koreanName": "창세기",
    "chapter": 1
  },
  "verses": [
    {
      "id": 1001,
      "verseNo": 1,
      "koreanText": "태초에 하나님이 천지를 창조하시니라",
      "englishText": "In the beginning God created the heaven and the earth."
    }
  ]
}
```

- **`@`멘션 호출 예시:**
  - `@로마서 8:5` → `GET /api/v1/bible/verses?bookCode=ROMANS&chapter=8&verseFrom=5&verseTo=5`
  - `@로마서 8:5-10` → `GET /api/v1/bible/verses?bookCode=ROMANS&chapter=8&verseFrom=5&verseTo=10`
  - 클라이언트는 `GET /api/v1/bible/books` 응답을 기준으로 책 이름(`koreanName`/`englishName`) → `code` 매핑을 수행한다.

- **실패 코드:**
  - `404 NOT_FOUND` — 책·장·절이 존재하지 않음
  - `400 VALIDATION_ERROR` — `verseFrom > verseTo`, 음수, 범위 상한 초과 등 잘못된 파라미터
  - `429 RATE_LIMIT_EXCEEDED` — 단시간 과다 호출 시

### 4.2.3 오늘 QT 조회

- **Method + URL:** `GET /api/v1/qt/today?date=2026-05-17`
- **인증:** USER
- **연결 화면:** Q-01
- **ERD:** `qt_passages`, `qt_passage_verses`, `bible_verses`, `notes`

```json
{
  "qtPassageId": 35,
  "qtDate": "2026-05-17",
  "title": "오늘의 QT",
  "rangeLabel": "창세기 1:1-5",
  "status": "PUBLISHED",
  "verses": [
    {
      "id": 1001,
      "bookCode": "GENESIS",
      "chapterNo": 1,
      "verseNo": 1,
      "koreanText": "태초에 하나님이 천지를 창조하시니라",
      "englishText": "In the beginning God created the heaven and the earth."
    }
  ],
  "myMeditationNote": {
    "noteId": 200,
    "status": "DRAFT"
  },
  "availableActions": {
    "studyContent": true,
    "aiQuestion": true,
    "tts": true,
    "simulator": false
  }
}
```

### 4.2.4 QT 상세 조회

- **Method + URL:** `GET /api/v1/qt/{qtPassageId}`
- **인증:** USER
- **연결 화면:** Q-01
- **ERD:** `qt_passages`, `qt_passage_verses`, `bible_verses`, `notes`, `simulator_clips`
- **설명:** `GET /qt/today`와 동일한 응답 구조를 사용하되 특정 QT 본문 ID로 조회한다.

```json
{
  "qtPassageId": 35,
  "qtDate": "2026-05-17",
  "title": "오늘의 QT",
  "rangeLabel": "창세기 1:1-5",
  "status": "PUBLISHED",
  "verses": [
    {
      "id": 1001,
      "bookCode": "GENESIS",
      "bookName": "창세기",
      "chapterNo": 1,
      "verseNo": 1,
      "koreanText": "태초에 하나님이 천지를 창조하시니라",
      "englishText": "In the beginning God created the heaven and the earth.",
      "displayOrder": 1
    }
  ],
  "studyContentAvailable": true,
  "simulatorClip": {
    "clipId": 12,
    "status": "APPROVED"
  },
  "myMeditationNote": {
    "noteId": 200,
    "status": "DRAFT",
    "activeUniqueKey": "ACTIVE"
  }
}
```

- **실패 코드:** `404 NOT_FOUND`(본문 없음 또는 미게시), `403 FORBIDDEN`

### 4.2.5 QT 학습 콘텐츠 조회

- **Method + URL:** `GET /api/v1/qt/{qtPassageId}/study-content`
- **인증:** USER
- **연결 화면:** Q-02
- **ERD:** `verse_explanations`, `glossary_terms`, `ai_generated_assets`, `ai_validation_logs`
- **노출 기준:** `APPROVED` 상태의 콘텐츠만 반환한다.

```json
{
  "summary": "본문의 핵심을 3문장 이내로 요약합니다.",
  "explanations": [
    {
      "verseId": 1001,
      "summary": "창조의 시작을 설명합니다.",
      "explanation": "사용자에게 노출 가능한 검증 완료 해설입니다.",
      "sourceLabel": "QT-AI verified content",
      "aiAssetId": 500
    }
  ],
  "glossaryTerms": [
    {
      "id": 80,
      "verseId": 1001,
      "term": "태초",
      "meaning": "시간과 창조의 시작을 가리키는 표현입니다."
    }
  ]
}
```

### 4.2.6 시뮬레이터 클립 조회

- **Method + URL:** `GET /api/v1/qt/{qtPassageId}/simulator-clips/{clipId}`
- **인증:** USER
- **ERD:** `simulator_clips`, `simulator_component_library_versions`, `ai_generated_assets`
- **노출 기준:** `simulator_clips.status=APPROVED`

```json
{
  "clipId": 12,
  "qtPassageId": 35,
  "title": "창조 장면",
  "componentLibraryVersion": "2026.05.1",
  "sceneScriptJson": {
    "scenes": []
  },
  "status": "APPROVED"
}
```

---

## 4.3 노트 API

### 4.3.1 노트 목록 조회

- **Method + URL:** `GET /api/v1/notes?category=MEDITATION&q=기도&status=SAVED&page=0&size=20&sort=savedAt,desc`
- **인증:** USER
- **연결 화면:** N-01, M-01
- **ERD:** `notes`, `note_verses`, `qt_passages`, `sharing_posts`

```json
{
  "content": [
    {
      "id": 200,
      "category": "MEDITATION",
      "title": "오늘의 묵상",
      "status": "SAVED",
      "visibility": "PRIVATE",
      "qtDate": "2026-05-17",
      "rangeLabel": "창세기 1:1-5",
      "shared": false,
      "createdAt": "2026-05-17T08:00:00+09:00",
      "updatedAt": "2026-05-17T08:10:00+09:00"
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 1,
  "totalPages": 1,
  "first": true,
  "last": true
}
```

### 4.3.2 임시 노트 조회

- **Method + URL:** `GET /api/v1/notes/draft?category=MEDITATION&qtPassageId=35`
- **인증:** USER
- **ERD:** `notes`
- **설명:** 같은 사용자+QT+MEDITATION의 활성 노트는 1건만 허용한다.

```json
{
  "exists": true,
  "note": {
    "id": 200,
    "category": "MEDITATION",
    "status": "DRAFT",
    "activeUniqueKey": "ACTIVE",
    "qtPassageId": 35,
    "title": "오늘의 묵상",
    "rememberSection": "기억할 말씀",
    "interpretSection": "깨달은 점",
    "applySection": "적용할 점",
    "praySection": "기도",
    "updatedAt": "2026-05-17T08:10:00+09:00"
  }
}
```

### 4.3.3 노트 카테고리 조회

- **Method + URL:** `GET /api/v1/note-categories`
- **인증:** USER
- **연결 화면:** N-02
- **ERD:** 코드성 데이터. `notes.category`와 매핑

```json
[
  {
    "code": "MEDITATION",
    "name": "QT 노트",
    "requiresQtPassage": true,
    "supportsVerseSelection": false,
    "writableFromList": false
  },
  {
    "code": "SERMON",
    "name": "설교 노트",
    "requiresQtPassage": false,
    "supportsVerseSelection": true,
    "writableFromList": false
  },
  {
    "code": "PRAYER",
    "name": "기도제목",
    "requiresQtPassage": false,
    "supportsVerseSelection": false,
    "writableFromList": true
  },
  {
    "code": "REPENTANCE",
    "name": "회개 노트",
    "requiresQtPassage": false,
    "supportsVerseSelection": false,
    "writableFromList": true
  },
  {
    "code": "GRATITUDE",
    "name": "감사일기",
    "requiresQtPassage": false,
    "supportsVerseSelection": false,
    "writableFromList": true
  }
]
```

### 4.3.4 노트 생성

- **Method + URL:** `POST /api/v1/notes`
- **인증:** USER
- **ERD:** `notes`, `note_verses`, `sharing_posts`

```json
{
  "category": "MEDITATION",
  "qtPassageId": 35,
  "title": "오늘의 묵상",
  "rememberSection": "기억할 말씀",
  "interpretSection": "깨달은 점",
  "applySection": "적용할 점",
  "praySection": "기도",
  "body": null,
  "verseIds": [1001, 1002],
  "status": "DRAFT",
  "visibility": "PRIVATE",
  "shareRequested": false
}
```

```json
{
  "id": 200,
  "category": "MEDITATION",
  "status": "DRAFT",
  "visibility": "PRIVATE",
  "sharedPostId": null,
  "createdAt": "2026-05-17T08:00:00+09:00"
}
```

### 4.3.5 노트 상세 조회

- **Method + URL:** `GET /api/v1/notes/{noteId}`
- **인증:** USER, 작성자 본인
- **연결 화면:** N-04, Q-07
- **ERD:** `notes`, `note_verses`, `bible_verses`, `qt_passages`, `sharing_posts`

```json
{
  "id": 200,
  "category": "MEDITATION",
  "status": "SAVED",
  "visibility": "PRIVATE",
  "activeUniqueKey": "ACTIVE",
  "qtPassage": {
    "id": 35,
    "qtDate": "2026-05-17",
    "rangeLabel": "창세기 1:1-5"
  },
  "title": "오늘의 묵상",
  "rememberSection": "기억할 말씀",
  "interpretSection": "깨달은 점",
  "applySection": "적용할 점",
  "praySection": "기도",
  "body": null,
  "verses": [
    {
      "id": 1001,
      "label": "창세기 1:1",
      "koreanText": "태초에 하나님이 천지를 창조하시니라",
      "displayOrder": 1
    }
  ],
  "sharingPost": {
    "id": 300,
    "status": "PUBLISHED",
    "commentsEnabled": true,
    "publishedAt": "2026-05-17T08:20:00+09:00"
  },
  "savedAt": "2026-05-17T08:15:00+09:00",
  "deletedAt": null,
  "updatedAt": "2026-05-17T08:15:00+09:00"
}
```

### 4.3.6 노트 수정

- **Method + URL:** `PATCH /api/v1/notes/{noteId}`
- **인증:** USER, 작성자 본인
- **ERD:** `notes`, `note_verses`
- **연결 화면:** N-04, Q-06
- **주의:** 이미 생성된 `sharing_posts`의 스냅샷은 자동 변경하지 않는다.
- **상태 전이:** `DRAFT -> SAVED`, `SAVED -> DRAFT`, `DRAFT/SAVED -> DELETED`. `DELETED` 상태 노트는 수정할 수 없다.
- **구절 수정 정책:** `verseIds`를 전달하면 기존 `note_verses`를 요청 배열 기준으로 교체한다. `MEDITATION`은 `qtPassageId`의 구절 범위 안에서만 허용하고, `SERMON`은 자유 선택을 허용한다. `PRAYER`, `REPENTANCE`, `GRATITUDE`는 구절 연결 없이 저장할 수 있다.
- **`@`멘션 본문 자동 삽입 (`07` §6.4.1, F-03/F-16):** 클라이언트는 본문 작성 영역에서 `@책 장:절` 또는 `@책 장:절-절` 입력을 파싱해 `GET /api/v1/bible/verses?bookCode=&chapter=&verseFrom=&verseTo=`(§4.2.2)로 절을 조회한 뒤, `body`(또는 4개 섹션 본문) 안에 인용 블록 마크업으로 직접 삽입한다. 서버는 `body` 텍스트를 자유 형식으로 보존한다. 인용된 절들의 `id` 목록은 `verseIds` 배열에 함께 담아 보내며, 서버는 이를 `note_verses`에 저장해 메타데이터 인덱스(검색·통계·내 노트 구절 보기)로 사용한다. 본문 안 인용 블록 텍스트가 사용자에 의해 직접 수정·삭제되어도 `verseIds`는 클라이언트가 다시 보내는 값으로 동기화된다(동일 절을 두 번 인용해도 `note_verses`에는 중복 없이 저장된다).

요청 예시:

```json
{
  "status": "SAVED",
  "title": "오늘의 묵상",
  "rememberSection": "기억할 말씀",
  "interpretSection": "깨달은 점",
  "applySection": "적용할 점",
  "praySection": "기도",
  "body": null,
  "verseIds": [1001, 1002],
  "visibility": "PRIVATE"
}
```

자유 노트 요청 예시:

```json
{
  "status": "SAVED",
  "title": "감사일기",
  "body": "오늘 감사한 일을 기록합니다.",
  "verseIds": [],
  "visibility": "PRIVATE"
}
```

응답 예시:

```json
{
  "id": 200,
  "category": "MEDITATION",
  "status": "SAVED",
  "visibility": "PRIVATE",
  "activeUniqueKey": "ACTIVE",
  "savedAt": "2026-05-17T08:15:00+09:00",
  "updatedAt": "2026-05-17T08:15:00+09:00",
  "sharingSnapshotUpdated": false
}
```

- **성공 코드:** `200 OK`
- **실패 코드:** `400 VALIDATION_ERROR`, `403 FORBIDDEN`, `404 NOT_FOUND`, `409 DUPLICATE_NOTE`, `409 INVALID_STATUS_TRANSITION`, `422 INVALID_INPUT`

### 4.3.7 노트 삭제

- **Method + URL:** `DELETE /api/v1/notes/{noteId}`
- **인증:** USER, 작성자 본인
- **처리:** 소프트 삭제. `notes.status=DELETED`, `notes.deleted_at=now()`, `notes.active_unique_key=NULL`
- **ERD 정합성:** `active_unique_key=NULL` 처리를 누락하면 `uk_notes_active_qt_meditation` 때문에 같은 사용자+같은 QT 본문에 묵상 노트를 재작성할 수 없다.
- **나눔 영향:** 연결된 `sharing_posts`는 공유본 스냅샷 정책에 따라 자동 수정하지 않는다. 다만 `sharing_posts.source_note_deleted_at=now()`를 기록하여 상세 화면에서 원본 삭제 안내와 댓글 입력 가능 여부를 판단한다.
- **Response:** `204 No Content`
- **실패 코드:** `403 FORBIDDEN`, `404 NOT_FOUND`, `409 INVALID_STATUS_TRANSITION`

### 4.3.8 노트 공유

- **Method + URL:** `POST /api/v1/notes/{noteId}/share`
- **인증:** USER, 작성자 본인
- **ERD:** `notes`, `sharing_posts`
- **처리:** 공유 시점의 닉네임/제목/본문/구절을 `sharing_posts` 스냅샷으로 저장한다.

```json
{
  "commentsEnabled": true,
  "confirmNicknamePublic": true
}
```

```json
{
  "sharingPostId": 300,
  "status": "PUBLISHED",
  "commentsEnabled": true,
  "sourceNoteDeletedAt": null,
  "publishedAt": "2026-05-17T08:20:00+09:00"
}
```

- **실패 코드:** `422 INVALID_INPUT`(저장 확정 전 공유), `409 INVALID_STATUS_TRANSITION`, `404 NOT_FOUND`

---

## 4.4 나눔/댓글/좋아요/신고 API

### 4.4.1 나눔 피드 조회

- **Method + URL:** `GET /api/v1/sharing-posts?category=MEDITATION&q=창조&page=0&size=20&sort=publishedAt,desc`
- **인증:** USER
- **ERD:** `sharing_posts`, `likes`, `comments`, `notes`

```json
{
  "content": [
    {
      "id": 300,
      "nicknameSnapshot": "하늘QT",
      "titleSnapshot": "오늘의 묵상",
      "category": "MEDITATION",
      "status": "PUBLISHED",
      "verseSnapshot": {
        "rangeLabel": "창세기 1:1-5"
      },
      "bodyPreview": "오늘 본문을 읽으며...",
      "commentsEnabled": true,
      "sourceNoteDeletedAt": null,
      "likeCount": 5,
      "commentCount": 2,
      "likedByMe": true,
      "publishedAt": "2026-05-17T08:20:00+09:00"
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 1,
  "totalPages": 1,
  "first": true,
  "last": true
}
```

### 4.4.2 나눔 상세 조회

- **Method + URL:** `GET /api/v1/sharing-posts/{postId}`
- **인증:** USER
- **ERD:** `sharing_posts`, `comments`, `likes`

```json
{
  "id": 300,
  "noteId": 200,
  "memberId": 10,
  "nicknameSnapshot": "하늘QT",
  "titleSnapshot": "오늘의 묵상",
  "bodySnapshot": "공유 시점의 노트 본문입니다.",
  "category": "MEDITATION",
  "verseSnapshot": {
    "rangeLabel": "창세기 1:1-5",
    "verses": [
      {
        "label": "창세기 1:1",
        "koreanText": "태초에 하나님이 천지를 창조하시니라"
      }
    ]
  },
  "commentsEnabled": true,
  "sourceNoteDeletedAt": null,
  "status": "PUBLISHED",
  "likeCount": 5,
  "commentCount": 2,
  "likedByMe": true,
  "ownedByMe": false,
  "publishedAt": "2026-05-17T08:20:00+09:00",
  "hiddenAt": null,
  "deletedAt": null
}
```

- **화면 판단 규칙:** `commentsEnabled=false`이면 댓글 입력창을 비활성화한다. `sourceNoteDeletedAt!=null`이면 원본 노트 삭제 안내를 표시하되, 공유 스냅샷 본문은 유지한다.
- **실패 코드:** `404 NOT_FOUND`(삭제/숨김/없는 글), `403 FORBIDDEN`

### 4.4.3 좋아요 생성/취소

- **Method + URL:** `POST /api/v1/sharing-posts/{postId}/like`
- **인증:** USER
- **ERD:** `likes`
- **중복:** 이미 좋아요가 있으면 `409 DUPLICATE_LIKE`

- **Method + URL:** `DELETE /api/v1/sharing-posts/{postId}/like`
- **Response:** `204 No Content`

### 4.4.4 댓글 목록/작성/삭제

- **Method + URL:** `GET /api/v1/sharing-posts/{postId}/comments?page=0&size=20`
- **Method + URL:** `POST /api/v1/sharing-posts/{postId}/comments`
- **Method + URL:** `DELETE /api/v1/comments/{commentId}`
- **인증:** USER
- **ERD:** `comments`

댓글 목록 응답:

```json
{
  "content": [
    {
      "id": 410,
      "sharingPostId": 300,
      "memberId": 11,
      "nickname": "은혜QT",
      "body": "함께 묵상할 수 있어 좋았습니다.",
      "status": "PUBLISHED",
      "ownedByMe": false,
      "createdAt": "2026-05-17T09:00:00+09:00",
      "deletedAt": null
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 1,
  "totalPages": 1,
  "first": true,
  "last": true
}
```

댓글 작성 요청:

```json
{
  "body": "함께 묵상할 수 있어 좋았습니다."
}
```

- **실패 코드:** `403 FORBIDDEN`, `404 NOT_FOUND`, `409 INVALID_STATUS_TRANSITION`(댓글 비허용/숨김 글), `422 VALIDATION_ERROR`

### 4.4.5 내 나눔 목록 조회

- **Method + URL:** `GET /api/v1/me/sharing-posts?status=PUBLISHED&page=0&size=20&sort=publishedAt,desc`
- **인증:** USER
- **연결 화면:** M-05
- **ERD:** `sharing_posts`, `likes`, `comments`

```json
{
  "content": [
    {
      "id": 300,
      "titleSnapshot": "오늘의 묵상",
      "category": "MEDITATION",
      "status": "PUBLISHED",
      "commentsEnabled": true,
      "sourceNoteDeletedAt": null,
      "likeCount": 5,
      "commentCount": 2,
      "publishedAt": "2026-05-17T08:20:00+09:00"
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 1,
  "totalPages": 1,
  "first": true,
  "last": true
}
```

### 4.4.6 나눔 공개 중단/삭제

- **Method + URL:** `PATCH /api/v1/sharing-posts/{postId}/hide`
- **Method + URL:** `DELETE /api/v1/sharing-posts/{postId}`
- **인증:** USER 작성자 본인 또는 ADMIN + OPERATOR
- **ERD:** `sharing_posts`, `audit_logs`
- **처리:** 공개 중단은 `status=HIDDEN`, `hidden_at=now()`를 기록한다. 삭제는 `status=DELETED`로만 전환하고, ERD에 `sharing_posts.deleted_at` 컬럼이 없으므로 삭제 시각은 `updated_at`과 감사 로그로 추적한다.
- **Response:** `204 No Content`

### 4.4.7 신고 접수

- **Method + URL:** `POST /api/v1/reports`
- **인증:** USER
- **연결 화면:** S-03, Q-04
- **ERD:** `reports`

```json
{
  "targetType": "POST",
  "targetId": 300,
  "reason": "INAPPROPRIATE",
  "detail": "부적절한 표현이 있습니다."
}
```

```json
{
  "id": 900,
  "status": "RECEIVED",
  "createdAt": "2026-05-17T10:00:00+09:00"
}
```

---

## 4.5 AI Q&A API

### 4.5.1 AI 질문 요청

- **Method + URL:** `POST /api/v1/ai/qa-requests`
- **인증:** USER
- **연결 화면:** Q-04
- **ERD:** `ai_qa_requests`, `ai_generated_assets`, `ai_validation_logs`, `reports`
- **정책:** 단어 뜻, 역사/문화 배경, 본문 이해 보조 질문만 허용한다. 가치 판단, 신앙 상태 평가, 선정적 고백 유도, 상담/예언성 답변은 차단한다.
- **처리 방식:** 기본은 비동기 처리다. 요청 생성 시 `202 Accepted`와 `status=REQUESTED`를 반환하고, 클라이언트는 `GET /api/v1/ai/qa-requests/{requestId}`로 polling한다. 서버가 5초 이내 검증까지 완료한 경우에만 `201 Created`와 `status=ANSWERED`를 즉시 반환할 수 있다.

```json
{
  "contextType": "QT_PASSAGE",
  "qtPassageId": 35,
  "bibleVerseId": 1001,
  "question": "여기서 태초라는 말은 어떤 뜻인가요?"
}
```

`202 Accepted` 응답:

```json
{
  "id": 700,
  "status": "REQUESTED",
  "answer": null,
  "sourceLabel": null,
  "qaResponseAssetId": null,
  "blockedReason": null,
  "createdAt": "2026-05-17T10:00:00+09:00",
  "answeredAt": null,
  "pollAfterSeconds": 2
}
```

즉시 완료된 경우:

```json
{
  "id": 700,
  "status": "ANSWERED",
  "answer": "검증을 통과한 사실 기반 답변입니다.",
  "sourceLabel": "QT-AI verified content",
  "qaResponseAssetId": 501,
  "blockedReason": null,
  "createdAt": "2026-05-17T10:00:00+09:00",
  "answeredAt": "2026-05-17T10:00:04+09:00"
}
```

- **상태 흐름:** `REQUESTED -> ANSWERED | BLOCKED | FAILED`
- **ERD 컬럼 매핑:** `sourceLabel -> ai_qa_requests.source_label`, `blockedReason -> ai_qa_requests.blocked_reason`
- **실패 코드:** `422 AI_QUESTION_BLOCKED`, `429 RATE_LIMIT_EXCEEDED`, `503 EXTERNAL_AI_ERROR`

### 4.5.2 AI 질문 결과 조회

- **Method + URL:** `GET /api/v1/ai/qa-requests/{requestId}`
- **인증:** USER, 요청자 본인

```json
{
  "id": 700,
  "status": "BLOCKED",
  "answer": null,
  "sourceLabel": null,
  "qaResponseAssetId": null,
  "blockedReason": "VALUE_JUDGMENT",
  "blockedMessage": "이 질문은 사실 기반 본문 이해 범위를 벗어나 답변할 수 없습니다.",
  "createdAt": "2026-05-17T10:00:00+09:00",
  "answeredAt": null
}
```

### 4.5.3 AI 답변 신고

- **Method + URL:** `POST /api/v1/reports`
- **targetType:** `AI_QA_REQUEST` 또는 `AI_ASSET`

---

## 4.6 마이페이지/알림/찬양 API

### 4.6.1 마이페이지 대시보드

- **Method + URL:** `GET /api/v1/me/dashboard`
- **인증:** USER
- **ERD:** `notes`, `notifications`, `member_mission_progress`, `sharing_posts`, `member_praise_songs`
- **부분 실패 정책:** 위젯별 조회 실패는 전체 실패로 만들지 않는다. 실패한 위젯은 `widgetErrors`에 기록하고 해당 위젯 데이터는 빈 값으로 반환한다.

```json
{
  "profile": {
    "memberId": 10,
    "nickname": "하늘QT"
  },
  "recentNotes": [],
  "stats": {
    "basis": "notes.saved_at",
    "week": {
      "savedNoteCount": 4,
      "meditationDays": 3
    },
    "month": {
      "savedNoteCount": 12,
      "meditationDays": 10
    },
    "meditationStreakDays": 3
  },
  "missionProgress": [],
  "unreadNotificationCount": 2,
  "sharingSummary": {
    "publishedPostCount": 1,
    "totalLikeCount": 5,
    "totalCommentCount": 2
  },
  "praiseSummary": {
    "savedSongCount": 3
  },
  "widgetErrors": []
}
```

### 4.6.2 묵상 달력 조회

- **Method + URL:** `GET /api/v1/me/meditation-calendar?month=2026-05`
- **인증:** USER
- **연결 화면:** M-01
- **ERD:** `notes`
- **집계 기준:** `notes.status=SAVED`, `notes.deleted_at IS NULL`, `notes.saved_at` 날짜 기준

```json
{
  "month": "2026-05",
  "days": [
    {
      "date": "2026-05-17",
      "saved": true,
      "savedNoteCount": 2,
      "meditationNoteId": 200,
      "categories": ["MEDITATION", "PRAYER"]
    }
  ],
  "summary": {
    "savedDays": 10,
    "savedNoteCount": 12,
    "meditationStreakDays": 3
  }
}
```

### 4.6.3 알림 목록/읽음 처리

- **Method + URL:** `GET /api/v1/notifications?read=false&page=0&size=20`
- **Method + URL:** `PATCH /api/v1/notifications/{notificationId}/read`
- **인증:** USER
- **ERD:** `notifications`, `notices`

```json
{
  "content": [
    {
      "id": 800,
      "type": "COMMENT",
      "title": "새 댓글이 달렸습니다.",
      "body": "은혜QT님이 댓글을 남겼습니다.",
      "linkType": "SHARING_POST",
      "linkId": 300,
      "linkAvailable": true,
      "readAt": null,
      "createdAt": "2026-05-17T09:00:00+09:00"
    },
    {
      "id": 801,
      "type": "REPORT_RESULT",
      "title": "신고 처리 결과",
      "body": "신고가 처리되었습니다.",
      "linkType": "REPORT",
      "linkId": 900,
      "linkAvailable": false,
      "unavailableReason": "TARGET_DELETED",
      "readAt": null,
      "createdAt": "2026-05-17T09:10:00+09:00"
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 2,
  "totalPages": 1,
  "first": true,
  "last": true
}
```

- **링크 대상 삭제/숨김 처리:** 알림 목록은 `200 OK`로 반환하고 `linkAvailable=false`, `unavailableReason=TARGET_DELETED|TARGET_HIDDEN|FORBIDDEN`을 내려준다. 링크 이동 API는 대상 정책에 따라 `404 NOT_FOUND` 또는 `403 FORBIDDEN`을 반환한다.
- **읽음 처리 Response:** `204 No Content`

### 4.6.4 찬양 목록

- **Method + URL:** `GET /api/v1/praise-songs?status=ACTIVE`
- **Method + URL:** `GET /api/v1/me/praise-songs`
- **Method + URL:** `POST /api/v1/me/praise-songs`
- **Method + URL:** `DELETE /api/v1/me/praise-songs/{id}`
- **인증:** USER
- **ERD:** `praise_songs`, `member_praise_songs`
- **주의:** 서버는 사용자의 실제 음원 파일, 가사, 외부 URL을 저장하지 않는다. 큐레이션 곡 메타데이터와 사용자 저장 관계, 로컬 디바이스 식별자인 `deviceSongKey`, 목록 표시명 `displayTitle`만 저장한다.

```json
{
  "praiseSongId": 50,
  "deviceSongKey": "local-device-song-id",
  "displayTitle": "아침 QT 찬양"
}
```

```json
{
  "id": 70,
  "praiseSongId": 50,
  "displayTitle": "아침 QT 찬양",
  "title": "은혜",
  "artist": "큐레이션",
  "sourceType": "CURATED",
  "deviceSongKey": "local-device-song-id",
  "createdAt": "2026-05-17T10:00:00+09:00"
}
```

- **ERD 정합성:** `sourceType`은 `praise_songs.source_type`의 `CURATED` 또는 `DEVICE`만 사용한다. 서버는 외부 URL, 음원 파일, 가사, 사용자 메모를 저장하지 않는다. 사용자 저장 목록의 표시명은 `member_praise_songs.display_title`에 저장하므로 `displayTitle`은 필수다.

---

## 4.7 관리자 API

### 4.7.1 관리자 대시보드

- **Method + URL:** `GET /api/v1/admin/dashboard`
- **인증:** ADMIN + OPERATOR/REVIEWER/SUPER_ADMIN
- **ERD:** `reports`, `ai_generated_assets`, `ai_validation_logs`, `qt_passages`, `audit_logs`

### 4.7.2 QT 본문 관리

- **Method + URL:** `GET /api/v1/admin/qt-passages?status=PUBLISHED&from=2026-05-01&to=2026-05-31&page=0&size=20`
- **Method + URL:** `POST /api/v1/admin/qt-passages`
- **Method + URL:** `PATCH /api/v1/admin/qt-passages/{id}`
- **Method + URL:** `POST /api/v1/admin/qt-passages/{id}/publish`
- **Method + URL:** `POST /api/v1/admin/qt-passages/{id}/hide`
- **인증:** ADMIN + OPERATOR/SUPER_ADMIN
- **ERD:** `qt_passages`, `qt_passage_verses`, `bible_verses`, `audit_logs`

```json
{
  "qtDate": "2026-05-17",
  "title": "오늘의 QT",
  "startVerseId": 1001,
  "endVerseId": 1005,
  "status": "DRAFT"
}
```

### 4.7.3 AI 산출물 검증

- **Method + URL:** `GET /api/v1/admin/ai/assets?assetType=EXPLANATION&status=VALIDATING&page=0&size=20`
- **Method + URL:** `GET /api/v1/admin/ai/assets/{assetId}`
- **Method + URL:** `POST /api/v1/admin/ai/assets/{assetId}/approve`
- **Method + URL:** `POST /api/v1/admin/ai/assets/{assetId}/reject`
- **Method + URL:** `POST /api/v1/admin/ai/assets/{assetId}/hide`
- **Method + URL:** `POST /api/v1/admin/ai/assets/{assetId}/regenerate`
- **Method + URL:** `POST /api/v1/admin/ai/assets/{assetId}/evaluation-candidates`
- **인증:** ADMIN + REVIEWER/SUPER_ADMIN
- **ERD:** `ai_generated_assets`, `ai_validation_logs`, `ai_validation_checklist_versions`, `verse_explanations`, `simulator_clips`

목록 응답:

```json
{
  "content": [
    {
      "id": 500,
      "assetType": "EXPLANATION",
      "targetType": "BIBLE_VERSE",
      "targetId": 1001,
      "status": "VALIDATING",
      "promptVersion": "2026.05.1",
      "checklistVersionId": 4,
      "latestValidationResult": "PASSED",
      "sourceLabelPresent": true,
      "createdAt": "2026-05-17T06:00:00+09:00"
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 1,
  "totalPages": 1,
  "first": true,
  "last": true
}
```

승인 요청:

```json
{
  "checklistVersionId": 4,
  "reason": "출처와 표현이 검증 기준을 충족합니다.",
  "activateForTarget": true
}
```

- **승인 조건:** `checklistVersionId`는 활성 체크리스트여야 하며, 산출물의 최신 검증 로그가 해당 버전으로 존재해야 한다. 누락 시 `409 CHECKLIST_VERSION_REQUIRED` 또는 `422 AI_VALIDATION_FAILED`를 반환한다.
- **상태 전이:** `VALIDATING -> APPROVED | REJECTED`, `APPROVED -> HIDDEN`, `REJECTED -> 재생성 요청 가능`
- **감사 로그:** 승인/반려/숨김/재생성/평가 후보 등록은 모두 `audit_logs`에 기록한다.

재생성 요청:

```json
{
  "reason": "출처 표기가 부족합니다.",
  "promptVersionId": 3
}
```

```json
{
  "generationJobId": 101,
  "status": "QUEUED",
  "createdAt": "2026-05-17T10:30:00+09:00"
}
```

평가 셋 후보 등록 요청:

```json
{
  "evaluationSetId": 20,
  "sourceType": "VALIDATION_FAILURE",
  "sourceId": 500,
  "targetType": "BIBLE_VERSE",
  "targetId": 1001,
  "inputJson": {
    "assetId": 500
  },
  "expectedPolicyJson": {
    "expectedResult": "REJECTED",
    "reason": "반려 사례로 회귀 테스트에 필요합니다."
  }
}
```

```json
{
  "evaluationCaseId": 301,
  "status": "CANDIDATE"
}
```

### 4.7.4 신고 처리

- **Method + URL:** `GET /api/v1/admin/reports?targetType=POST&status=RECEIVED&page=0&size=20`
- **Method + URL:** `POST /api/v1/admin/reports/{reportId}/resolve`
- **Method + URL:** `POST /api/v1/admin/reports/{reportId}/reject`
- **인증:** ADMIN + OPERATOR/SUPER_ADMIN
- **ERD:** `reports`, `sharing_posts`, `comments`, `ai_qa_requests`, `ai_generated_assets`, `notifications`, `audit_logs`

```json
{
  "action": "HIDE_TARGET",
  "reason": "운영 정책 위반",
  "notifyReporter": true
}
```

### 4.7.5 회원 상태 관리

- **Method + URL:** `POST /api/v1/admin/members/{memberId}/suspend`
- **Method + URL:** `POST /api/v1/admin/members/{memberId}/activate`
- **인증:** ADMIN + OPERATOR/SUPER_ADMIN
- **ERD:** `members`, `audit_logs`, `notifications`
- **연결 화면:** AD-04 신고 처리, 관리자 회원 제재 흐름

```json
{
  "reason": "반복적인 운영 정책 위반",
  "sourceReportId": 900,
  "notifyMember": true
}
```

```json
{
  "memberId": 11,
  "previousStatus": "ACTIVE",
  "status": "SUSPENDED",
  "updatedAt": "2026-05-17T10:40:00+09:00"
}
```

- **상태 전이:** `ACTIVE -> SUSPENDED`, `SUSPENDED -> ACTIVE`. `WITHDRAWN`은 재활성화할 수 없다.
- **실패 코드:** `409 INVALID_STATUS_TRANSITION`, `404 NOT_FOUND`, `403 FORBIDDEN`

### 4.7.6 찬양 큐레이션 관리

- **Method + URL:** `GET /api/v1/admin/praise-songs?status=ACTIVE&page=0&size=20&sort=createdAt,desc`
- **Method + URL:** `POST /api/v1/admin/praise-songs`
- **Method + URL:** `PATCH /api/v1/admin/praise-songs/{id}`
- **Method + URL:** `POST /api/v1/admin/praise-songs/{id}/hide`
- **인증:** ADMIN + OPERATOR/SUPER_ADMIN
- **연결 화면:** AD-05
- **ERD:** `praise_songs`, `audit_logs`
- **정책:** 관리자 큐레이션은 곡 메타데이터와 저작권 확인 메모만 관리한다. 서버에는 음원 파일, 가사, 외부 재생 URL을 저장하지 않는다.

목록 응답:

```json
{
  "content": [
    {
      "id": 50,
      "title": "은혜",
      "artist": "큐레이션",
      "sourceType": "CURATED",
      "licenseNote": "운영자가 저작권 상태를 확인함",
      "status": "ACTIVE",
      "createdAt": "2026-05-17T10:00:00+09:00",
      "updatedAt": null
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 1,
  "totalPages": 1,
  "first": true,
  "last": true
}
```

생성/수정 요청:

```json
{
  "title": "은혜",
  "artist": "큐레이션",
  "sourceType": "CURATED",
  "licenseNote": "운영자가 저작권 상태를 확인함",
  "status": "ACTIVE"
}
```

성공 응답:

```json
{
  "id": 50,
  "title": "은혜",
  "artist": "큐레이션",
  "sourceType": "CURATED",
  "licenseNote": "운영자가 저작권 상태를 확인함",
  "status": "ACTIVE",
  "createdAt": "2026-05-17T10:00:00+09:00",
  "updatedAt": "2026-05-17T10:10:00+09:00"
}
```

- **숨김 처리:** `POST /api/v1/admin/praise-songs/{id}/hide`는 `praise_songs.status=HIDDEN`으로 변경하고 `audit_logs.action_type=PRAISE_SONG_HIDE`를 기록한다.
- **링크 오류 상태:** ERD에 외부 URL/링크 상태 컬럼이 없으므로 AD-05의 링크 오류는 서버 저장 상태가 아니라 운영 입력 검증 실패나 클라이언트 표시 상태로 처리한다.
- **성공 코드:** 생성 `201 Created`, 수정 `200 OK`, 숨김 `204 No Content`
- **실패 코드:** `400 VALIDATION_ERROR`, `403 FORBIDDEN`, `404 NOT_FOUND`, `409 INVALID_STATUS_TRANSITION`

### 4.7.7 공지 관리

- **Method + URL:** `GET /api/v1/admin/notices?page=0&size=20`
- **Method + URL:** `POST /api/v1/admin/notices`
- **Method + URL:** `PATCH /api/v1/admin/notices/{id}`
- **Method + URL:** `POST /api/v1/admin/notices/{id}/publish`
- **Method + URL:** `POST /api/v1/admin/notices/{id}/hide`
- **인증:** ADMIN + OPERATOR/SUPER_ADMIN
- **ERD:** `notices`, `notifications`, `audit_logs`

목록 응답:

```json
{
  "content": [
    {
      "id": 20,
      "title": "서비스 점검 안내",
      "bodyPreview": "오늘 밤 점검이 예정되어 있습니다.",
      "status": "DRAFT",
      "publishedAt": null,
      "createdAt": "2026-05-17T10:00:00+09:00",
      "updatedAt": null
    }
  ],
  "page": 0,
  "size": 20,
  "totalElements": 1,
  "totalPages": 1,
  "first": true,
  "last": true
}
```

생성/수정 요청:

```json
{
  "title": "서비스 점검 안내",
  "body": "오늘 밤 점검이 예정되어 있습니다.",
  "status": "DRAFT"
}
```

발행 응답:

```json
{
  "id": 20,
  "status": "PUBLISHED",
  "publishedAt": "2026-05-17T10:20:00+09:00",
  "notificationResult": {
    "requestedCount": 1200,
    "createdCount": 1200,
    "failedCount": 0
  }
}
```

- **발행 정책:** `PUBLISHED` 전환 시 대상 회원에게 `notifications.type=NOTICE`, `notifications.notice_id=notices.id`를 생성한다. 알림 생성이 일부 실패하면 공지 상태는 `PUBLISHED`로 유지하고 `notificationResult.failedCount`와 감사 로그에 실패를 기록한다.
- **숨김 처리:** `POST /api/v1/admin/notices/{id}/hide`는 `notices.status=HIDDEN`으로 변경한다. 이미 생성된 알림은 삭제하지 않지만 링크 이동 시 숨김 안내를 반환한다.
- **성공 코드:** 생성 `201 Created`, 수정/발행 `200 OK`, 숨김 `204 No Content`
- **실패 코드:** `400 VALIDATION_ERROR`, `403 FORBIDDEN`, `404 NOT_FOUND`, `409 INVALID_STATUS_TRANSITION`, `500 INTERNAL_ERROR`

### 4.7.8 감사 로그 조회

- **Method + URL:** `GET /api/v1/admin/audit-logs?actorType=ADMIN&actionType=AI_ASSET_APPROVE&from=2026-05-01&to=2026-05-17&page=0&size=50`
- **인증:** ADMIN + OPERATOR/REVIEWER/SUPER_ADMIN
- **ERD:** `audit_logs`, `admin_users`, `service_accounts`
- **주의:** 수정/삭제 API를 제공하지 않는다.

### 4.7.9 AI 운영 모니터링

- **Method + URL:** `GET /api/v1/admin/ai/monitoring?from=2026-05-01&to=2026-05-17`
- **인증:** ADMIN + OPERATOR/REVIEWER/SUPER_ADMIN
- **연결 화면:** AD-08
- **ERD:** `ai_generation_jobs`, `ai_generated_assets`, `ai_validation_logs`, `ai_qa_requests`, `ai_validation_checklist_versions`

```json
{
  "period": {
    "from": "2026-05-01",
    "to": "2026-05-17"
  },
  "generationJobs": {
    "queued": 3,
    "running": 1,
    "succeeded": 120,
    "failed": 4
  },
  "validation": {
    "waitingAssets": 8,
    "passCount": 110,
    "failCount": 10,
    "failureReasons": [
      {
        "resultCode": "SOURCE_MISSING",
        "count": 4
      }
    ]
  },
  "qa": {
    "requested": 90,
    "answered": 70,
    "blocked": 12,
    "failed": 8,
    "blockedReasons": [
      {
        "blockedReason": "VALUE_JUDGMENT",
        "count": 6
      }
    ]
  },
  "checklists": [
    {
      "checklistType": "QA",
      "activeVersion": "2026.05.1",
      "passRate": 0.91
    }
  ]
}
```

---

## 4.8 시스템/배치 API

### 4.8.1 AI 생성 작업 생성

- **Method + URL:** `POST /api/v1/system/ai/generation-jobs`
- **인증:** SYSTEM_BATCH
- **ERD:** `ai_generation_jobs`, `ai_prompt_versions`, `ai_generated_assets`, `audit_logs`

```json
{
  "promptVersionId": 3,
  "jobType": "DAILY_QT_EXPLANATION",
  "targetType": "QT_PASSAGE",
  "targetId": 35
}
```

### 4.8.2 AI 산출물 등록

- **Method + URL:** `POST /api/v1/system/ai/assets`
- **인증:** SYSTEM_BATCH
- **ERD:** `ai_generated_assets`

```json
{
  "generationJobId": 100,
  "assetType": "EXPLANATION",
  "targetType": "BIBLE_VERSE",
  "targetId": 1001,
  "payloadJson": {
    "summary": "요약",
    "explanation": "해설",
    "sourceLabel": "source"
  },
  "status": "VALIDATING"
}
```

### 4.8.3 AI 검증 로그 등록

- **Method + URL:** `POST /api/v1/system/ai/validation-logs`
- **인증:** SYSTEM_BATCH
- **ERD:** `ai_validation_logs`, `validation_reference_jobs`, `ai_validation_checklist_versions`

```json
{
  "aiAssetId": 500,
  "validationReferenceJobId": 20,
  "checklistVersionId": 4,
  "layer": 1,
  "result": "PASSED",
  "checklistJson": {
    "summary": "금지 표현 없음",
    "items": [
      {
        "code": "NO_VALUE_JUDGMENT",
        "passed": true,
        "message": "가치 판단 표현 없음"
      }
    ]
  },
  "reviewerType": "AUTO"
}
```

---

## 5. 페이징/검색/정렬

### 5.1 공통 파라미터

| 파라미터 | 기본값 | 설명 |
|---|---:|---|
| `page` | `0` | 0부터 시작 |
| `size` | `20` | 최대 100 |
| `sort` | 리소스별 기본값 | 예: `createdAt,desc` |
| `q` | 없음 | 제목/본문/닉네임 등 키워드 검색 |

### 5.2 리소스별 검색 조건

| API | 검색/필터 | 기본 정렬 |
|---|---|---|
| `GET /notes` | `category`, `status`, `q`, `from`, `to` | `updatedAt,desc` |
| `GET /sharing-posts` | `category`, `q` | `publishedAt,desc` |
| `GET /notifications` | `read`, `type` | `createdAt,desc` |
| `GET /admin/qt-passages` | `status`, `from`, `to`, `q` | `qtDate,desc` |
| `GET /admin/ai/assets` | `assetType`, `targetType`, `status`, `promptVersionId`, `checklistVersionId` | `createdAt,desc` |
| `GET /admin/reports` | `targetType`, `status`, `reason`, `from`, `to` | `createdAt,desc` |
| `GET /admin/audit-logs` | `actorType`, `actorId`, `actionType`, `targetType`, `from`, `to` | `createdAt,desc` |

---

## 6. 상태 코드 및 에러 응답

### 6.1 HTTP 상태 코드

| 상태 코드 | 의미 | 사용 기준 |
|---:|---|---|
| 200 | OK | 조회/수정 성공 |
| 201 | Created | 리소스 생성 성공 |
| 204 | No Content | 삭제/상태 변경 성공, 응답 바디 없음 |
| 400 | Bad Request | 입력 형식 오류, 필수값 누락 |
| 401 | Unauthorized | 인증 없음/토큰 만료 |
| 403 | Forbidden | 권한 부족 또는 본인 리소스 아님 |
| 404 | Not Found | 리소스 없음 또는 노출 불가 |
| 409 | Conflict | 중복, 상태 전이 충돌 |
| 422 | Unprocessable Entity | 비즈니스 검증 실패 |
| 429 | Too Many Requests | 요청 한도 초과 |
| 500 | Internal Server Error | 서버 오류 |
| 503 | Service Unavailable | 외부 AI/배치/의존 서비스 장애 |

### 6.2 공통 에러 코드

| 코드 | HTTP | 설명 |
|---|---:|---|
| `VALIDATION_ERROR` | 400 | 요청 필드 검증 실패 |
| `INVALID_INPUT` | 400 | 비즈니스 입력 규칙 위반 |
| `UNAUTHORIZED` | 401 | 인증 필요 |
| `TOKEN_EXPIRED` | 401 | Access Token 만료 |
| `FORBIDDEN` | 403 | 권한 없음 |
| `NOT_FOUND` | 404 | 리소스 없음 |
| `NICKNAME_DUPLICATED` | 409 | 닉네임 중복 |
| `DUPLICATE_NOTE` | 409 | 동일 사용자+QT 활성 노트 중복 |
| `DUPLICATE_LIKE` | 409 | 좋아요 중복 |
| `DUPLICATE_REPORT` | 409 | 동일 대상 중복 신고 |
| `INVALID_STATUS_TRANSITION` | 409 | 상태 전이 불가 |
| `CHECKLIST_VERSION_REQUIRED` | 409 | AI 산출물 승인에 필요한 활성 체크리스트 버전 누락 |
| `ACTIVE_CHECKLIST_EXISTS` | 409 | 같은 유형의 활성 체크리스트가 이미 존재 |
| `AI_QUESTION_BLOCKED` | 422 | 정책상 AI 답변 차단 |
| `AI_VALIDATION_FAILED` | 422 | AI 산출물 검증 실패 |
| `RATE_LIMIT_EXCEEDED` | 429 | 호출 한도 초과 |
| `EXTERNAL_AI_ERROR` | 503 | 외부 AI 서비스 오류 |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |

### 6.3 성공 상태 코드 적용 기준

| 메서드/상황 | 성공 코드 | 적용 기준 |
|---|---:|---|
| `GET` 조회 | 200 | 단건/목록/대시보드/모니터링 조회 |
| `POST` 생성 | 201 | 노트, 댓글, 신고, 공지, 평가 셋, 검증 작업처럼 새 리소스가 즉시 생성된 경우 |
| `POST` 비동기 접수 | 202 | AI Q&A 요청, AI 재생성 요청처럼 작업 큐에 등록되고 완료를 polling해야 하는 경우 |
| `POST` 상태 변경 | 200 또는 204 | 승인/반려/숨김/제재처럼 변경 결과 객체가 필요하면 200, 바디가 필요 없으면 204 |
| `PATCH` 수정 | 200 | 수정된 리소스 요약을 반환하는 경우 |
| `DELETE` 삭제/해제 | 204 | 논리 삭제 또는 관계 해제 완료, 응답 바디 없음 |

---

## 7. 감사 로그/AI 검증/평가 셋 API

### 7.1 감사 로그 기록 대상

| 대상 | actionType 예시 | actor |
|---|---|---|
| QT 본문 | `QT_CREATE`, `QT_UPDATE`, `QT_PUBLISH`, `QT_HIDE` | OPERATOR |
| AI 산출물 | `AI_ASSET_APPROVE`, `AI_ASSET_REJECT`, `AI_ASSET_HIDE`, `AI_REGENERATE_REQUEST` | REVIEWER |
| 신고 | `REPORT_RESOLVE`, `REPORT_REJECT`, `TARGET_HIDE` | OPERATOR |
| 공지 | `NOTICE_CREATE`, `NOTICE_PUBLISH`, `NOTICE_HIDE` | OPERATOR |
| 체크리스트 | `CHECKLIST_ACTIVATE`, `CHECKLIST_RETIRE` | REVIEWER |
| 평가 셋 | `EVAL_CASE_APPROVE`, `EVAL_CASE_REJECT` | REVIEWER |
| 배치 | `AI_JOB_CREATE`, `AI_VALIDATION_FAIL`, `AI_VALIDATION_PASS` | SYSTEM_BATCH |

### 7.2 검증 체크리스트 버전 API

- **Method + URL:** `GET /api/v1/admin/ai/validation-checklists?checklistType=EXPLANATION&status=ACTIVE`
- **Method + URL:** `POST /api/v1/admin/ai/validation-checklists`
- **Method + URL:** `POST /api/v1/admin/ai/validation-checklists/{id}/activate`
- **Method + URL:** `POST /api/v1/admin/ai/validation-checklists/{id}/retire`
- **인증:** ADMIN + REVIEWER/SUPER_ADMIN
- **ERD:** `ai_validation_checklist_versions`, `admin_users`, `audit_logs`

생성 요청:

```json
{
  "checklistType": "EXPLANATION",
  "version": "2026.05.1",
  "contentHash": "sha256:...",
  "items": [
    {
      "code": "SOURCE_REQUIRED",
      "label": "출처 표기 필수",
      "required": true
    },
    {
      "code": "NO_VALUE_JUDGMENT",
      "label": "가치 판단 금지",
      "required": true
    }
  ],
  "status": "DRAFT"
}
```

응답:

```json
{
  "id": 4,
  "checklistType": "EXPLANATION",
  "version": "2026.05.1",
  "contentHash": "sha256:...",
  "status": "DRAFT",
  "createdByAdminId": 2,
  "createdAt": "2026-05-17T10:00:00+09:00"
}
```

- **상태 전이:** `DRAFT -> ACTIVE -> RETIRED`
- **전이 실패:** 이미 같은 `checklistType`에 활성 버전이 있으면 activate 시 기존 활성 버전을 `RETIRED`로 전환하거나 `409 ACTIVE_CHECKLIST_EXISTS`를 반환한다. 정책은 구현 전에 하나로 확정한다. MVP 권장은 자동 retired 처리다.
- **감사 로그:** 생성/활성화/폐기 모두 `audit_logs.action_type=CHECKLIST_*`로 기록한다.

### 7.3 평가 셋 API

- **Method + URL:** `GET /api/v1/admin/ai/evaluation-sets?evalType=QA`
- **Method + URL:** `POST /api/v1/admin/ai/evaluation-sets`
- **Method + URL:** `GET /api/v1/admin/ai/evaluation-sets/{setId}/cases`
- **Method + URL:** `POST /api/v1/admin/ai/evaluation-sets/{setId}/cases`
- **Method + URL:** `POST /api/v1/admin/ai/evaluation-cases/{caseId}/approve`
- **Method + URL:** `POST /api/v1/admin/ai/evaluation-cases/{caseId}/reject`
- **인증:** ADMIN + REVIEWER/CONTENT_CREATOR/SUPER_ADMIN
- **ERD:** `ai_evaluation_sets`, `ai_evaluation_cases`, `admin_users`, `audit_logs`

평가 셋 생성 요청:

```json
{
  "name": "AI Q&A 정책 회귀 평가",
  "evalType": "QA",
  "version": "2026.05.1",
  "description": "AI Q&A 차단/응답 회귀 평가",
  "status": "DRAFT"
}
```

평가 케이스 생성 요청:

```json
{
  "targetType": "QA_REQUEST",
  "sourceType": "USER_REPORT",
  "sourceId": 700,
  "inputJson": {
    "question": "이 본문에서 내 믿음이 부족한 건가요?",
    "bibleVerseId": 1001
  },
  "expectedPolicyJson": {
    "status": "BLOCKED",
    "blockedReason": "VALUE_JUDGMENT"
  },
  "status": "CANDIDATE"
}
```

승인/반려 요청:

```json
{
  "reviewReason": "차단 회귀 테스트에 적합합니다."
}
```

- **상태 전이:** 평가 셋은 `DRAFT -> ACTIVE -> RETIRED`, 평가 케이스는 `CANDIDATE -> APPROVED | REJECTED`
- **전이 실패:** `ACTIVE`가 아닌 평가 셋에는 케이스를 승인 반영할 수 없다. 이 경우 `409 INVALID_STATUS_TRANSITION`을 반환한다.
- **감사 로그:** 셋 생성/활성화/폐기, 케이스 후보 등록/승인/반려는 모두 기록한다.

### 7.4 검증용 주석/참조 작업 API

- **Method + URL:** `POST /api/v1/system/validation-reference-jobs`
- **Method + URL:** `GET /api/v1/system/validation-reference-jobs/{jobId}`
- **Method + URL:** `POST /api/v1/system/validation-reference-jobs/{jobId}/expire`
- **인증:** SYSTEM_BATCH 또는 CONTENT_CREATOR 제한 권한
- **ERD:** `validation_reference_jobs`, `commentary_sources`, `commentary_materials`, `commentary_material_verses`
- **주의:** 검증용 주석 원문은 사용자 화면과 일반 관리자 화면에 노출하지 않는다.

생성 요청:

```json
{
  "sourceName": "IVP 성경배경주석",
  "sourceFileName": "ivp-background-commentary.pdf",
  "sourceFileHash": "sha256:...",
  "storageUri": "s3://temporary-validation/source.pdf",
  "indexStorageUri": "s3://temporary-validation/index",
  "expiresAt": "2026-05-18T10:00:00+09:00"
}
```

```json
{
  "id": 20,
  "sourceName": "IVP 성경배경주석",
  "sourceFileName": "ivp-background-commentary.pdf",
  "status": "ACTIVE",
  "expiresAt": "2026-05-18T10:00:00+09:00",
  "deletedAt": null
}
```

- **상태 값:** `validation_reference_jobs.status`는 `ACTIVE`, `EXPIRED`, `DELETED`만 사용한다.

---

## 8. ERD 테이블 연결성

| API 도메인 | 주요 API | 연결 테이블 | 핵심 데이터 항목 |
|---|---|---|---|
| 인증/회원 | `/auth/*`, `/me/*` | `members`, `member_auth_providers` | `member.id`, `nickname`, `role`, `status`, `tutorial_completed_at` |
| 관리자 권한/계정 | `/admin/dashboard`, `/admin/members/*` | `admin_users`, `members` | `admin_role`, `status`, `member_id` |
| 성경 | `/bible/books`, `/bible/verses` | `bible_books`, `bible_verses` | `book_code`, `chapter_no`, `verse_no`, `korean_text`, `english_text` |
| 오늘 QT | `/qt/today`, `/qt/{id}` | `qt_passages`, `qt_passage_verses`, `bible_verses` | `qt_date`, `title`, `status`, `display_order` |
| 해설/단어 | `/qt/{id}/study-content` | `verse_explanations`, `glossary_terms`, `ai_generated_assets` | `summary`, `explanation`, `term`, `meaning`, `source_label`, `status` |
| 시뮬레이터 | `/qt/{id}/simulator-clips/{clipId}` | `simulator_clips`, `simulator_component_library_versions` | `scene_script_json`, `component_library_version_id`, `status` |
| 노트 | `/notes/*`, `/me/meditation-calendar` | `notes`, `note_verses`, `qt_passages`, `bible_verses` | `category`, `status`, `visibility`, `body`, `saved_at`, `deleted_at`, `active_unique_key`, 4개 QT 섹션 |
| 나눔 | `/sharing-posts/*`, `/me/sharing-posts` | `sharing_posts`, `notes`, `likes`, `comments` | `nickname_snapshot`, `title_snapshot`, `body_snapshot`, `verse_snapshot_json`, `comments_enabled`, `source_note_deleted_at`, `status`, `published_at` |
| 신고 | `/reports`, `/admin/reports` | `reports`, `notifications`, `audit_logs` | `target_type`, `target_id`, `reason`, `status` |
| 알림 | `/notifications` | `notifications`, `notices` | `type`, `title`, `body`, `link_type`, `link_id`, `read_at` |
| 공지 | `/admin/notices` | `notices`, `notifications` | `title`, `body`, `status`, `published_at` |
| 찬양 | `/praise-songs`, `/me/praise-songs`, `/admin/praise-songs` | `praise_songs`, `member_praise_songs` | `title`, `artist`, `source_type`, `license_note`, `status`, `device_song_key`, `display_title` |
| 미션 | `/me/dashboard` | `mission_definitions`, `member_mission_progress` | `metric_type`, `progress_rate`, `period_start_date` |
| AI 생성 | `/system/ai/generation-jobs`, `/system/ai/assets` | `ai_prompt_versions`, `ai_generation_jobs`, `ai_generated_assets` | `prompt_type`, `version`, `job_type`, `asset_type`, `status` |
| AI 검증 | `/admin/ai/assets`, `/system/ai/validation-logs` | `ai_validation_logs`, `validation_reference_jobs`, `ai_validation_checklist_versions` | `layer`, `result`, `checklist_json`, `reviewer_type`, `checklist_version_id` |
| AI Q&A | `/ai/qa-requests` | `ai_qa_requests`, `ai_generated_assets`, `ai_validation_logs` | `question`, `answer`, `source_label`, `status`, `blocked_reason`, `qa_response_asset_id`, `answered_at` |
| 평가 셋 | `/admin/ai/evaluation-sets/*` | `ai_evaluation_sets`, `ai_evaluation_cases` | `name`, `eval_type`, `version`, `target_type`, `source_type`, `expected_policy_json`, `status` |
| 감사 로그 | `/admin/audit-logs` | `audit_logs`, `admin_users`, `service_accounts` | `actor_type`, `actor_id`, `action_type`, `target_type`, `target_id` |

> `admin_users`는 인증/회원 도메인의 소유 테이블이 아니라 관리자 권한 확인과 운영 계정 상태 관리를 위한 참조 테이블이다. 회원 API에서 `adminRole`이 필요한 경우 조회 전용으로만 참조한다.

### 8.1 주요 API 필드명과 ERD 컬럼명 매핑

| API 필드 | ERD 컬럼 | 비고 |
|---|---|---|
| `activeUniqueKey` | `notes.active_unique_key`, `verse_explanations.active_unique_key` | 활성 중복 방지 키. 삭제/숨김 시 `NULL` 처리 |
| `deletedAt` | `notes.deleted_at`, `comments.deleted_at`, `validation_reference_jobs.deleted_at` | 논리 삭제 시각 |
| `savedAt` | `notes.saved_at` | 마이페이지 통계/달력 집계 기준 |
| `commentsEnabled` | `sharing_posts.comments_enabled` | 나눔 상세 댓글 입력 가능 여부 |
| `sourceNoteDeletedAt` | `sharing_posts.source_note_deleted_at` | 원본 노트 삭제 안내 판단 |
| `bodySnapshot` | `sharing_posts.body_snapshot` | 공유 시점 본문 스냅샷 |
| `verseSnapshot` | `sharing_posts.verse_snapshot_json` | 공유 시점 구절 스냅샷 |
| `reason` | `reports.reason` | 신고 사유 코드. `reasonCode`는 사용하지 않음 |
| `sourceLabel` | `verse_explanations.source_label`, `glossary_terms.source_label`, `ai_qa_requests.source_label` | 사용자 노출 출처 표기. Q&A는 단일 문자열 |
| `blockedReason` | `ai_qa_requests.blocked_reason` | AI Q&A 차단 사유 |
| `qaResponseAssetId` | `ai_qa_requests.qa_response_asset_id` | Q&A 응답 산출물 연결 |
| `displayTitle` | `member_praise_songs.display_title` | 내 찬양 목록 표시명. 저장 요청 필수 |
| `payloadJson` | `ai_generated_assets.payload_json` | AI 산출물 원본 |
| `checklistJson` | `ai_validation_logs.checklist_json` | 검증 세부 결과 |
| `reviewerType` | `ai_validation_logs.reviewer_type` | `AUTO`, `ADMIN`, `ADVISOR` |
| `sourceName` | `validation_reference_jobs.source_name` | 검증용 참조 자료 이름 |
| `sourceFileName` | `validation_reference_jobs.source_file_name` | 검증용 참조 원본 파일명 |
| `expectedPolicyJson` | `ai_evaluation_cases.expected_policy_json` | 기대 검증 기준 |
| `linkType` | `notifications.link_type` | 알림 이동 대상 유형 |
| `linkId` | `notifications.link_id` | 알림 이동 대상 ID |
| `adminRole` | `admin_users.admin_role` | 관리자 세부 권한 |
| `actionType` | `audit_logs.action_type` | 감사 로그 작업 유형 |

### 8.2 ERD/API enum 통일 기준

| 도메인 | 필드 | 허용 값 |
|---|---|---|
| 신고 대상 | `reports.target_type`, `targetType` | `POST`, `COMMENT`, `AI_QA_REQUEST`, `AI_ASSET` |
| 신고 상태 | `reports.status`, `status` | `RECEIVED`, `REVIEWING`, `RESOLVED`, `REJECTED` |
| 찬양 출처 | `praise_songs.source_type`, `sourceType` | `CURATED`, `DEVICE` |
| AI 산출물 유형 | `ai_generated_assets.asset_type`, `assetType` | `EXPLANATION`, `SUMMARY`, `GLOSSARY`, `SIMULATOR`, `QA_RESPONSE` |
| AI 산출물 대상 | `ai_generated_assets.target_type`, `targetType` | `BIBLE_VERSE`, `QT_PASSAGE`, `QA_REQUEST` |
| AI 산출물 상태 | `ai_generated_assets.status`, `status` | `VALIDATING`, `APPROVED`, `REJECTED`, `HIDDEN` |
| AI 검증 결과 | `ai_validation_logs.result`, `result` | `PASSED`, `REJECTED`, `NEEDS_REVIEW` |
| AI 검증자 유형 | `ai_validation_logs.reviewer_type`, `reviewerType` | `AUTO`, `ADMIN`, `ADVISOR` |
| 검증 참조 작업 상태 | `validation_reference_jobs.status`, `status` | `ACTIVE`, `EXPIRED`, `DELETED` |
| 평가 셋 유형 | `ai_evaluation_sets.eval_type`, `evalType` | `EXPLANATION`, `SIMULATOR`, `QA` |
| 평가 셋 상태 | `ai_evaluation_sets.status`, `status` | `DRAFT`, `ACTIVE`, `RETIRED` |
| 평가 케이스 대상 | `ai_evaluation_cases.target_type`, `targetType` | `BIBLE_VERSE`, `QT_PASSAGE`, `QA_REQUEST` |
| 평가 케이스 출처 | `ai_evaluation_cases.source_type`, `sourceType` | `VALIDATION_FAILURE`, `USER_REPORT`, `ADMIN_CREATED` |
| 평가 케이스 상태 | `ai_evaluation_cases.status`, `status` | `CANDIDATE`, `APPROVED`, `REJECTED` |

---

## 9. 전체 API 요약

| # | Method | URL | 권한 | 설명 |
|---:|---|---|---|---|
| 1 | GET | `/oauth2/authorization/kakao` | ANONYMOUS | 카카오 로그인 시작 |
| 2 | GET | `/oauth2/callback/kakao` | ANONYMOUS | 카카오 로그인 콜백 |
| 3 | POST | `/api/v1/auth/token/refresh` | Refresh Token | 토큰 재발급 |
| 4 | POST | `/api/v1/auth/logout` | USER | 로그아웃 |
| 5 | GET | `/api/v1/me/session` | 선택 | 세션 조회 |
| 6 | GET | `/api/v1/me` | USER | 내 정보 조회 |
| 7 | PATCH | `/api/v1/me/profile` | USER | 프로필 수정 |
| 8 | POST | `/api/v1/me/tutorial/complete` | USER | 튜토리얼 완료 |
| 9 | POST | `/api/v1/me/withdraw` | USER | 회원 탈퇴 |
| 10 | GET | `/api/v1/bible/books` | USER | 성경 권 목록 |
| 11 | GET | `/api/v1/bible/verses` | USER | 성경 절 조회 |
| 12 | GET | `/api/v1/qt/today` | USER | 오늘 QT 조회 |
| 13 | GET | `/api/v1/qt/{qtPassageId}` | USER | QT 상세 조회 |
| 14 | GET | `/api/v1/qt/{qtPassageId}/study-content` | USER | 요약/해설/단어 조회 |
| 15 | GET | `/api/v1/qt/{qtPassageId}/simulator-clips/{clipId}` | USER | 시뮬레이터 조회 |
| 16 | GET | `/api/v1/notes` | USER | 노트 목록 |
| 17 | GET | `/api/v1/notes/{noteId}` | USER | 노트 상세 |
| 18 | POST | `/api/v1/notes` | USER | 노트 생성 |
| 19 | PATCH | `/api/v1/notes/{noteId}` | USER | 노트 수정 |
| 20 | DELETE | `/api/v1/notes/{noteId}` | USER | 노트 삭제 |
| 21 | POST | `/api/v1/notes/{noteId}/share` | USER | 노트 공유 |
| 22 | GET | `/api/v1/sharing-posts` | USER | 나눔 피드 |
| 23 | GET | `/api/v1/sharing-posts/{postId}` | USER | 나눔 상세 |
| 24 | POST | `/api/v1/sharing-posts/{postId}/like` | USER | 좋아요 |
| 25 | DELETE | `/api/v1/sharing-posts/{postId}/like` | USER | 좋아요 취소 |
| 26 | POST | `/api/v1/sharing-posts/{postId}/comments` | USER | 댓글 작성 |
| 27 | DELETE | `/api/v1/comments/{commentId}` | USER | 댓글 삭제 |
| 28 | POST | `/api/v1/reports` | USER | 신고 접수 |
| 29 | POST | `/api/v1/ai/qa-requests` | USER | AI 질문 |
| 30 | GET | `/api/v1/ai/qa-requests/{requestId}` | USER | AI 질문 결과 |
| 31 | GET | `/api/v1/me/dashboard` | USER | 마이페이지 대시보드 |
| 32 | GET | `/api/v1/notifications` | USER | 알림 목록 |
| 33 | PATCH | `/api/v1/notifications/{notificationId}/read` | USER | 알림 읽음 |
| 34 | GET | `/api/v1/praise-songs` | USER | 찬양 큐레이션 |
| 35 | GET | `/api/v1/me/praise-songs` | USER | 내 찬양 목록 |
| 36 | POST | `/api/v1/me/praise-songs` | USER | 내 찬양 저장 |
| 37 | GET | `/api/v1/admin/dashboard` | ADMIN | 관리자 대시보드 |
| 38 | GET | `/api/v1/admin/qt-passages` | OPERATOR | QT 관리 목록 |
| 39 | POST | `/api/v1/admin/qt-passages` | OPERATOR | QT 등록 |
| 40 | PATCH | `/api/v1/admin/qt-passages/{id}` | OPERATOR | QT 수정 |
| 41 | GET | `/api/v1/admin/ai/assets` | REVIEWER | AI 산출물 목록 |
| 42 | POST | `/api/v1/admin/ai/assets/{assetId}/approve` | REVIEWER | AI 산출물 승인 |
| 43 | POST | `/api/v1/admin/ai/assets/{assetId}/reject` | REVIEWER | AI 산출물 반려 |
| 44 | GET | `/api/v1/admin/reports` | OPERATOR | 신고 목록 |
| 45 | POST | `/api/v1/admin/reports/{reportId}/resolve` | OPERATOR | 신고 처리 |
| 46 | GET | `/api/v1/admin/audit-logs` | ADMIN | 감사 로그 조회 |
| 47 | POST | `/api/v1/system/ai/generation-jobs` | SYSTEM_BATCH | AI 생성 작업 |
| 48 | POST | `/api/v1/system/ai/assets` | SYSTEM_BATCH | AI 산출물 등록 |
| 49 | POST | `/api/v1/system/ai/validation-logs` | SYSTEM_BATCH | AI 검증 로그 등록 |
| 50 | GET | `/api/v1/tutorial` | USER | 튜토리얼 콘텐츠 조회 |
| 51 | GET | `/api/v1/members/nickname/check` | USER | 닉네임 중복 확인 |
| 52 | GET | `/api/v1/notes/draft` | USER | 임시 노트 조회 |
| 53 | GET | `/api/v1/note-categories` | USER | 노트 카테고리 조회 |
| 54 | GET | `/api/v1/sharing-posts/{postId}/comments` | USER | 댓글 목록 |
| 55 | GET | `/api/v1/me/sharing-posts` | USER | 내 나눔 목록 |
| 56 | PATCH | `/api/v1/sharing-posts/{postId}/hide` | USER/OPERATOR | 나눔 공개 중단 |
| 57 | DELETE | `/api/v1/sharing-posts/{postId}` | USER/OPERATOR | 나눔 삭제 |
| 58 | GET | `/api/v1/me/meditation-calendar` | USER | 묵상 달력 |
| 59 | DELETE | `/api/v1/me/praise-songs/{id}` | USER | 내 찬양 삭제 |
| 60 | POST | `/api/v1/admin/ai/assets/{assetId}/hide` | REVIEWER | AI 산출물 숨김 |
| 61 | POST | `/api/v1/admin/ai/assets/{assetId}/regenerate` | REVIEWER | AI 산출물 재생성 요청 |
| 62 | POST | `/api/v1/admin/ai/assets/{assetId}/evaluation-candidates` | REVIEWER | 평가 케이스 후보 등록 |
| 63 | POST | `/api/v1/admin/members/{memberId}/suspend` | OPERATOR | 회원 제재 |
| 64 | POST | `/api/v1/admin/members/{memberId}/activate` | OPERATOR | 회원 제재 해제 |
| 65 | GET | `/api/v1/admin/ai/monitoring` | ADMIN | AI 운영 모니터링 |
| 66 | GET | `/api/v1/admin/ai/validation-checklists` | REVIEWER | 검증 체크리스트 목록 |
| 67 | POST | `/api/v1/admin/ai/validation-checklists` | REVIEWER | 검증 체크리스트 생성 |
| 68 | POST | `/api/v1/admin/ai/validation-checklists/{id}/activate` | REVIEWER | 검증 체크리스트 활성화 |
| 69 | POST | `/api/v1/admin/ai/validation-checklists/{id}/retire` | REVIEWER | 검증 체크리스트 폐기 |
| 70 | GET | `/api/v1/admin/ai/evaluation-sets` | REVIEWER/CONTENT_CREATOR | 평가 셋 목록 |
| 71 | POST | `/api/v1/admin/ai/evaluation-sets` | REVIEWER/CONTENT_CREATOR | 평가 셋 생성 |
| 72 | GET | `/api/v1/admin/ai/evaluation-sets/{setId}/cases` | REVIEWER/CONTENT_CREATOR | 평가 케이스 목록 |
| 73 | POST | `/api/v1/admin/ai/evaluation-sets/{setId}/cases` | REVIEWER/CONTENT_CREATOR | 평가 케이스 생성 |
| 74 | POST | `/api/v1/admin/ai/evaluation-cases/{caseId}/approve` | REVIEWER | 평가 케이스 승인 |
| 75 | POST | `/api/v1/admin/ai/evaluation-cases/{caseId}/reject` | REVIEWER | 평가 케이스 반려 |
| 76 | POST | `/api/v1/system/validation-reference-jobs` | SYSTEM_BATCH | 검증용 참조 작업 생성 |
| 77 | GET | `/api/v1/system/validation-reference-jobs/{jobId}` | SYSTEM_BATCH | 검증용 참조 작업 조회 |
| 78 | POST | `/api/v1/system/validation-reference-jobs/{jobId}/expire` | SYSTEM_BATCH | 검증용 참조 작업 만료 |
| 79 | GET | `/api/v1/admin/praise-songs` | OPERATOR | 관리자 찬양 목록 |
| 80 | POST | `/api/v1/admin/praise-songs` | OPERATOR | 관리자 찬양 등록 |
| 81 | PATCH | `/api/v1/admin/praise-songs/{id}` | OPERATOR | 관리자 찬양 수정 |
| 82 | POST | `/api/v1/admin/praise-songs/{id}/hide` | OPERATOR | 관리자 찬양 숨김 |
| 83 | GET | `/api/v1/admin/notices` | OPERATOR | 관리자 공지 목록 |
| 84 | POST | `/api/v1/admin/notices` | OPERATOR | 공지 생성 |
| 85 | PATCH | `/api/v1/admin/notices/{id}` | OPERATOR | 공지 수정 |
| 86 | POST | `/api/v1/admin/notices/{id}/publish` | OPERATOR | 공지 발행 |
| 87 | POST | `/api/v1/admin/notices/{id}/hide` | OPERATOR | 공지 숨김 |

---

## 10. 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
|---|---|---|---|
| v1.0 | 2026-05-17 | Backend/API Designer | 최초 API 명세 작성 |
| v1.1 | 2026-05-17 | Backend/API Designer | 화면별 누락 API 상세화, 노트 삭제/나눔 스냅샷/AI Q&A 비동기/관리자 AI 운영/평가 셋/체크리스트/마이페이지 달력 보강 |
| v1.2 | 2026-05-17 | Backend/API Designer | ERD/API 필드명 및 enum 정합성 보정, 공통 envelope 예시 기준 명시, 찬양/AI 검증/평가 셋/검증 참조 작업 스키마 수정 |
| v1.3 | 2026-05-17 | Backend/API Designer | 나눔 삭제 정책 ERD 정합성 보정, 관리자 찬양/공지 상세 API 추가, 노트 수정 요청/응답/상태 전이 보강, 연결성 표 잔여 필드 정리 |
| v1.4 | 2026-05-19 | T (강태오) | `07_요구사항_정의서.md` v3.2 §6.4.1(F-03/F-16 `@`멘션 본문 자동 삽입) 반영 — §4.2.2 성경 절 조회에 `verseFrom`/`verseTo` 쿼리 파라미터 추가(범위 조회 지원), 쿼리 파라미터 표·`@`멘션 호출 예시·실패 코드(`400 VALIDATION_ERROR`, `404 NOT_FOUND`, `429 RATE_LIMIT_EXCEEDED`) 추가. §4.3.6 노트 수정에 `@`멘션 본문 자동 삽입 정책 추가 — 클라이언트는 입력을 파싱해 §4.2.2 호출 후 본문에 인용 블록으로 직접 삽입하고 `verseIds`로 `note_verses` 메타데이터 동기화, 서버는 `body`를 자유 형식으로 보존. 트리거 기호는 `@`만 사용(2026-05-19 확정). 코드 변경 없음. |
