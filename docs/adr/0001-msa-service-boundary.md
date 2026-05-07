# ADR-0001: MSA 서비스 경계 6개 + Database per Service

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
강상민, 김태혁, 이지윤, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
1차 프로젝트(HMS)는 단일 Spring Boot 모놀리스로 시작했지만 도메인이 커지면서 한 사람의 변경이 다른 도메인을 무너뜨리는 사고가 반복됨. 2차 프로젝트(QT-AI)는 6명이 6주 동안 동시에 6개 도메인을 작업해야 하므로 service 경계가 코드 분리·DB 분리 양쪽에 강제되어야 함.

## Decision
6개 service로 분리 (03번 § 5):

| Service | Owner | 책임 |
| --- | --- | --- |
| Gateway | 강태오 | JWT 검증·라우팅·Rate Limit·X-User-Id strip |
| BFF Aggregator | 강태오 | 4 service 병렬 호출·STOMP WS·대시보드 |
| Auth Service | 강상민 | 회원·OAuth·JWT·Refresh Rotation |
| Bible Service | 김태혁 | 성경 본문·BOOKS·KR_BIBLE |
| AI Service | 이지윤 | 큐티 4단계·RAG·Anthropic |
| Journal Service | 이승욱 | 묵상 노트·이벤트 소싱·Saga 컨슈머 |

각 service는 자체 DB schema 소유 (Database per Service — ADR-0003). FK 제약 없음 (ADR-0005). 외부 식별은 BIGINT user_id로만.

## Alternatives
- **모놀리스 유지**: 1차 실패 패턴 그대로 — 6명이 같은 코드베이스에서 충돌
- **3 service**: 도메인 결합 (예: Auth+Bible 묶기)이 결국 다시 모놀리스화
- **8+ service**: BFF·Notification 분리. 6명 인력으로 운영 어려움 + 시연 6주에 너무 큰 운영 부담

## Consequences
**긍정:**
- 6명이 service-owner 1대1 매칭 (Lead 강태오는 Gateway+BFF+DevOps)
- service 단위 독립 배포 가능 (06번 § 6 + Helm subchart)
- 코드·DB·배포 모두 격리 → 한 도메인 사고가 다른 도메인 사고로 번지지 않음

**부정:**
- 분산 트랜잭션 관리 부담 (Saga — ADR-0007)
- 운영 복잡도 ↑ (06번 + 07번 보강)
- 6 service 동시 배포 시 시간 ↑ (Helm umbrella 도입)

## 검증 방법
W1 5/22까지 6 service 모두 hello-world 배포 + /actuator/health 200 OK + NetworkPolicy 통신 매트릭스 6×6 검증 (05번 § 6.1.3)