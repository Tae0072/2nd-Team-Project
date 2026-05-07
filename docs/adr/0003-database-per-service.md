# ADR-0003: Database per Service (schema 격리)

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
단일 DB는 운영 부담은 적지만 service 간 schema 변경 충돌이 잦음. 1차 HMS의 가장 큰 사고 중 하나가 \USERS\ 테이블 변경이 다른 도메인 모두를 깨뜨린 것. MSA 풀스코프에서는 schema 격리가 강제되어야 함.

## Decision
4 schema (auth_db, bible_db, ai_db, journal_db) — 단일 MySQL instance에 schema 단위 격리 (02번 § 1.2):

| Schema | Owner Service | 주요 테이블 |
| --- | --- | --- |
| auth_db | Auth | USERS, OAUTH_LINKS, REFRESH_TOKENS |
| bible_db | Bible | BOOKS, KR_BIBLE |
| ai_db | AI | AI_SESSIONS, AI_TURNS, PROMPT_TEMPLATES |
| journal_db | Journal | JOURNALS, JOURNAL_EVENTS, INBOX_KEYS |

각 service의 spring.datasource.url은 자기 schema만 가리킴. service 계정도 schema 단위 GRANT.

## Alternatives
- **단일 schema 공유**: 1차 실패 그대로
- **물리적 다중 instance (DB 4개)**: 6주 시연 인프라 부담. 운영 환경 진입 시 검토 (v1.1)
- **NoSQL 혼합 (예: Journal MongoDB)**: 학습 곡선 + 시연 6주 부담. 통일성 우선

## Consequences
**긍정:**
- service 별 schema 변경 자유 (Flyway migration 격리 — 02번 § 8.5)
- 권한·백업·복구 단위 명확
- 운영 환경 진입 시 instance 분리 단순 (1 instance → 4 instance 마이그레이션)

**부정:**
- service 간 JOIN 불가 → Kafka 이벤트로 데이터 동기화 (Eventually Consistent — ADR-0004·0005)
- BFF가 4 service 호출로 어그리게이션 (CompletableFuture — 04번 § 9.4)

## 검증 방법
W1 5/22까지 4 schema 모두 Flyway V1__init.sql 적용 + service 계정으로만 자기 schema 접근 가능 (다른 schema는 \Access denied\) 검증