# 📋 QT-AI — Dev D (이승욱) 상세 일정표

문서 버전: v1.0
작성일: 2026-05-08
담당자: 이승욱
역할: Journal Service Owner + Kafka Owner
담당 서비스: Journal Service — 묵상 노트 이벤트 소싱 · Outbox · Saga 보상 트랜잭션
개발 기간: W1(5/12) ~ W5(6/17)
연관 문서: 00_개발_일정_총괄표 / 02_ERD_문서 v1.2 / 04_API_명세서 v1.2 / 03_아키텍처_정의서 v1.2 §6

---

## 0. 역할 핵심 선언

> **"이벤트 소싱과 Saga를 실제로 돌려본 개발자가 된다."**
> Journal Service는 단순 CRUD가 아니라 이벤트 소싱 + Kafka Outbox + Saga 보상 트랜잭션이
> 결합된 가장 복잡한 서비스다. W3 Kafka 통합 주간의 핵심 카운터파트.
> Kafka 토픽 설계·컨슈머 멱등성·DLQ 처리를 팀에서 가장 깊이 이해하는 사람이 된다.

---

## 1. 소유권 선언

```
journal-service/
  └── src/main/kotlin/com/qtai/journalservice/
      ├── domain/
      │   ├── entity/Journal.kt
      │   ├── entity/JournalEvent.kt      (이벤트 소싱 로그)
      │   ├── entity/OutboxEvent.kt       (Kafka Outbox 패턴)
      │   └── repository/
      ├── usecase/
      │   ├── CreateJournalUseCase.kt
      │   ├── PublishJournalUseCase.kt    (Outbox + 멱등성 키)
      │   └── SagaCompensationUseCase.kt  (journal.creation.failed 컨슈머)
      ├── infrastructure/
      │   ├── kafka/
      │   │   ├── JournalEventProducer.kt  (Outbox 발행)
      │   │   └── SagaCompensationConsumer.kt
      │   └── scheduler/OutboxScheduler.kt (Outbox polling)
      └── api/
          └── JournalController.kt
  └── src/main/resources/
      └── db/migration/
          ├── V1__create_journal_tables.sql
          └── V2__create_outbox_table.sql
```

**팀에 제공하는 공개 인터페이스**
- Kafka 토픽 발행: `journal.created`, `journal.updated`, `journal.deleted`
- Saga 보상 컨슈머: `journal.creation.failed` 수신 → 롤백 처리
- BFF에서 알림 발행: `notification.requested` (journal.created 처리 후)

---

## 2. Journal Service 핵심 기술 요구사항

| 요구사항 | 구현 방식 | 완료 목표 | 왜 중요한가 |
|---------|-----------|-----------|-------------|
| 이벤트 소싱 | `JOURNAL_EVENTS` 테이블에 모든 변경 이력 기록 | W1 수 | ADR-0004 |
| Outbox 패턴 | `OUTBOX_EVENTS` 테이블 → 스케줄러 → Kafka 발행 | W2 화 | 트랜잭션 원자성 보장 |
| 멱등성 키 | `PublishJournalRequest.idempotencyKey` → DB UNIQUE | W2 수 | 중복 발행 방지 |
| Saga 보상 컨슈머 | `journal.creation.failed` 수신 → Journal DRAFT 롤백 | W3 월 | 분산 트랜잭션 |
| 낙관적 락 | `@Version` 필드 — 동시 수정 충돌 방지 | W2 화 | 동시 편집 안전 |
| Flyway | V1 (Journal+Events) + V2 (Outbox) | W1 월 | DB 스키마 관리 |

---

## 3. 일별 상세 일정

### 🟩 W1 (5/12~5/22)

| 일자 | 오전 | 오후 코어 | 저녁 |
|------|------|-----------|------|
| 5/12 월 | 킥오프 참석. git pull | Flyway V1 — JOURNALS·JOURNAL_EVENTS 테이블 DDL | Journal Entity + JournalEvent Entity |
| 5/13 화 | Stand-up | Journal Repository (findByUserId + findById + soft delete) | @DataJpaTest — 기본 CRUD 확인 |
| 5/14 수 | Stand-up | `CreateJournalUseCase` — DRAFT 생성 + JournalEvent 기록 | 이벤트 소싱 sequence 로직 (ADR-0011) |
| 5/15 목 | Stand-up | `JournalController` — POST/GET/PUT/DELETE 엔드포인트 | X-User-Id 헤더 → userId 추출 |
| 5/16 금 | Stand-up | 단위 테스트 — CreateJournalUseCase Mockito | `/journal/journals` POST curl 테스트 |
| 5/19 월 | Stand-up | Flyway V2 — OUTBOX_EVENTS 테이블 + OutboxEvent 엔티티 | Kafka consumer group 명명 규칙 확인 |
| 5/20 화 | Stand-up | `PublishJournalUseCase` 골격 (DRAFT→PUBLISHED + Outbox insert) | 멱등성 키 DB UNIQUE 제약 확인 |
| 5/21 수 | Stand-up | Kafka producer 골격 (`JournalEventProducer`) — local Kafka 연결 테스트 | W1 체크리스트 점검 |
| 5/22 목 | Stand-up | **W1 Lock-in 게이트 참석 (18:00)** | W1 회고 |

