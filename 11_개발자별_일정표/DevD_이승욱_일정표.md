# QT-AI -- DevD (이승욱) Journal Service 상세 일정표 v2.0

> 이 문서 목적: Journal Service와 Kafka Outbox 패턴을 처음부터 완성하는 가이드.
> W3 Kafka 통합 주간이 이 프로젝트에서 가장 복잡한 부분이다.

문서 버전: v2.0 | 작성일: 2026-05-08 | 담당자: 이승욱
연관 문서: 02_ERD_문서 v1.2 / 04_API_명세서 v1.2 / 03_아키텍처_정의서 v1.2 섹션6

---

## 0. Journal Service가 하는 일

Journal Service는 묵상 노트를 저장하고 발행하는 서비스다.

```
사용자가 큐티 완료 후 노트 작성 --> DRAFT 상태로 저장
노트 발행 버튼 --> PUBLISHED 상태 변경 --> Kafka 이벤트 발행
AI 세션 실패 시 --> journal.creation.failed 수신 --> 롤백
```

**만들어야 하는 API**
```
POST   /journal/journals             묵상 노트 생성 (DRAFT)
GET    /journal/journals             내 노트 목록
GET    /journal/journals/{id}        노트 상세
PUT    /journal/journals/{id}        노트 수정 (DRAFT 상태만 가능)
DELETE /journal/journals/{id}        노트 삭제 (Soft Delete)
PATCH  /journal/journals/{id}/publish  노트 발행 (DRAFT --> PUBLISHED + Kafka)
```

**이 서비스가 유독 복잡한 이유**
1. 이벤트 소싱: 모든 변경 이력을 DB 에 기록
2. Outbox 패턴: DB 저장과 Kafka 발행의 원자성 보장
3. Saga 보상: 분산 트랜잭션 실패 시 롤백

---

## 1. 환경 세팅 (5/12 아침)

```bash
cd C:\workspace\2nd-Team-Project
git pull origin main
.\gradlew.bat :journal-service:build -x test --no-daemon
# "BUILD SUCCESSFUL" 확인
```

---

## 2. Day1 -- 5/12(화): Flyway SQL 작성

### 이벤트 소싱이란?

일반 CRUD: 최신 상태만 저장. "지금 무엇인지"만 알 수 있다.
이벤트 소싱: 모든 변경 이력 저장. "언제 어떻게 바뀌었는지" 전부 알 수 있다.

```
노트 생성 --> JOURNAL_EVENTS 에 {event_type: "CREATED"} 기록
노트 수정 --> JOURNAL_EVENTS 에 {event_type: "UPDATED"} 기록
노트 발행 --> JOURNAL_EVENTS 에 {event_type: "PUBLISHED"} 기록
```

### Outbox 패턴이란?

Kafka 에 바로 발행하면 이런 문제가 생긴다:
- DB 저장 성공 + Kafka 발행 실패 --> 데이터 불일치
- Kafka 발행 성공 + DB 저장 실패 --> 데이터 불일치

해결책: DB 에 "OUTBOX_EVENTS" 테이블에 먼저 저장 --> 스케줄러가 Kafka 로 발행
이렇게 하면 DB 트랜잭션 안에서 Outbox 도 함께 저장되므로 원자성이 보장된다.

### V1__create_journal_tables.sql

