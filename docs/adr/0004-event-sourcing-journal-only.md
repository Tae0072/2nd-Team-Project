# ADR-0004: 이벤트 소싱은 Journal 도메인에만 적용 (v1 in-process / v2 Kafka)

## 상태
Accepted (2026-05-13 / 2026-05-14 Modular Monolith 연계 갱신)

## 날짜
2026-05-13 (원본) / 2026-05-14 (v1 in-process 보강)

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
이벤트 소싱은 변경 이력을 모두 보존하는 강력한 패턴이지만 학습 곡선과 운영 부담이 크다. 모든 도메인에 적용하면 6주 시연 일정에 무리다. 묵상 노트(Journal)는 사용자의 묵상 변화 이력이 핵심 가치이므로 이벤트 소싱이 도메인에 자연스럽다. 2026-05-14 ADR-0001 Modular Monolith 전환으로 도메인 간 통신이 Kafka에서 in-process 이벤트로 바뀌었지만, **Journal 도메인 내부의 이벤트 소싱 원칙은 그대로 유지**한다.

## Decision
v1에서는 **`com.qtai.journal` 도메인 패키지에만 이벤트 소싱**을 적용한다.

- `journal_events` 테이블이 append-only 이벤트 로그(source of truth)다.
- `journal_journals` 테이블은 조회용 read model(projection)이다.
- 생성·수정·삭제·발행·공유 상태 변경은 `journal_events` 추가 후 같은 트랜잭션 안에서 `journal_journals`를 갱신한다.
- **v1 (Modular Monolith):** 도메인 간 통신은 Spring `ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)`로 처리. Journal 도메인이 `JournalCreatedEvent` 등 in-process 이벤트를 발행하면 BFF·AI 도메인이 핸들러로 받는다.
- **v2 (분리 시):** 동일 envelope을 Kafka로 발행. publisher만 교체하고 핸들러 로직은 유지.
- `POST /api/v1/journals/today`가 오늘 QT Journal DRAFT를 생성한다. `ai.session.completed` in-process 이벤트는 Journal 도메인 핸들러가 받아 같은 `userId + qtDate` Journal에 `aiSessionId`와 AI 요약을 첨부한다.

## Alternatives
- **모든 도메인 이벤트 소싱**: 일정·학습 부담 과도.
- **Journal도 일반 CRUD**: 변경 이력과 시연 가치 손실.
- **Audit log만 별도**: 도메인 이벤트로 재구성 어려움.

## Consequences
**긍정:**
- 사용자가 묵상 변화를 시간 순서로 추적 가능.
- v1 in-process 이벤트에서도 envelope·idempotencyKey 패턴을 유지해 v2 Kafka 전환 시 publisher만 교체.
- Journal 이벤트 처리가 한 도메인 패키지에 모여 API 계약 단순.

**부정:**
- Bible팀이 Journal 도메인까지 함께 책임져 복잡도 증가.
- 이승욱·이지윤이 이벤트 소싱 규칙을 엄격히 지켜야 함 (append-only, 같은 트랜잭션 내 projection 갱신).

## 검증 방법
- `PATCH /api/v1/journals/{id}` 처리 중 예외 발생 시 `journal_events`와 `journal_journals` 모두 롤백.
- 중복 `idempotencyKey` in-process 이벤트는 `journal_inbox_keys` DB UNIQUE 제약으로 skip (ADR-0007).

## 갱신 이력
- 2026-05-13 v1: "Kafka `@TransactionalEventListener(AFTER_COMMIT)` 발행" (Accepted)
- **2026-05-14 v2: v1 Modular Monolith에서는 in-process 이벤트로 처리, Kafka는 v2 분리 시 publisher 교체.**
