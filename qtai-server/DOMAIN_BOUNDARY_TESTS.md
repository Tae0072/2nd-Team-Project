# 도메인 경계 테스트 기준 — QT-AI v2.3

> **문서 버전:** v0.1
> **작성일:** 2026-05-15
> **기준 문서:** `03_아키텍처_정의서.md`, `18_코드_품질_게이트.md`, `23_도메인_용어사전.md`
> **문서 역할:** 구현 저장소에서 Spring Modulith/ArchUnit으로 검증할 도메인 경계 테스트 기준을 고정한다.

---

## 1. 목적

QT-AI v1은 단일 `qtai-server` Modular Monolith다. 운영 단위는 하나지만 도메인 경계는 v2 분리를 염두에 두고 강하게 유지한다.

이 문서는 구현 저장소에서 테스트 코드로 옮길 규칙을 정리한다. 실제 테스트 클래스는 Spring Boot 프로젝트 생성 후 작성한다.

---

## 2. 필수 검증 도구

| 도구 | 목적 | 적용 시점 |
| --- | --- | --- |
| Spring Modulith | 모듈 경계와 허용 의존성 검증 | Spring Boot 골격 생성 후 |
| ArchUnit | 금지 import, Controller/Repository 직접 연결, 금지 의존성 검증 | 첫 백엔드 PR부터 |
| rg Guard | 초기 문자열 기반 보조 검사 | CI workflow에서 즉시 |

---

## 3. Spring Modulith 기준

각 최상위 도메인은 `@ApplicationModule`로 정의한다.

```java
@ApplicationModule(displayName = "Bible Domain")
package com.qtai.bible;

import org.springframework.modulith.ApplicationModule;
```

`bff`는 화면 응답 조립을 위해 각 도메인의 `api` 영역만 의존한다.

```java
@ApplicationModule(
    displayName = "BFF Aggregator",
    allowedDependencies = {
        "gatewayauth::api",
        "bible::api",
        "ai::api",
        "simulator::api"
    }
)
package com.qtai.bff;

import org.springframework.modulith.ApplicationModule;
```

---

## 4. 공개 인터페이스 기준

각 도메인의 `api/` 패키지는 `@NamedInterface("api")`로 공개한다.

```java
@NamedInterface("api")
package com.qtai.bible.api;

import org.springframework.modulith.NamedInterface;
```

| 도메인 | 공개 가능한 예 |
| --- | --- |
| `gatewayauth.api` | 인증 결과 DTO, 인증 검증 Port |
| `bible.api` | `BibleQueryPort`, `ExplanationQueryPort`, `JournalCommandPort`, `JournalQueryPort`, `SongQueryPort` |
| `ai.api` | 관리자 재생성 요청 Port, AI 실행 로그 조회 DTO |
| `simulator.api` | `SimulatorQueryPort`, 시뮬레이터 상태 DTO |

---

## 5. ArchUnit 필수 룰

| 룰 | 차단 기준 |
| --- | --- |
| 도메인 내부 import 금지 | 다른 도메인의 `domain`, `application`, `infrastructure` 참조 |
| Controller → Repository 직접 접근 금지 | `@RestController`가 Repository 타입에 의존 |
| 사용자 요청 경로 LLM client 직접 호출 금지 | Controller가 AI client package에 의존 |
| 금지 기술 의존성 금지 | vector/search stack, Kafka 관련 의존성 |
| DB 쓰기 UseCase 트랜잭션 확인 | create/update/delete/save/remove 계열 메서드의 `@Transactional` 누락 |

---

## 6. 테스트 클래스 배치

```text
qtai-server/src/test/java/com/qtai/
    QtaiModulesTest.java
    architecture/
        DomainBoundaryRulesTest.java
        ControllerRulesTest.java
        ForbiddenDependencyRulesTest.java
```

---

## 7. 완료 기준

| 항목 | 완료 기준 |
| --- | --- |
| Modulith | `ApplicationModules.of(...).verify()` 테스트 통과 |
| ArchUnit | 도메인 내부 import 금지 룰 통과 |
| Controller | Controller가 Repository와 LLM client를 직접 참조하지 않음 |
| CI | `./gradlew test` 또는 `./gradlew build`에서 경계 테스트 실행 |
| PR | 위반 시 PR 머지 차단 |

---

## 8. 현재 상태

| 항목 | 상태 |
| --- | --- |
| 도메인 경계 테스트 기준 | 이 문서에서 v0.1로 신규 작성 |
| 실제 테스트 클래스 | Spring Boot 골격 생성 후 작성 |
| 다음 권장 작업 | 전체 정합성 점검 |
