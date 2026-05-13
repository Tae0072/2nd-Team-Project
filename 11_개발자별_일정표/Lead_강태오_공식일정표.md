# QT-AI 개인 공식 일정표 - 강태오

> 이 파일 하나만 읽고도 본인 작업을 시작할 수 있도록 최신 결정, 작업 범위, 일정, 검증 명령을 모두 포함한다.
> 기준일: 2026-05-13 / 기준 결정: 2026-05-12 4서비스 재정렬

## 1. 내 역할

- 담당자: 강태오
- 역할: Lead / Gateway / BFF / DevOps
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
- BFF Aggregator: 오늘의 QT, 본문 화면, 대시보드, 관리자 API, 알림 WebSocket 집계
- CI/CD: 4서비스 matrix, gitleaks, build/test, Helm lint, 구서비스 재생성 차단
- 공통 의사결정 충돌 조정과 PR 리뷰

## 5. API와 이벤트 계약 요약

- Gateway Auth: POST /auth/register, /auth/login, /auth/refresh, /auth/logout, /auth/oauth/google, GET /auth/me
- BFF: GET /api/v1/qt/today, GET /api/v1/passages/{bookCode}/{chapter}/{verse}, GET /api/v1/me/dashboard
- Admin/WS: /api/v1/admin/**, WS /ws/notifications
- 라우팅 대상은 gateway, bff-aggregator, bible-service, ai-service 4개뿐이다.

## 6. W1 상세 일정 - Foundation Lock-in

- 5/13: AuthFilter 골격, X-User-Id/X-User-Role spoofing strip, Gateway route 4서비스 기준 정리
- 5/14: K8s Secret 4종(deepseek, mysql, jwt-keys, google-oauth)과 NetworkPolicy 초안
- 5/15: GitHub Actions matrix를 gateway/bff-aggregator/bible-service/ai-service로 고정
- 5/19: BFF dashboard/usecase 병렬 호출 구조와 timeout/fallback 기준 구현
- 5/20: Loki, Prometheus, Jaeger traceId 관측성 기준 배포
- 5/21: Kafka topic/schema registry bootstrap 스크립트와 smoke test
- 5/22: Foundation Lock-in 5항목 최종 검증표 작성

## 7. W2-W5 일정

### W2 - 핵심 도메인 구현
- Gateway Auth API 실제 구현 및 통합 테스트
- BFF 본문 화면/대시보드 집계 API 완성
- admin/notification WebSocket 인증 연결

### W3 - Kafka/E2E 통합
- Gateway -> BFF -> Bible/AI trace 연결 확인
- Kafka 흐름과 BFF 화면 E2E 1차
- rate limit, CORS, SSE buffering 장애 처리

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
