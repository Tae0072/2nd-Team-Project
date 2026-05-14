# QT-AI 개인 공식 일정표 - 김지민

> 이 파일 하나만 읽고도 본인 작업을 시작할 수 있도록 최신 결정, 작업 범위, 일정, 검증 명령을 모두 포함한다.
> **기준일: 2026-05-14 / 기준 결정: 2026-05-14 오전 회의 (Modular Monolith 전환 + Bible팀 합류)**
>
> **2026-05-14 v2.0 변경 요지 (가장 큰 역할 변동):**
> - 백엔드는 단일 `qtai-server`.
> - **본인 새 역할: Bible팀 3인 합류.** Flutter 단독에서 Bible 도메인 → Flutter → 인증 → 관리자 페이지 일괄 진행으로 전환.
> - Flutter 빌드 책임자는 **이승욱**으로 이관 (시연 6/17). 본인은 Flutter UI 작업을 Bible팀과 분담.
> - 관리자 페이지는 W1에서는 보류, Bible 프로토타입·Flutter 완료 후 3명이 함께 진행.

## 1. 내 역할

- 담당자: 김지민
- **새 역할 (2026-05-14): Bible팀 - Bible 도메인 + Flutter UI + 인증 + 관리자 페이지**
- 개인 작업 폴더: `workspaces/DevE_김지민/`
- 기본 브랜치 흐름: feature/{name}-{task} -> dev PR -> 리뷰 -> squash merge

## 2. 반드시 지킬 최신 결정

- 백엔드는 gateway, bff-aggregator, bible-service, ai-service 4개 서비스만 사용한다.
- 인증은 Gateway Auth 모듈에서 처리한다. 독립 Auth Service를 만들지 않는다.
- 묵상일지 Journal은 Bible Service 내부 도메인이다. 독립 Journal Service를 만들지 않는다.
- LLM은 DeepSeek API(OpenAI 호환) 기준이다. 구 Anthropic SDK나 Claude 고정 코드는 만들지 않는다.
- Java 21, Spring Boot 3.3.x, Gradle Kotlin DSL, MySQL 8.0, Kafka KRaft, Jaeger를 고정한다.
- Kafka envelope는 data 필드만 사용한다. payload 키는 사용하지 않는다.
- 에러 응답은 RFC 7807 ProblemDetail(application/problem+json)로 통일한다.
- 성경 데이터는 KJV, 개역한글, Matthew Henry 주석만 허용 범위로 다룬다. 개역개정, ESV, NIV는 금지다.
- 오늘 QT는 MVP에서 하루 1구절이며 `verseStart == verseEnd`로 전달한다.
- AI 질문과 묵상 기록은 오늘 QT 본문에서만 가능하다. 일반 성경 화면은 읽기 전용이다.
- Journal은 `POST /api/v1/journals/today`로 오늘 DRAFT를 만들거나 조회한다. 자유 본문 `POST /api/v1/journals`는 만들지 않는다.
- Journal 4필드(`felt`, `memorableVerse`, `application`, `prayer`)는 별도 저장 버튼 없이 자동 저장한다. 사용자에게 글자 수 제한을 노출하지 않는다.
- AI 완료 이벤트는 새 Journal 생성이 아니라 오늘 Journal에 AI 요약과 `aiSessionId`를 첨부한다.
- 찬양은 AI 추천곡 저장/제거만 MVP에 포함한다. 직접 YouTube URL 입력, 가사/음원/스트리밍 제공은 제외한다.
- 교회 인증은 MVP 기본 제외다. 인증 버튼 자리는 둘 수 있지만, 인증 여부로 앱 사용을 막지 않는다.

## 3. 내가 주로 만지는 경로