**W1 완료 기준**
- [ ] `POST /journal/journals` → 201 DRAFT 생성
- [ ] `GET /journal/journals/{id}` → 상세 조회
- [ ] `PUT /journal/journals/{id}` → DRAFT 수정
- [ ] JOURNAL_EVENTS 이벤트 소싱 기록 확인
- [ ] Flyway V1+V2 마이그레이션 성공

---

### 🟨 W2 (5/26~5/29)

| 일자 | 주요 작업 |
|------|-----------|
| 5/26 화 | 페이스 점검. `PATCH /journal/journals/{id}/publish` → Outbox insert + PUBLISHED 상태 전이 |
| 5/27 수 | `OutboxScheduler` — 5초 주기 polling → KafkaTemplate 발행 |
| 5/28 목 | `@Version` 낙관적 락 적용. 멱등성 키 중복 발행 테스트 |
| 5/29 금 | Kafka consumer 로그 확인 (`kafka-console-consumer.sh`). Service 커버리지 60%+ |

---

### 🟧 W3 (6/1~6/5) ← **Kafka 통합 핵심 주간**

| 일자 | 주요 작업 |
|------|-----------|
| 6/1 월 | `SagaCompensationConsumer` — `journal.creation.failed` 수신 → DRAFT 롤백 |
| 6/2 화 | 페이스 점검 (11:30). Kafka 이벤트 유실률 0% 검증 (`consumer lag` 모니터링) |
| 6/3 수 | Feature Freeze. `@RetryableTopic` DLQ 설정. consumer 멱등성 검증 (중복 메시지 처리) |
| 6/4 목 | journal.created → notification.requested E2E 흐름 (강태오 협력) |
| 6/5 금 | 통합 시나리오: 묵상 노트 발행 → AI 완료 알림 수신 전체 흐름 확인 |

---

### 🟥 W4 (6/8~6/12) + ⬛ W5 (6/15~6/17)

| 주차 | 주요 작업 |
|------|-----------|
| W4 | 회귀 테스트. Saga 보상 시나리오 시연 dry-run. 커버리지 70%+ |
| W5 | 시연 시나리오 묵상 노트 발행 흐름 리허설 지원 |

---

## 4. Kafka 설계 핵심 원칙

```kotlin
// ✅ Outbox 패턴 — 트랜잭션 안에서 DB 삽입, 스케줄러가 Kafka 발행
@Transactional
fun publishJournal(journalId: Long, idempotencyKey: String) {
    val journal = journalRepository.findById(journalId) ?: throw JournalNotFoundException()
    journal.publish()  // DRAFT → PUBLISHED
    outboxRepository.save(OutboxEvent(
        topic = "journal.created",
        payload = objectMapper.writeValueAsString(JournalCreatedPayload(journal)),
        idempotencyKey = idempotencyKey  // DB UNIQUE 제약
    ))
    journalEventRepository.save(JournalEvent(journal, "PUBLISHED"))
}

// ✅ Saga 보상 컨슈머 — DLQ + 멱등성 처리
@RetryableTopic(attempts = "3", backoff = @Backoff(delay = 1000))
@KafkaListener(topics = ["journal.creation.failed"], groupId = "journal-saga-compensation")
fun consumeJournalCreationFailed(event: JournalCreationFailedEvent) {
    if (processedEventRepository.exists(event.idempotencyKey)) return  // 멱등성
    // 보상 처리: PUBLISHED → DRAFT 롤백
}
```

---

## 5. AI 에이전트 활용 가이드

| 단계 | Claude 활용처 | 주의사항 |
|------|--------------|----------|
| W1 | Flyway DDL 초안, 이벤트 소싱 Entity 구조 | 03번 ERD §5와 대조 필수 |
| W2 | Outbox 스케줄러 코드, KafkaTemplate 설정 | 토픽명 `events/schema/` JSON과 일치 확인 |
| W3 | @RetryableTopic 설정, DLQ consumer 코드 | Kafka 버전(KRaft single-node) 환경 확인 |