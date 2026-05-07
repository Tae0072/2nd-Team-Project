# ADR-0010: 탈퇴자 이메일 마스킹으로 재가입 가능

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
USERS.email은 UNIQUE 제약. 탈퇴 시 row를 그대로 두면 같은 이메일로 재가입 X. row를 hard delete하면 이전 묵상 데이터 유실 (ADR-0006 위배). 사용자 가치(재가입 가능) + 데이터 보존 + UNIQUE 제약을 동시에 만족해야 함.

## Decision
**탈퇴 시 email 컬럼 마스킹** (02번 § 2.2.1):

탈퇴 트리거 시:
\\\sql
UPDATE USERS
SET deleted_at = NOW(),
    email = CONCAT('u_', id, '_deactivated_', UNIX_TIMESTAMP(), '@deleted.local')
WHERE id = ?;
\\\

마스킹된 이메일은:
- 도메인 \@deleted.local\ 가 실재하지 않아 외부 발신 사고 X
- id + epoch로 UNIQUE 제약 자동 충족
- 원본 이메일 추적 X (개인정보 최소화)

새 회원가입은 \SQLRestriction("deleted_at IS NULL")\ 적용된 query로 활성 USERS만 검사 → 같은 이메일로 새 row INSERT 가능

## Alternatives
- **탈퇴 시 row hard delete**: ADR-0006 위배 (Journal 등 보존 필요)
- **탈퇴 시 email 컬럼 NULL**: UNIQUE 제약에 NULL 다중 허용되지만 일관성 X
- **탈퇴자도 같은 이메일로 재가입 못 함**: UX 손실
- **별도 DEACTIVATED_USERS 테이블로 archive**: schema 복잡 + JOIN 필요

## Consequences
**긍정:**
- 같은 이메일로 재가입 가능 (사용자 가치)
- 탈퇴자 데이터 보존 (Journal 등 — ADR-0006)
- UNIQUE 제약 자동 충족

**부정:**
- email 컬럼이 PII가 아닌 형태로 변형됨 (단, 원본 추적 불가)
- Audit log에 원본 이메일 보존 필요 (별도 테이블 + 90일 보관 — 05번 § 9.2)

## 검증 방법
W1 통합 테스트: alice@example.com 탈퇴 → 같은 이메일로 재가입 → 새 USERS row 생성 (탈퇴자 row는 마스킹된 채 유지)