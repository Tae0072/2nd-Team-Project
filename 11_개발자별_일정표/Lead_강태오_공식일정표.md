# QT-AI 개인 공식 일정표 - 강태오

> 이 파일 하나만 읽고도 본인 작업을 시작할 수 있도록 최신 결정, 작업 범위, 일정, 검증 명령을 모두 포함한다.
> **기준일: 2026-05-14 / 기준 결정: 2026-05-14 오전 회의 (Modular Monolith + Lead 횡단 역할)**
>
> **2026-05-14 v2.0 변경 요지:**
> - 백엔드는 단일 `qtai-server`. AI 주도는 강상민으로 이관.
> - **본인 새 역할: Lead · DevOps · 전체 조율 (단일 파트에 고정 X).** PR 자동 검증 스크립트, 인프라, 컨벤션, 횡단 지원.
> - 우선 액션: (1) Spring Modulith + ArchUnit 도입 + `@ApplicationModule` 메타데이터 6개 선언 + 시연 (W1 첫 주). (2) DECISIONS·ADR·AGENTS·02_ERD·03_아키텍처 정합 PR 완료 후 W1 첫날 본 일정표 본문 갱신. (3) **W2 첫째 주(5/26~5/29) 강사 면담 — MSA·Kafka·K8s 학습 평가 포함 여부 확인 → ADR-0016 트리거 조건 박제.** (4) 면담 결과에 따라 W4(6/8) 시작 시 AI 도메인 v2 분리 작업 개시 또는 발표 자료 "v2 분리 계획" 슬라이드 작성.
> - **PR 검증 도구 확정 (2026-05-14, ADR-0015): Spring Modulith 메인 + ArchUnit 보조.** 상세 룰은 18_코드_품질_게이트 §1.5. W1 첫 주에 `@ApplicationModule` 메타데이터 6개 도메인 선언 + `QtaiModulesTest.verifyModuleBoundaries()` 통과 + 의도적 위반 케이스 추가로 PR 머지 차단 시연.

## 1. 내 역할

- 담당자: 강태오
- **새 역할 (2026-05-14): Lead · DevOps · 전체 조율 (단일 파트에 묶이지 않음)**
- 개인 작업 폴더: `workspaces/Lead_강태오/`
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

- services/gateway/
- services/bff-aggregator/
- .github/workflows/
- helm/
- AGENTS.md
- DECISIONS.md

## 4. 담당 범위

- Gateway Auth: JWT 발급/검증, Google OAuth 진입점, Refresh Rotation, Rate Limit
- Gateway routing: BFF, Bible, AI, admin, WebSocket/SSE 패스스루
- BFF Aggregator: 오늘 QT 첫 화면, 읽기 전용 본문 화면, 관리자 API, 알림 WebSocket 집계
- CI/CD: **단일 `qtai-server` build/test** (Modular Monolith, ADR-0001) + Spring Modulith verifyModuleBoundaries + ArchUnit (ADR-0015) + gitleaks. Helm lint는 v2 분리 시 활성화(ADR-0016 보류)
- 공통 의사결정 충돌 조정과 PR 리뷰

## 5. API와 이벤트 계약 요약

- Gateway Auth: POST /auth/register, /auth/login, /auth/refresh, /auth/logout, /auth/oauth/google, GET /auth/me
- BFF: GET /api/v1/qt/today, GET /api/v1/passages/{bookCode}/{chapter}/{verse}, GET /api/v1/me/dashboard
- Journal route: POST /api/v1/journals/today와 /api/v1/journals/**는 Bible Service로 라우팅
- Admin/WS: /api/v1/admin/**, WS /ws/notifications
- 라우팅 대상은 gateway, bff-aggregator, bible-service, ai-service 4개뿐이다.

## 6. W1 상세 일정 - Foundation Lock-in

- 5/13: AuthFilter 골격, X-User-Id/X-User-Role spoofing strip, Gateway route **도메인별 라우팅(`/bible` `/ai` `/api/v1`)** + journals/today 기준 정리
- 5/14: K8s Secret 4종(deepseek, mysql, jwt-keys, google-oauth)과 NetworkPolicy 초안
- 5/15: GitHub Actions matrix를 gateway/bff-aggregator/bible-service/ai-service로 고정
- 5/19: BFF 오늘 QT 첫 화면 응답 구조 구현 - QT 본문 우선, 최근 Journal/AI 세션은 병렬 fallback
- 5/20: Loki, Prometheus, Jaeger traceId 관측성 기준 배포
- 5/21: Kafka topic/schema registry bootstrap 스크립트와 smoke test
- 5/22: Foundation Lock-in 5항목 최종 검증표 작성

### W1 PR 머지 조건 (필수)

- [ ] 단위 테스트(Unit Test) 작성 완료 및 `./gradlew :gateway:test :bff-aggregator:test` 로컬 통과
- [ ] 테스트 미작성 항목은 PR 본문에 사유 명시 (단위 테스트 누락 시 REQUEST_CHANGES)

## 7. W2-W5 일정

### W2 - 핵심 도메인 구현
- Gateway Auth API 실제 구현 및 통합 테스트
- BFF 오늘 QT 첫 화면과 읽기 전용 본문 집계 API 완성
- admin/notification WebSocket 인증 연결

### W3 - Kafka/E2E 통합
- Gateway -> BFF -> Bible/AI trace 연결 확인
- Journal today DRAFT -> AI 완료 요약 첨부 -> 알림 E2E 1차
- rate limit, CORS, SSE buffering 장애 처리

#### W3 PR 머지 조건 (필수)

- [ ] 통합 테스트(Integration Test) 작성 완료 및 `./gradlew :gateway:integrationTest :bff-aggregator:integrationTest` 통과
- [ ] 테스트 커버리지 70% 이상 유지

### W4 - 안정화와 시연 환경
- Helm values, rollback, smoke test 안정화
- 보안/품질 게이트와 PR template 정리
- 시연 환경 1일 1회 배포 리허설

### W5 - 발표와 리허설
- 발표용 아키텍처 다이어그램과 운영 대시보드 준비
- 시연 직전 Gateway/BFF/CI 책임 구간 점검
- 장애 시 백업 영상/스크립트 전환 담당

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
.\gradlew.bat -p services\gateway build --no-daemon
.\gradlew.bat -p services\bff-aggregator build --no-daemon
rg -n "auth-service|journal-service|ANTHROPIC|com\.anthropic" services .github AGENTS.md DECISIONS.md
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

- Gateway AuthFilter와 route 설정 PR
- BFF Aggregator usecase/controller 골격 PR
- CI/CD와 Helm 4서비스 기준 PR
- Foundation Lock-in 검증 리포트

## 12. PR 전에 확인

- 내 담당 경로 밖 변경이 섞이지 않았는가
- OpenAPI, event schema, DECISIONS.md와 충돌하지 않는가
- ProblemDetail, Kafka data envelope, DeepSeek, 4서비스 기준을 지켰는가
- 로컬 build/test 결과를 PR 본문에 적었는가
- 막힌 점은 추측으로 넘기지 않고 Lead에게 질문으로 남겼는가
