# ADR-0002: Monorepo + Gradle multi-module

## 상태
Accepted (2026-05-13 정합성 패치)

## 날짜
2026-05-13

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
MSA에서 service당 별도 git repo(polyrepo)를 사용할 수 있지만, 6주 시연에서는 OpenAPI, Kafka schema, ADR, Helm, 공통 Gradle 설정을 한 곳에서 동기화하는 편이 더 안전하다. 2026-05-12 결정으로 배포 단위는 Gateway, BFF, Bible, AI 4개로 확정되었다.

## Decision
문서·계약·서비스 골격은 하나의 monorepo에서 관리하고, 백엔드는 Gradle Kotlin DSL multi-module로 구성한다.

```text
2nd-Team-Project/
├── settings.gradle.kts
├── build.gradle.kts
├── gateway/
├── bff-aggregator/
├── bible-service/
├── ai-service/
├── apis/
│   ├── auth/openapi.yaml      # Gateway Auth 계약
│   ├── bff/openapi.yaml
│   ├── bible/openapi.yaml
│   └── ai/openapi.yaml
├── events/schema/*.json
├── docs/adr/*.md
└── helm/
```

`auth-service`와 `journal-service` 모듈은 v1.0에서 만들지 않는다. Auth 기능은 `gateway`, Journal 도메인은 `bible-service`에 포함한다.

## Alternatives
- **Polyrepo(service당 1 repo)**: cross-cutting 변경(BaseEntity, event schema, API 계약)이 여러 PR로 흩어져 누락 위험이 큼.
- **단일 Gradle module**: service 간 코드 경계가 흐려져 ADR-0001을 무력화함.
- **문서 repo와 개발 repo 완전 분리 유지**: 문서는 필요하지만, 실제 skeleton과 CI 기준은 개발 repo에도 동일하게 반영되어야 한다.

## Consequences
**긍정:**
- OpenAPI, Kafka schema, ADR, CI를 한 번에 검증할 수 있다.
- Gradle BOM과 Java 21/Spring Boot 3.3 기준을 모든 백엔드에 강제할 수 있다.
- Flutter 앱은 Gradle 밖에 두되 같은 repo에서 계약을 참조할 수 있다.

**부정:**
- repo가 커지면 checkout과 CI 시간이 늘 수 있다.
- 공통 설정 변경 시 4개 서비스에 영향이 있으므로 PR 리뷰가 필요하다.

## 검증 방법
`settings.gradle.kts`는 `gateway`, `bff-aggregator`, `bible-service`, `ai-service`만 include한다. CI matrix도 같은 4개 서비스만 대상으로 한다.
