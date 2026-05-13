# ADR-0001: MSA 서비스 경계 4개 + Gateway Auth + Bible Journal 통합

## 상태
Accepted (2026-05-13 정합성 패치)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
1차 프로젝트(HMS)는 단일 Spring Boot 모놀리스로 시작했지만 도메인이 커지면서 변경 충돌과 경계 붕괴가 반복됨. QT-AI는 MSA 경계를 유지하되, 2026-05-12 회의에서 범위가 좁은 Auth Service는 Gateway 내부 Auth 모듈로 흡수하고, Journal Service는 Bible Service의 묵상 도메인으로 통합하기로 결정했다. AI/RAG는 DeepSeek API 기반 Spring Boot 서비스로 고정한다.

## Decision
v1.0 배포 단위는 4개 Spring Boot 서비스로 분리한다.

| Service | Owner | 책임 |
| --- | --- | --- |
| Gateway | 강태오 | JWT 발급·검증, Google OAuth, Refresh Rotation, 라우팅, Rate Limit, CORS |
| BFF Aggregator | 강태오 | 화면별 어그리게이션, Bible/AI 병렬 호출, WebSocket 알림 |
| Bible Service | 이지윤·이승욱 | 성경 본문, 쉬운 설명, 주석, 묵상일지(Journal), 익명 나눔, Kafka Journal 컨슈머/프로듀서 |
| AI/RAG Service | 강태오·김태혁·강상민 | DeepSeek Q&A, ChromaDB RAG, SSE, `ai.session.completed` 발행 |

Auth는 독립 서비스가 아니라 Gateway Auth 모듈이며 `auth_db`를 소유한다. Journal은 독립 서비스가 아니라 Bible Service 내부 도메인이며 `bible_db` 안의 `JOURNALS`, `JOURNAL_EVENTS` 테이블을 사용한다. 각 DB schema는 소유 경계를 유지하고, 서비스 간 FK는 만들지 않는다.

## Alternatives
- **6 service 유지(Auth, Journal 독립)**: 팀 배정과 일정 대비 운영·CI·K8s 부담이 크고, Auth/Journal의 범위가 v1.0에 비해 과분함.
- **모놀리스 유지**: 1차 실패 패턴 반복. API 계약·DB 경계·배포 검증이 흐려짐.
- **3 service 이하로 축소**: Bible/AI/BFF 책임이 섞여 SSE, RAG, Journal 이벤트 소싱 경계가 흐려짐.
- **8+ service로 세분화**: Notification 등 분리가 가능하지만 6주 시연 일정에 과도함.

## Consequences
**긍정:**
- 실제 개발 범위가 4개 배포 단위로 줄어 W1 Foundation 검증이 현실화된다.
- Gateway Auth와 Bible Journal 통합으로 API 계약과 DB 소유권이 명확해진다.
- AI/RAG를 3인 공동 소유로 두어 DeepSeek, RAG, SSE 리스크를 분산한다.

**부정:**
- Gateway가 인증 DB와 라우팅을 함께 책임져 Gateway 변경의 중요도가 커진다.
- Bible Service가 성경 조회와 Journal 이벤트 소싱을 함께 가져 복잡도가 높다.
- 기존 6 service 기준 문서는 반드시 함께 정리해야 한다.

## 검증 방법
W1 Lock-in까지 Gateway, BFF Aggregator, Bible Service, AI/RAG Service 4개가 `/actuator/health`를 제공하고, OpenAPI 4개(`apis/auth`, `apis/bff`, `apis/bible`, `apis/ai`)와 Kafka schema가 최신 `DECISIONS.md`와 일치해야 한다.
