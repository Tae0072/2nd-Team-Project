# ADR-0006: Soft Delete는 USERS, JOURNALS만

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
강상민, 김태혁, 이지윤, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
Soft Delete를 모든 테이블에 적용하면 데이터는 안전하지만 query 복잡도와 인덱스 크기가 늘어남. 1차 HMS는 모든 테이블에 deleted_at을 넣어서 일부 조회가 누락(deleted_at IS NULL 빠짐)되는 사고 발생. 어디에 적용할지 명확한 기준 필요.

## Decision
**USERS와 JOURNALS만 Soft Delete** (02번 § 7.5):

| 테이블 | 삭제 정책 |
| --- | --- |
| USERS | Soft Delete (deleted_at) + email 마스킹 (ADR-0010) |
| JOURNALS | Soft Delete (deleted_at) — 사용자 영적 자산 보존 |
| REFRESH_TOKENS | revoked_at (Soft Delete 아님 — 일정 후 hard delete) |
| AI_SESSIONS, AI_TURNS | Hard Delete 안 함 — status로 구분 |
| OAUTH_LINKS, BOOKS, KR_BIBLE | Hard Delete 안 함 (불변 또는 cascade) |
| INBOX_KEYS | TTL 기반 자동 삭제 |

Soft Delete 컬럼이 있는 entity는 \@SQLRestriction("deleted_at IS NULL")\ 필수 (Hibernate 6).

## Alternatives
- **모든 테이블 Soft Delete**: 1차 사고 패턴
- **모두 Hard Delete**: 사용자 영적 자산(Journal) 영구 손실 위험
- **30일 retention만 + Hard Delete**: v1.1 ADR-0014에서 검토

## Consequences
**긍정:**
- 사용자 묵상 영구 보존 (탈퇴해도 본인이 복구 시 회복 가능 — v1.1)
- query 복잡도 최소화 (2개 테이블만 deleted_at 고려)

**부정:**
- DB 크기 증가 (탈퇴자 데이터 유지)
- v1.1에 30일 retention + 자동 hard delete 도입 필요

## 검증 방법
07번 § 11 ArchUnit + W1 통합 테스트: \UserRepository.findByEmail()\가 \deleted_at IS NOT NULL\인 user 반환 X 검증