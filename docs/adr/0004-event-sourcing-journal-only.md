# ADR-0004: 이벤트 소싱은 Journal에만 적용

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
강상민, 김태혁, 이지윤, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
이벤트 소싱은 변경 이력을 모두 보존하는 강력한 패턴이지만 학습 곡선과 운영 부담이 큼. 4 service 모두에 적용하면 6주 시연 일정에 무리. 그러나 묵상 노트(Journal)는 사용자의 영적 변화 이력이 핵심 가치 → 이벤트 소싱이 도메인 자체에 자연스럽게 맞음.

## Decision
**Journal Service만 이벤트 소싱.** 다른 service는 일반 CRUD (02번 § 5):

- JOURNAL_EVENTS 테이블이 source of truth
- JOURNALS 테이블은 read model (projection)
- 모든 변경(생성·수정·삭제)은 JOURNAL_EVENTS 추가 → JOURNALS 갱신 (같은 트랜잭션 안)
- AFTER_COMMIT 후 \journal.updated\ 토픽 발행

eventType: TITLE_CHANGED, CONTENT_CHANGED, STATUS_CHANGED (events/schema/journal.updated-value.json)

## Alternatives
- **모든 service에 이벤트 소싱**: 6주 시연 일정 무리. 학습 곡선
- **Journal도 일반 CRUD**: 변경 이력이 사라짐. 도메인 가치 손실
- **Audit log로만 이력 기록**: 도메인 의미보다 운영 의미만. 사용자 가치 ↓

## Consequences
**긍정:**
- 사용자가 자기 묵상 변화 시간 순으로 볼 수 있음 (v1.1 history endpoint)
- 디버깅 시 정확한 변경 시점 추적
- 02번 § 5.4 sequence + last_event_sequence + SELECT FOR UPDATE로 동시성 보장

**부정:**
- Journal Service 학습 곡선 (이승욱 owner)
- read model 일관성 관리 (트랜잭션 안에서 함께 갱신 강제)
- 단일 PATCH가 EVENT + JOURNAL 양쪽 write → 트랜잭션 누락 위험 (07번 § 4.2 가드레일)

## 검증 방법
W1 통합 테스트: PATCH 중간 예외 발생 시 JOURNAL_EVENTS와 JOURNALS 둘 다 롤백 (07번 § 4.2)