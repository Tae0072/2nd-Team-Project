# QT-AI 개인 공식 일정표 - 강상민

> 이 파일 하나만 읽고도 본인 작업을 시작할 수 있도록 최신 결정, 작업 범위, 일정, 검증 명령을 모두 포함한다.
> 기준일: 2026-05-13 / 기준 결정: 2026-05-12 4서비스 재정렬

## 1. 내 역할

- 담당자: 강상민
- 역할: AI/RAG Service - DeepSeek/SSE Main Owner
- 개인 작업 폴더: `workspaces/DevC_강상민/`
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

- services/ai-service/src/main/java/com/qtai/ai/
- services/ai-service/src/main/resources/application.yml
- apis/ai/openapi.yaml

## 4. 담당 범위

- AI session/turn API와 SSE streaming 구현
- DeepSeek API(OpenAI 호환) RestClient/WebClient adapter 구현
- AI_SESSIONS, AI_TURNS, PROMPT_TEMPLATES 저장 모델
- ai.session.completed Kafka 발행은 AFTER_COMMIT 패턴으로 처리
- timeout, semaphore, provider error, client cancel 처리

## 5. API와 이벤트 계약 요약

- POST /ai/sessions
- POST /ai/sessions/{id}/turns - SSE
- POST /ai/sessions/{id}/complete
- GET /ai/sessions/{id}, GET /ai/sessions
- SSE events: turn_started, token, rag_sources, turn_completed, [DONE]
- Config: DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL

## 6. W1 상세 일정 - Foundation Lock-in

- 5/13: DeepSeekStreamService, timeout, semaphore, cancel hook 골격
- 5/14: AiSession/AiTurn Entity, Flyway V1, StartSession/ProcessTurn UseCase
- 5/15: SSE 4종 이벤트와 [DONE] 종료 흐름 구현
- 5/19: CompleteSessionUseCase와 ai.session.completed AFTER_COMMIT 발행
- 5/20: LLM_TIMEOUT, LLM_PROVIDER_ERROR ProblemDetail 매핑
- 5/21: DevB RAG/prompt assembly 연결
- 5/22: 1턴 E2E와 DeepSeek 장애 fallback 검증

## 7. W2-W5 일정

### W2 - 핵심 도메인 구현
- 실제 DeepSeek streaming 연동
- RAG source 포함 답변 생성
- AI session 완료 -> Bible Journal 자동 생성 흐름 연결

### W3 - Kafka/E2E 통합
- Kafka Saga 보상과 E2E 통합
- SSE buffering, gateway timeout, client cancel 장애 처리
- provider 비용/latency metric 발행

### W4 - 안정화와 시연 환경
- 회귀 테스트와 eval 안정화
- 시연용 WireMock fallback
- 운영 로그 마스킹 점검

### W5 - 발표와 리허설
- AI 코칭 시연 책임
- 장애 시 녹화 응답/fallback 전환
- 발표 Q&A: DeepSeek, RAG, SSE 설명

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
.\gradlew.bat -p services\ai-service build --no-daemon
.\gradlew.bat -p services\ai-service test --no-daemon
rg -n "DeepSeek|SseEmitter|ServerSentEvent|ai.session.completed" services\ai-service
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

- DeepSeekStreamService 실제 adapter
- AI Session/Turn API와 SSE Controller
- ai.session.completed publisher
- provider timeout/error 테스트

## 12. PR 전에 확인

- 내 담당 경로 밖 변경이 섞이지 않았는가
- OpenAPI, event schema, DECISIONS.md와 충돌하지 않는가
- ProblemDetail, Kafka data envelope, DeepSeek, 4서비스 기준을 지켰는가
- 로컬 build/test 결과를 PR 본문에 적었는가
- 막힌 점은 추측으로 넘기지 않고 Lead에게 질문으로 남겼는가
