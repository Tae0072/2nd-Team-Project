# ADR-0009: BaseEntity는 v1.0에서 DB 사용 모듈에 소스 복사한다

## 상태
Accepted (2026-05-13 정합성 패치)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
JPA Entity의 공통 필드(`created_at`, `updated_at`, `version`, `deleted_at` 등)는 DB를 쓰는 모듈에서 반복된다. v1.0에서 별도 Maven artifact나 `common` 모듈을 만들면 빌드·배포·의존성 관리 부담이 커진다. 2026-05-12 이후 배포 단위는 4개지만, JPA BaseEntity가 필요한 곳은 Gateway Auth, Bible Service, AI Service 중심이다.

## Decision
v1.0에서는 BaseEntity를 DB 사용 모듈에 소스 복사한다.

```text
gateway/src/main/java/com/qtai/common/BaseEntity.java       # Gateway Auth DB
bible-service/src/main/java/com/qtai/common/BaseEntity.java
ai-service/src/main/java/com/qtai/common/BaseEntity.java
```

BFF Aggregator는 DB를 소유하지 않으므로 기본적으로 BaseEntity를 두지 않는다. 변경이 필요하면 Lead가 동일한 내용으로 대상 모듈에 동시 반영한다. v1.1에서는 `common` Gradle module 분리를 검토한다.

## Alternatives
- **v1.0부터 common module 분리**: 깔끔하지만 6주 시연의 설정·리뷰 부담이 크다.
- **각 모듈이 자유롭게 작성**: Hibernate 6, `@SQLRestriction`, audit 필드가 미묘하게 달라질 위험이 있다.
- **모든 서비스에 무조건 복사**: BFF처럼 DB가 없는 모듈에도 불필요한 JPA 의존성이 생긴다.

## Consequences
**긍정:**
- v1.0 구현 속도를 유지하면서 JPA 공통 필드 기준을 맞출 수 있다.
- DB가 없는 BFF를 가볍게 유지한다.

**부정:**
- BaseEntity 변경 시 여러 파일을 동시 수정해야 한다.
- 소스 복사 방식은 장기 유지보수에 적합하지 않다.

## 검증 방법
DB 사용 모듈의 `BaseEntity.java` 해시 또는 주요 필드가 동일한지 CI 스크립트로 확인한다. BFF에는 JPA Entity가 없어야 한다.
