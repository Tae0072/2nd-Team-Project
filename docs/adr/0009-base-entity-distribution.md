# ADR-0009: BaseEntity는 v1.0에서 소스 복사로 6 service 배포

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
JPA Entity의 공통 필드(created_at, updated_at, version)는 모든 service가 공유. Maven artifact로 만들어서 의존성으로 가져오면 깔끔하지만 6주 시연에 별도 module + Maven Central publish 부담. 반면 6 service에 같은 코드를 6번 복사하면 변경 시 6 PR 필요.

## Decision
**v1.0: 6 service에 BaseEntity.java 소스 복사**. v1.1: Maven artifact 분리 (03번 § 5):

v1.0:
\\\
auth-service/src/main/java/com/qtai/common/BaseEntity.java
bible-service/src/main/java/com/qtai/common/BaseEntity.java
... (6 service 모두 동일 파일)
\\\

변경 시 6 service 모두 PR (스크립트로 자동 동기화 가능):
\\\ash
# 강태오 W0 작성: scripts/sync-base-entity.sh
for svc in gateway bff-aggregator auth-service bible-service ai-service journal-service; do
  cp common/BaseEntity.java \/src/main/java/com/qtai/common/BaseEntity.java
done
\\\

v1.1: Gradle multi-module의 \common\ 서브모듈로 분리, 6 service가 \implementation(project(":common"))\ 의존

## Alternatives
- **v1.0부터 Maven artifact 분리**: 시연 6주 일정에 무리. 게다가 외부 publish 필요 → ghcr.io maven plugin 학습 곡선
- **각자 알아서 BaseEntity 작성**: 6 service가 미묘하게 달라짐. 마이그레이션 시 사고
- **JPA \@MappedSuperclass\ 안 씀**: 모든 entity에 공통 필드 반복 작성

## Consequences
**긍정:**
- v1.0 단순함 (외부 의존성 X)
- v1.1 마이그레이션 단순 (\implementation(project(":common"))\ 추가만)

**부정:**
- 동기화 스크립트 잊으면 service 별 BaseEntity 미묘하게 다름 (07번 § 11 ArchUnit 룰로 보강)
- code duplication

## 검증 방법
W1 ArchUnit 룰: 6 service의 \BaseEntity\ MD5 해시가 같음 (스크립트 또는 ArchUnit 룰)