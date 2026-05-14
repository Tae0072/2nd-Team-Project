# ADR-0007: 도메인 이벤트 멱등성은 DB UNIQUE 제약으로 강제 (v1 in-process / v2 Kafka)

## 상태
Accepted (2026-05-13 / 2026-05-14 Modular Monolith 연계 갱신)

## 날짜
2026-05-13 (원본) / 2026-05-14 (v1 in-process 보강)

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
Kafka는 at-least-once delivery 모델이라 같은 메시지가 2번 도착할 수 있다 (consumer 재시작 + offset 미확정 등). 1차 HMS는 application layer 중복 체크였는데 race condition 여지 있었다. ADR-0001 Modular Monolith 전환으로 v1 도메인 간 통신이 in-process 이벤트로 바뀌었지만, **재시도·재처리 시 핸들러가 중복 호출될 가능성은 여전히 있다.** 이벤트 소싱 핸들러 트랜잭션 실패 후 재시도, 또는 v2 Kafka 전환 시 at-least-once 시나리오 모두 동일한 방어 메커니즘이 필요하다.

## Decision
**`*_inbox_keys` 테이블에 `idempotency_key` UNIQUE 제약**으로 멱등성 강제.

```sql
CREATE TABLE journal_inbox_keys (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  idempotency_key VARCHAR(255) NOT NULL,
  topic VARCHAR(100) NOT NULL,
  consumed_at DATETIME(6) NOT NULL,
  UNIQUE KEY uk_idempotency (idempotency_key, topic)
);
```

핸들러 처리 흐름 (v1 in-process / v2 Kafka 공통):
1. 이벤트 수신
2. `INSERT INTO *_inbox_keys` 시도 (DB UNIQUE 제약 발동)
3. `DuplicateKeyException` → 이미 처리됨 → skip
4. 정상 INSERT → 비즈니스 로직 처리 → 트랜잭션 커밋

idempotencyKey pattern은 envelope `eventType`별로 고정 (DECISIONS.md §4.2):
- `ai.session.completed`: `ai.session.completed:{sessionId}`
- `journal.created`: `journal.created:{journalId}`
- 등등

## Alternatives
- **application layer 중복 체크 (`SELECT 후 INSERT`)**: race condition 위험.
- **Kafka transactional producer + exactly-once**: 모든 producer에 transactional producer를 강제하면 설정 부담과 학습 곡선이 커져 6주 시연에 무리. v2에서도 도입 보류.
- **idempotent 핸들러 없음 (중복 허용)**: 1차 사고 패턴 — Journal 중복 생성 등.

## Consequences
**긍정:**
- DB가 race condition 방어 (UNIQUE 제약은 atomic).
- v1 in-process / v2 Kafka 모두 동일 핸들러 코드로 동작.
- 명시적이고 디버깅 쉬움.

**부정:**
- `*_inbox_keys` 테이블 크기 증가 (TTL 기반 자동 삭제 + 인덱스로 보강).
- idempotencyKey pattern을 모든 발행 지점이 정확히 발행해야 함.

## 검증 방법
07번 § 4.4 통합 테스트: 같은 이벤트를 2번 발행 → 핸들러는 1번만 처리 (DUPLICATE KEY로 두 번째 skip).

## 갱신 이력
- 2026-05-13 v1: "Kafka 컨슈머 멱등성" (Accepted)
- **2026-05-14 v2: v1 Modular Monolith에서도 in-process 이벤트 재시도 방어용으로 적용. Kafka 도입 시(v2) 동일 메커니즘.**
