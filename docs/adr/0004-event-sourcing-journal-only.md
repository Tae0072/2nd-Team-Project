# ADR-0004: 이벤트 소싱은 Bible Service의 Journal 도메인에만 적용

## 상태
Accepted (2026-05-13 정합성 패치)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
이벤트 소싱은 변경 이력을 모두 보존하는 강력한 패턴이지만 학습 곡선과 운영 부담이 크다. 모든 도메인에 적용하면 6주 시연 일정에 무리다. 반면 묵상 노트(Journal)는 사용자의 묵상 변화 이력이 핵심 가치이므로 이벤트 소싱이 도메인에 자연스럽다. 2026-05-12 결정으로 Journal은 독립 서비스가 아니라 Bible Service 내부 도메인으로 통합되었다.

## Decision
v1.0에서는 **Bible Service의 Journal 도메인만 이벤트 소싱**을 적용한다.

- `JOURNAL_EVENTS` 테이블이 append-only 이벤트 로그다.
- `JOURNALS` 테이블은 조회용 read model(projection)이다.
- 생성·수정·삭제·발행·공유 상태 변경은 `JOURNAL_EVENTS` 추가 후 같은 트랜잭션 안에서 `JOURNALS`를 갱신한다.
- Kafka 발행은 트랜잭션 커밋 후 `@TransactionalEventListener(AFTER_COMMIT)`로 처리한다.
- `ai.session.completed`는 Bible Service 컨슈머가 받아 Journal DRAFT를 자동 생성한다.

## Alternatives
- **모든 도메인 이벤트 소싱**: Gateway Auth, Bible 조회, AI 세션까지 모두 적용하면 일정과 학습 부담이 과도함.
- **Journal도 일반 CRUD**: 변경 이력과 시연 가치가 사라짐.
- **Audit log만 별도 저장**: 운영 감사에는 좋지만 도메인 이벤트로 재구성하기 어렵다.

## Consequences
**긍정:**
- 사용자가 묵상 변화를 시간 순서로 추적할 수 있다.
- Kafka 보상·멱등성·순서 보장 학습 포인트가 명확하다.
- Journal 이벤트 처리가 Bible Service 내부에 모여 API 계약이 단순해진다.

**부정:**
- Bible Service가 성경 조회와 Journal 쓰기 모델을 함께 책임져 복잡도가 커진다.
- 이승욱 담당 영역은 Bible Service 안에서도 Kafka·이벤트 소싱 규칙을 엄격히 지켜야 한다.

## 검증 방법
`PATCH /api/v1/journals/{id}` 처리 중 예외가 발생하면 `JOURNAL_EVENTS`와 `JOURNALS`가 모두 롤백되어야 한다. 중복 `idempotencyKey` 메시지는 DB UNIQUE 제약으로 skip되어야 한다.
