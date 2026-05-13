# ADR-0011: JOURNAL_EVENTS sequence는 last_event_sequence + SELECT FOR UPDATE

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-13

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
ADR-0004 이벤트 소싱에서 동일 journal_id에 동시 PATCH가 들어오면 sequence 충돌 가능. 단순 \MAX(sequence)+1\은 race condition. UUID 기반 sequence는 정렬 X. 일관된 sequence 생성 + 동시성 안전이 필요.

## Decision
**JOURNALS 테이블에 last_event_sequence 컬럼 + SELECT FOR UPDATE** (02번 § 5.4):

\\\sql
ALTER TABLE JOURNALS ADD COLUMN last_event_sequence BIGINT NOT NULL DEFAULT 0;
\\\

PATCH 트랜잭션 흐름:
1. \SELECT * FROM JOURNALS WHERE id=? FOR UPDATE\ (행 수준 락)
2. \
ew_sequence = last_event_sequence + 1\
3. \INSERT INTO JOURNAL_EVENTS (journal_id, sequence, ...) VALUES (?, new_sequence, ...)\
4. \UPDATE JOURNALS SET last_event_sequence = new_sequence WHERE id = ?\
5. 트랜잭션 커밋 → AFTER_COMMIT \journal.updated\ 발행

JOURNAL_EVENTS의 \(journal_id, sequence)\ UNIQUE 제약이 추가 안전망.

## Alternatives
- **MAX(sequence)+1 (락 없음)**: race condition으로 같은 sequence 발생 → UNIQUE 충돌 → 일부 PATCH 실패
- **DB sequence object (Oracle 스타일)**: MySQL 미지원
- **UUID v7 (시간 정렬 가능)**: BIGINT보다 무거움 + 사용자에게 노출 시 가독성 ↓
- **낙관적 락 (version 컬럼)**: 충돌 빈도가 낮으면 좋지만 Journal은 동시 PATCH 가능 → 비관적 락이 안전

## Consequences
**긍정:**
- 동시성 안전 보장 (07번 § 4.3 10 thread 통합 테스트로 검증)
- sequence 빈틈 없음 (1, 2, 3, ...)
- UNIQUE 제약 추가 안전망

**부정:**
- 비관적 락 → 동일 journal_id에 동시 PATCH 시 직렬화 (성능 ↓ but 사용자 1명이 자기 journal에 동시 PATCH 빈도 낮음)
- W1 통합 테스트 필수 (07번 § 4.3)

## 검증 방법
07번 § 4.3 통합 테스트: 동일 journal_id에 10 thread 동시 PATCH → JOURNAL_EVENTS sequence 1~10 빠짐없이 적재