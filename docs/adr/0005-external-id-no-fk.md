# ADR-0005: 외부 service 식별은 BIGINT, FK 제약 없음

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
Database per Service에서 service 간 데이터 참조 (예: AI Service의 AI_SESSIONS.user_id가 Auth Service의 USERS.id를 가리킴)는 어떻게 표현해야 하는가? FK 제약을 걸면 schema 격리 위배 + 다른 service의 schema 변경에 따라 cascade 영향. 그러나 데이터 정합성은 필요.

## Decision
**외부 식별은 BIGINT 컬럼만 + FK 제약 없음** (02번 § 1.3):

\\\sql
-- ai_db.AI_SESSIONS
CREATE TABLE AI_SESSIONS (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,         -- auth_db.USERS.id를 가리키지만 FK 제약 X
  passage_book VARCHAR(3) NOT NULL, -- bible_db.BOOKS.code를 가리키지만 FK X
  ...
  INDEX idx_user (user_id)          -- 인덱스만 추가 (조회 성능)
);
\\\

데이터 정합성은 application layer에서 검증 (\@PreAuthorize\ + service 메서드의 owner 검증).

## Alternatives
- **FK 제약 유지**: schema 격리 위배. cross-schema FK는 MySQL에서 잠재적 deadlock + 인스턴스 분리 시 불가
- **UUID로 식별**: 가독성 ↓, 인덱스 크기 ↑ (BIGINT 8B vs UUID 36B)
- **Eventual Consistency 포기 (외부 정합 무시)**: 1차 사고 패턴 — IDOR 등 보안 위험

## Consequences
**긍정:**
- schema 격리 유지 (ADR-0003)
- 운영 환경에서 instance 분리 시 무중단 마이그레이션
- 인덱스 크기 작음

**부정:**
- application layer에서 owner 검증 강제 (07번 § 3.2 IDOR 단위 테스트)
- 외부 service 사라진 데이터 (예: 탈퇴한 user_id) 참조 가능 → application에서 처리

## 검증 방법
ArchUnit + 07번 § 11 — JPA \@JoinColumn\ 사용 X 검증