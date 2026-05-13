# ADR-0005: 외부 Context 식별은 BIGINT/코드 값으로 저장하고 FK 제약은 만들지 않는다

## 상태
Accepted (2026-05-13 정합성 패치)

## 날짜
2026-05-13

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
Database per Service에서는 다른 서비스가 소유한 테이블을 직접 JOIN하거나 cross-schema FK로 묶으면 안 된다. 2026-05-12 이후 Auth는 Gateway 내부 `auth_db`, Journal은 Bible Service 내부 `bible_db`, AI는 `ai_db`를 소유한다. 그래도 AI 세션과 Journal은 사용자 ID와 성경 passage를 참조해야 한다.

## Decision
외부 Context 식별자는 FK 없이 값으로만 저장한다.

```sql
-- ai_db.ai_sessions
CREATE TABLE ai_sessions (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id BIGINT NOT NULL,          -- auth_db.users.id 값, FK 없음
  book_code VARCHAR(10) NOT NULL,   -- bible_db.books.code 값, FK 없음
  chapter INT NOT NULL,
  verse INT NOT NULL,
  INDEX idx_ai_sessions_user_started (user_id, started_at DESC)
);
```

소유자 검증은 Gateway에서 인증된 사용자 컨텍스트(`X-User-Id` 내부 헤더 등)와 각 서비스 UseCase의 owner check로 수행한다. 데이터 정합성은 API 호출과 Kafka 이벤트 검증으로 보완한다.

## Alternatives
- **cross-schema FK 유지**: Database per Service 위반. 향후 DB 인스턴스 분리 시 장애물이 된다.
- **UUID만 사용**: 외부 노출에는 좋지만 v1.0 MySQL 인덱스·가독성·팀 숙련도 측면에서 부담이 크다.
- **외부 ID 검증 생략**: IDOR와 데이터 오염 위험이 커진다.

## Consequences
**긍정:**
- DB schema를 서비스별로 독립 배포할 수 있다.
- Bible/AI/Gateway Auth 간 순환 의존이 생기지 않는다.
- Kafka 이벤트 replay와 API 검증으로 느슨한 결합을 유지한다.

**부정:**
- DB가 FK로 정합성을 대신 보장하지 않으므로 애플리케이션 테스트가 중요하다.
- 잘못된 외부 ID가 저장될 수 있어 owner check와 계약 테스트가 필요하다.

## 검증 방법
Flyway DDL에서 서비스 간 FK가 없는지 확인한다. API/UseCase 테스트는 본인 리소스가 아닌 `user_id` 접근 시 403을 반환해야 한다.
