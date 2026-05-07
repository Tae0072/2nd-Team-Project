# ADR-0007: Kafka 멱등성은 DB UNIQUE 제약으로 강제

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
Kafka는 at-least-once delivery 모델. 같은 메시지가 2번 도착할 수 있음 (consumer 재시작 + offset 미확정 등). 1차 HMS는 application layer 중복 체크였는데 race condition 여지 있었음. MSA 풀스코프에서는 더 신뢰할 수 있는 방법 필요.

## Decision
**INBOX_KEYS 테이블에 idempotency_key UNIQUE 제약** (02번 § 8.3 + events/schema의 envelope.idempotencyKey):

\\\sql
CREATE TABLE INBOX_KEYS (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  idempotency_key VARCHAR(255) NOT NULL,
  topic VARCHAR(100) NOT NULL,
  consumed_at DATETIME(6) NOT NULL,
  UNIQUE KEY uk_idempotency (idempotency_key, topic)
);
\\\

consumer 처리 흐름:
1. 메시지 수신
2. \INSERT INTO INBOX_KEYS\ 시도 (DB UNIQUE 제약 발동)
3. \DUPLICATE KEY ENTRY\ → 이미 처리됨 → skip + ack
4. 정상 INSERT → 비즈니스 로직 처리 → ack

idempotencyKey pattern은 토픽별 (events/schema/*.json):
- ai.session.completed: \i.session.completed:{sessionId}\
- journal.created: \journal.created:{journalId}\
- 등등 (8개 토픽 모두)

## Alternatives
- **application layer 중복 체크 (\SELECT 후 INSERT\)**: race condition 위험
- **Kafka transactional producer + exactly-once**: 6 service 모두 transactional producer 설정 부담. 학습 곡선 + 시연 6주 무리
- **idempotent consumer 안 함 (중복 허용)**: 1차 사고 패턴 — Journal 중복 생성 등

## Consequences
**긍정:**
- DB가 race condition 방어 (UNIQUE 제약은 atomic)
- 명시적 + 디버깅 쉬움
- consumer 코드 간단

**부정:**
- INBOX_KEYS 테이블 크기 증가 (TTL 기반 자동 삭제 + 인덱스로 보강)
- idempotencyKey pattern을 모든 producer가 정확히 발행해야 함 (events/schema가 강제)

## 검증 방법
07번 § 4.4 통합 테스트: 같은 메시지 2번 produce → consumer는 1번만 처리 (DUPLICATE KEY로 두 번째 skip)