```sql
-- 묵상 노트 테이블
CREATE TABLE IF NOT EXISTS journals (
    journal_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT NOT NULL,
    title      VARCHAR(200) NOT NULL,
    content    TEXT NOT NULL,
    book       VARCHAR(10) NOT NULL,
    chapter    INT NOT NULL,
    verse      INT NOT NULL,
    status     ENUM('DRAFT','PUBLISHED','DELETED') NOT NULL DEFAULT 'DRAFT',
    session_id BIGINT,                   -- 연결된 AI 세션 (선택)
    version    INT NOT NULL DEFAULT 0,   -- 낙관적 락용 버전 필드
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
               ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 이벤트 소싱 테이블 (모든 변경 이력 저장)
CREATE TABLE IF NOT EXISTS journal_events (
    event_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    journal_id  BIGINT NOT NULL,
    user_id     BIGINT NOT NULL,
    event_type  VARCHAR(50) NOT NULL,    -- CREATED, UPDATED, PUBLISHED, DELETED
    payload     JSON,
    sequence_no BIGINT NOT NULL,         -- 순서 보장
    created_at  DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_journal_events (journal_id, sequence_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### V2__create_outbox_table.sql

```sql
-- Outbox 테이블: DB 저장과 Kafka 발행의 원자성 보장
CREATE TABLE IF NOT EXISTS outbox_events (
    outbox_id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    topic           VARCHAR(100) NOT NULL,     -- Kafka 토픽명
    payload         TEXT NOT NULL,             -- Kafka 메시지 본문 (JSON)
    idempotency_key VARCHAR(255) NOT NULL UNIQUE,  -- 중복 발행 방지 키
    status          ENUM('PENDING','SENT','FAILED') NOT NULL DEFAULT 'PENDING',
    created_at      DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    sent_at         DATETIME(6),
    -- PENDING 건만 빠르게 조회하기 위한 인덱스
    INDEX idx_outbox_pending (status, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 3. Day2~3 -- 5/13~5/14: Entity + UseCase

### Journal.kt

```kotlin
// journal-service/.../domain/entity/Journal.kt
package com.qtai.journalservice.domain.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(name = "journals")
class Journal(
    @Column(nullable = false)
    val userId: Long,

    @Column(nullable = false, length = 200)
    var title: String,

    @Column(nullable = false, columnDefinition = "TEXT")
    var content: String,

    @Column(nullable = false, length = 10)
    val book: String,

    @Column(nullable = false)
    val chapter: Int,

    @Column(nullable = false)
    val verse: Int,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    var status: Status = Status.DRAFT,

    @Column
    val sessionId: Long? = null,

    // 낙관적 락: 동시에 같은 노트를 수정하면 충돌 감지
    // "왜 필요한가?" --> 두 탭에서 같은 노트를 동시에 저장하면 데이터가 덮어씌워질 수 있음
    @Version
    var version: Int = 0,

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val journalId: Long = 0,

    @Column(nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    enum class Status { DRAFT, PUBLISHED, DELETED }

    // DRAFT --> PUBLISHED 상태 전이
    fun publish() {
        require(status == Status.DRAFT) { "DRAFT 상태만 발행 가능합니다." }
        status = Status.PUBLISHED
        updatedAt = LocalDateTime.now()
    }

    // Soft Delete
    fun delete() {
        status = Status.DELETED
        updatedAt = LocalDateTime.now()
    }
}
```

### CreateJournalUseCase.kt

```kotlin
// journal-service/.../usecase/CreateJournalUseCase.kt
package com.qtai.journalservice.usecase

import com.qtai.journalservice.domain.entity.Journal
import com.qtai.journalservice.domain.entity.JournalEvent
import com.qtai.journalservice.domain.repository.JournalRepository
import com.qtai.journalservice.domain.repository.JournalEventRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class CreateJournalUseCase(
    private val journalRepository: JournalRepository,
    private val journalEventRepository: JournalEventRepository
) {
    @Transactional
    fun create(
        userId: Long, title: String, content: String,
        book: String, chapter: Int, verse: Int, sessionId: Long?
    ): Journal {
        // 1. 노트 저장
        val journal = journalRepository.save(
            Journal(userId=userId, title=title, content=content,
                    book=book, chapter=chapter, verse=verse, sessionId=sessionId)
        )

        // 2. 이벤트 소싱 기록
        val lastSeq = journalEventRepository.findMaxSequenceByJournalId(journal.journalId) ?: 0
        journalEventRepository.save(
            JournalEvent(journalId=journal.journalId, userId=userId, eventType="CREATED", sequenceNo=lastSeq+1)
        )
        return journal
    }
}
```

---

## 4. Day4~5 -- 5/15~5/16: PublishUseCase + Outbox

### PublishJournalUseCase.kt

```kotlin
// journal-service/.../usecase/PublishJournalUseCase.kt
@Service
class PublishJournalUseCase(
    private val journalRepository: JournalRepository,
    private val outboxRepository: OutboxRepository,
    private val journalEventRepository: JournalEventRepository,
    private val objectMapper: ObjectMapper
) {
    // @Transactional 이 핵심이다
    // journal 상태 변경 + outbox 삽입이 하나의 트랜잭션으로 묶인다
    // 둘 중 하나라도 실패하면 전부 롤백 --> 데이터 일관성 보장
    @Transactional
    fun publish(journalId: Long, userId: Long, idempotencyKey: String): Journal {
        // 1. 노트 조회 + 소유권 확인
        val journal = journalRepository.findById(journalId)
            .orElseThrow { IllegalArgumentException("노트를 찾을 수 없습니다.") }

        if (journal.userId != userId) throw IllegalAccessException("다른 사람의 노트는 발행할 수 없습니다.")

        // 2. DRAFT --> PUBLISHED 상태 전이
        journal.publish()

        // 3. 이벤트 소싱 기록
        val lastSeq = journalEventRepository.findMaxSequenceByJournalId(journalId) ?: 0
        journalEventRepository.save(
            JournalEvent(journalId=journalId, userId=userId, eventType="PUBLISHED", sequenceNo=lastSeq+1)
        )

        // 4. Outbox 에 Kafka 이벤트 저장 (바로 Kafka 로 발행하지 않는다!)
        // "왜 바로 Kafka 에 발행하지 않는가?"
        // --> DB 트랜잭션 안에서 Outbox 를 저장해야 원자성이 보장된다
        val payload = objectMapper.writeValueAsString(mapOf(
            "journalId" to journalId, "userId" to userId,
            "title" to journal.title, "book" to journal.book,
            "chapter" to journal.chapter, "verse" to journal.verse
        ))

        outboxRepository.save(OutboxEvent(
            topic          = "journal.created",
            payload        = payload,
            idempotencyKey = idempotencyKey  // UNIQUE 제약 --> 중복 발행 자동 방지
        ))
        return journal
    }
}
```

---

## 5. Day6~9 -- 5/19~5/22: Kafka Producer + Outbox Scheduler

### OutboxScheduler.kt -- 5초마다 Kafka 로 발행

```kotlin
// journal-service/.../infrastructure/kafka/OutboxScheduler.kt
@Component
@EnableScheduling
class OutboxScheduler(
    private val outboxRepository: OutboxRepository,
    private val kafkaTemplate: KafkaTemplate<String, String>
) {
    // 5초마다 실행
    @Scheduled(fixedDelay = 5000)
    @Transactional
    fun processOutbox() {
        val pendingEvents = outboxRepository.findByStatusOrderByCreatedAt("PENDING")

        pendingEvents.forEach { event ->
            try {
                // Kafka 로 발행 (.get() 은 발행 완료까지 기다림)
                kafkaTemplate.send(event.topic, event.payload).get()

                // 발행 성공 --> SENT 로 업데이트
                event.status = "SENT"
                event.sentAt = java.time.LocalDateTime.now()
                outboxRepository.save(event)
            } catch (e: Exception) {
                // 발행 실패 --> FAILED 로 업데이트
                event.status = "FAILED"
                outboxRepository.save(event)
            }
        }
    }
}
```

### Kafka 발행 확인 방법

```bash
KAFKA_POD=$(kubectl get pods -n qtai -l app.kubernetes.io/name=kafka \
  -o jsonpath='{.items[0].metadata.name}')

kubectl exec -n qtai $KAFKA_POD -- kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic journal.created \
  --from-beginning \
  --max-messages 5
# 발행된 JSON 메시지가 화면에 출력되어야 함
```

---

## 6. W3 -- Saga 보상 컨슈머 (Kafka 통합 주간)

### Saga 패턴이란?

분산 트랜잭션에서 하나가 실패했을 때 이미 완료된 것들을 되돌리는 패턴이다.

```
시나리오:
1. Journal Service: 노트 PUBLISHED 상태로 변경 완료
2. AI Service: 세션 완료 처리 --> 실패!
3. AI Service: "journal.creation.failed" 이벤트 발행
4. Journal Service: 이 이벤트를 받아서 노트를 DRAFT 로 되돌림 (보상)
```

```kotlin
// journal-service/.../infrastructure/kafka/SagaCompensationConsumer.kt
@Component
class SagaCompensationConsumer(
    private val journalRepository: JournalRepository
) {
    @KafkaListener(topics = ["journal.creation.failed"], groupId = "journal-saga")
    @Transactional
    fun consume(message: String) {
        try {
            val event = objectMapper.readValue(message, Map::class.java)
            val journalId = (event["journalId"] as Int).toLong()
            val idempotencyKey = event["idempotencyKey"] as String

            // 멱등성 체크: 같은 이벤트를 두 번 처리하지 않음
            if (processedEventRepository.exists(idempotencyKey)) return

            // 보상 처리: PUBLISHED --> DRAFT 롤백
            val journal = journalRepository.findById(journalId).orElse(null) ?: return
            journal.status = Journal.Status.DRAFT
            journalRepository.save(journal)

            processedEventRepository.save(idempotencyKey)
        } catch (e: Exception) {
            // 파싱 실패 등 -- 로그 기록 후 무시
        }
    }
}
```

### @RetryableTopic + DLQ 설정

**DLQ (Dead Letter Queue) 란?**
처리에 계속 실패하는 메시지를 별도 토픽으로 이동시켜 무한 재시도를 막는다.

```kotlin
@RetryableTopic(
    attempts = "3",                    // 최대 3번 재시도
    backoff = @Backoff(delay = 1000),  // 1초 간격으로 재시도
    dltTopicSuffix = ".DLT"            // 실패 시 journal.creation.failed.DLT 로 이동
)
@KafkaListener(topics = ["journal.creation.failed"], groupId = "journal-saga")
fun consume(message: String) { ... }
```

---

## 7. JournalController.kt

```kotlin
// journal-service/.../api/JournalController.kt
@RestController
@RequestMapping("/journal")
class JournalController(
    private val createJournalUseCase: CreateJournalUseCase,
    private val publishJournalUseCase: PublishJournalUseCase
) {
    @PostMapping("/journals")
    @ResponseStatus(HttpStatus.CREATED)
    fun create(
        @RequestHeader("X-User-Id") userId: Long,   // Gateway 가 주입한 헤더
        @RequestBody req: CreateJournalRequest
    ) = createJournalUseCase.create(
        userId=userId, title=req.title, content=req.content,
        book=req.book, chapter=req.chapter, verse=req.verse, sessionId=req.sessionId
    )

    @PatchMapping("/journals/{id}/publish")
    fun publish(
        @RequestHeader("X-User-Id") userId: Long,
        @PathVariable id: Long,
        @RequestBody req: PublishRequest
    ) = publishJournalUseCase.publish(
        journalId=id, userId=userId,
        idempotencyKey=req.idempotencyKey ?: UUID.randomUUID().toString()
    )
}

data class CreateJournalRequest(
    val title: String, val content: String,
    val book: String, val chapter: Int, val verse: Int,
    val sessionId: Long? = null
)
data class PublishRequest(val idempotencyKey: String? = null)
```

### curl 테스트

```bash
.\gradlew.bat :journal-service:bootRun

# 노트 생성
curl -X POST http://localhost:8084/journal/journals \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d "{\"title\":\"요한복음 3:16 묵상\",\"content\":\"하나님의 사랑을 느꼈다\",\"book\":\"JHN\",\"chapter\":3,\"verse\":16}"
# 기대: {"journalId":1,"status":"DRAFT",...}

# 노트 발행
curl -X PATCH http://localhost:8084/journal/journals/1/publish \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d "{}"
# 기대: {"journalId":1,"status":"PUBLISHED",...}
```

---

## 8. 자주 발생하는 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `OptimisticLockException` | 동시에 같은 노트 수정 | 409 Conflict 반환 후 클라이언트에 재시도 요청 |
| Outbox UNIQUE 오류 | 같은 idempotencyKey 중복 | 이미 처리된 요청 --> 200 OK 반환 (멱등성 처리) |
| Kafka 연결 실패 | bootstrap-servers 설정 오류 | `spring.kafka.bootstrap-servers` 값 확인 |
| @Transactional 롤백 안 됨 | checked exception 사용 | RuntimeException 으로 바꾸거나 rollbackFor 설정 |
| Outbox PENDING 이 계속 쌓임 | Kafka 서버 연결 안 됨 | Kafka pod 상태 확인 |

---

## 9. W2~W4 주간 요약

| 주차 | 이승욱 핵심 작업 |
|------|----------------|
| W2 (5/26~5/29) | Outbox Scheduler 실동작, 멱등성 키 중복 테스트, 낙관적 락 테스트 |
| W3 (6/1~6/5) | Saga 보상 컨슈머, DLQ 설정, Kafka 유실률 0% 검증 (consumer lag 모니터링) |
| W4 (6/8~6/12) | 시연 노트 발행 플로우 dry-run, 커버리지 70%+ |