- apps/mobile/
- flutter-app/
- 08_프론트엔드_Flutter_가이드.md
- apis/*/openapi.yaml

## 4. 담당 범위

- Flutter 3.24+, Riverpod, Dio, go_router, flutter_secure_storage
- 앱 시작 후 별도 홈 없이 `/today` 오늘 QT 화면으로 바로 진입
- 소프트 로그인: 성경 본문/오늘 QT 미리보기는 비로그인 허용
- 로그인 후 오늘 QT AI 질문, 묵상 기록, 익명 나눔, 알림 접근
- AI SSE token / **sources**(구 rag_sources) / turn_completed 수신과 화면 상태 관리
- ProblemDetail code를 사용자 메시지로 매핑
- Journal 4필드 자동 저장 UI, 찬양 추천 저장/제거 UI, 교회 인증 optional 버튼 자리

## 5. API와 이벤트 계약 요약

- Auth: /auth/login, /auth/refresh, /auth/logout, /auth/oauth/google, /auth/me
- BFF: /api/v1/qt/today, /api/v1/passages/{bookCode}/{chapter}/{verse}, /api/v1/me/dashboard
- AI SSE: POST /ai/sessions/{id}/turns
- Journal: POST /api/v1/journals/today, /api/v1/journals/{id} PATCH/GET/DELETE, /api/v1/shares...
- WS: /ws/notifications

## 6. W1 상세 일정 - Foundation Lock-in

- 5/13: Flutter project/FVM, Riverpod providers, Dio base client
- 5/14: AuthState, secure storage, refresh retry interceptor
- 5/15: `/today` 첫 화면, 오늘 QT 본문/설명 우선 로딩, 비로그인 미리보기
- 5/19: 오늘 QT AI session/chat 화면과 SSE parser
- 5/20: Journal today DRAFT 확보, 4필드 자동 저장, publish/share 화면 골격
- 5/21: notification WebSocket, ProblemDetail error mapper
- 5/22: Gateway/BFF/Bible/AI 연결 smoke test

### W1 PR 머지 조건 (필수)

- [ ] 단위 테스트(Unit Test/Widget Test) 작성 완료 및 `flutter test` 로컬 통과
- [ ] 테스트 미작성 항목은 PR 본문에 사유 명시 (단위 테스트 누락 시 REQUEST_CHANGES)

## 7. W2-W5 일정

### W2 - 핵심 도메인 구현
- 오늘 QT 본문/설명/AI 질문 UX 완성
- 일반 성경 화면 읽기 전용 처리
- 묵상 자동 저장/발행/공유 플로우 구현
- 찬양 추천 저장/제거 UI 초안
- 로그인/refresh/logout 안정화

### W3 - Kafka/E2E 통합
- E2E 통합과 느린 네트워크/토큰 만료 처리
- SSE 재연결/취소 UX
- 교회 인증 optional 버튼 자리와 알림 화면 연결

#### W3 PR 머지 조건 (필수)

- [ ] 통합 테스트(Integration Test) 작성 완료 및 `flutter test integration_test/` 통과
- [ ] 핵심 화면(오늘 QT/AI/Journal) 테스트 커버리지 70% 이상 유지

### W4 - 안정화와 시연 환경
- 모바일 폴리싱, 접근성, empty/error/loading 상태
- 시연 기기에서 FPS/스크롤 안정성 점검
- 백업 데이터와 demo 계정 고정

### W5 - 발표와 리허설
- 모바일 시연 책임
- 시연 동선 리허설과 백업 영상 준비
- 발표 Q&A: Flutter 상태관리와 SSE 설명

## 8. 매일 작업 순서

- 작업 시작 전 git pull 방식으로 최신 dev 동기화
- 개인 workspaces/.../workflows/{date}-{task}.md에 오늘 작업과 DoD 작성
- 계약 파일 이름과 경로를 먼저 확인하고 코드 생성
- 작업 후 본인 서비스 build/test와 금지 패턴 검색
- 개인 reports/{date}-{task}.md에 결과, 막힌 점, 다음 작업 작성
- PR에는 변경 범위, 검증 명령, 남은 리스크를 짧게 적는다

## 9. 검증 명령

```powershell
cd C:\workspace\QT-AI-2nd-Team-Project-master
fvm flutter analyze
fvm flutter test
rg -n "ProblemDetail|Sse|EventSource|Dio|Riverpod" apps mobile flutter-app
```

## 10. 금지 패턴

- PostgreSQL, ZooKeeper, Tempo 설정 추가 금지
- application.yml이나 코드에 API key, DB password, private key 평문 작성 금지
- 트랜잭션 안에서 KafkaTemplate.send 직접 호출 금지. AFTER_COMMIT 패턴 사용
- 서비스 간 DB 직접 JOIN 또는 Repository 공유 금지
- JOURNAL_EVENTS 수정/삭제 금지. append-only 이벤트 로그로 유지
- AI SSE 경로에 /messages 사용 금지. /ai/sessions/{id}/turns만 사용
- OpenAPI 계약과 다른 DTO, 경로, 에러 포맷 임의 생성 금지

## 11. 산출물

- Flutter app scaffold와 routing
- Dio/Auth/SSE client
- 본문/AI/Journal 핵심 화면
- 시연용 모바일 체크리스트

## 12. PR 전에 확인

- 내 담당 경로 밖 변경이 섞이지 않았는가
- OpenAPI, event schema, DECISIONS.md와 충돌하지 않는가
- ProblemDetail, Kafka data envelope, DeepSeek, 4서비스 기준을 지켰는가
- 로컬 build/test 결과를 PR 본문에 적었는가
- 막힌 점은 추측으로 넘기지 않고 Lead에게 질문으로 남겼는가
