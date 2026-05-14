# ADR-0015: PR 검증 도구 = Spring Modulith 메인 + ArchUnit 보조

## 상태
Accepted (2026-05-14)

## 날짜
2026-05-14

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
ADR-0001 Modular Monolith의 핵심 방어선은 "다른 도메인 패키지의 클래스(Entity, Service, Repository)를 직접 import 금지"다. 1차(HMS) 실패의 원인이 단일 프로세스 안에서 도메인 경계가 깨졌기 때문이었음을 인정하면서, v2 분리 시 무리 없이 쪼개질 수 있도록 v1부터 import 경계를 코드 레벨에서 자동 강제해야 한다. 회의록 §4-4 "위반 시 PR 자동 거절"의 구체적 도구를 본 ADR에서 확정한다.

후보 4개(ArchUnit / Konsist / Gradle custom task / Spring Modulith)를 비교한 결과, Modular Monolith + Spring Boot 3.3 + `ApplicationEventPublisher` 기반 in-process 이벤트(ADR-0004·0007)를 모두 자연스럽게 추적하는 Spring Modulith가 가장 정합적이라고 판단했다.

## Decision

**v1 도메인 경계 검증은 Spring Modulith 메인 + ArchUnit 보조로 한다.**

### 도구 역할 분담

| 도구 | 역할 | 적용 범위 |
| --- | --- | --- |
| **Spring Modulith 1.2+** | 메인 — 모듈 경계 자동 검증, PlantUML 다이어그램 자동 생성, in-process 이벤트 추적 | 패키지 단위 의존성, 이벤트 publish/subscribe 추적 |
| **ArchUnit 1.3+** | 보조 — Modulith가 잡지 못하는 미세 룰 | DTO 매퍼 예외, `@SQLRestriction` 강제, Controller 비즈니스 로직 금지 등 |

### 의존성 (build.gradle.kts)

```kotlin
dependencies {
    // Spring Modulith
    implementation("org.springframework.modulith:spring-modulith-starter-core:1.2.4")
    testImplementation("org.springframework.modulith:spring-modulith-starter-test:1.2.4")

    // ArchUnit
    testImplementation("com.tngtech.archunit:archunit-junit5:1.3.0")
}
```

### 도메인 패키지 메타데이터 (`@ApplicationModule`)

각 도메인 패키지의 `package-info.java`에 `@ApplicationModule`을 선언한다.

```java
// com/qtai/bible/package-info.java
@ApplicationModule(
    displayName = "Bible Domain",
    allowedDependencies = {}  // 다른 도메인 import 금지
)
package com.qtai.bible;

import org.springframework.modulith.ApplicationModule;
```

```java
// com/qtai/bff/package-info.java
@ApplicationModule(
    displayName = "BFF Aggregator",
    allowedDependencies = { "bible::api", "ai::api", "gatewayauth::api" }
)
package com.qtai.bff;
```

### 공개 API = `@NamedInterface`

도메인 간 호출이 허용되는 Facade는 도메인 패키지의 `api/` 하위 패키지에 두고 `@NamedInterface("api")`를 붙인다.

```java
// com/qtai/bible/api/package-info.java
@NamedInterface("api")
package com.qtai.bible.api;

import org.springframework.modulith.NamedInterface;
```

```java
// com/qtai/bible/api/BibleFacade.java
public interface BibleFacade {
    BibleVerseResponse findVerse(String bookCode, int chapter, int verse);
    List<ExplanationResponse> findExplanations(String bookCode, int chapter, int verse);
}
```

다른 도메인은 `com.qtai.bible.api.*`만 import 허용. `com.qtai.bible.internal.*` 또는 `com.qtai.bible.repository.*` 직접 import는 자동 거절.

### 검증 테스트

```java
// qtai-server/src/test/java/com/qtai/QtaiModulesTest.java
class QtaiModulesTest {
    ApplicationModules modules = ApplicationModules.of(QtaiServerApplication.class);

    @Test
    void verifyModuleBoundaries() {
        modules.verify();  // 모든 @ApplicationModule 의존성 + @NamedInterface 검증
    }

    @Test
    void writeDocumentationSnippets() {
        new Documenter(modules)
            .writeModulesAsPlantUml()           // docs/modules/components.puml
            .writeIndividualModulesAsPlantUml() // 도메인별 다이어그램
            .writeAggregatingDocument();         // 통합 문서
    }
}
```

### ArchUnit 보조 룰

Modulith가 잡지 못하는 미세 정책은 ArchUnit으로.

```java
// qtai-server/src/test/java/com/qtai/architecture/CodingRulesTest.java
class CodingRulesTest {
    JavaClasses classes = new ClassFileImporter().importPackages("com.qtai");

    @Test
    void controllers_should_not_call_repositories() {
        noClasses().that().areAnnotatedWith(RestController.class)
            .should().dependOnClassesThat().areAssignableTo(JpaRepository.class)
            .check(classes);
    }

    @Test
    void entities_should_use_SQLRestriction_not_Where() {
        noClasses().that().areAnnotatedWith(Entity.class)
            .should().beAnnotatedWith("org.hibernate.annotations.Where")
            .check(classes);
    }

    @Test
    void writes_should_be_transactional() {
        methods().that().areAnnotatedWith(PostMapping.class)
            .or().areAnnotatedWith(PutMapping.class)
            .or().areAnnotatedWith(PatchMapping.class)
            .or().areAnnotatedWith(DeleteMapping.class)
            .should().beAnnotatedWith(Transactional.class)
            .check(classes);
    }
}
```

### CI 통합

`./gradlew build` 안에서 위 테스트들이 자동 실행되므로 별도 step 불필요. PR status check가 fail이면 머지 차단.

```yaml
# .github/workflows/ci.yml (기존 backend-build job에 자동 포함)
backend-build:
  steps:
    - run: ./gradlew build jacocoTestCoverageVerification
```

### 예외 허용 정책

| 케이스 | 처리 |
| --- | --- |
| 도메인 간 DTO 변환 매퍼 (`BibleResponseToAiRequestMapper`) | `com.qtai.{src}.api`의 DTO만 import → 허용 |
| Lombok 등 생성 코드 | `@ApplicationModule`의 `excludeFromVerification` 설정으로 제외 |
| 테스트 코드 | `ApplicationModules.verify()`는 production code만 검증 (기본) |
| Spring Boot Application 클래스 | `@SpringBootApplication`은 모든 모듈 스캔하므로 예외 |

### 위반 시 안내 메시지

PR 코멘트로 자동 안내될 메시지 표준:

```
❌ 도메인 경계 위반 — ADR-0001 도메인 패키지 절대 규칙 위반

   com.qtai.bff.controller.PassageController가
   com.qtai.bible.repository.BibleVerseRepository를 직접 import했습니다.

   해결:
   1. com.qtai.bible.api.BibleFacade Interface를 통해 호출하세요.
   2. 새 메서드가 필요하면 com.qtai.bible.api에 추가 후 PR 분리하세요.

   참조: ADR-0001 / AGENTS.md "도메인 경계 절대 규칙"
```

## Alternatives

- **ArchUnit 단독**: 표현력 강하지만 이벤트 추적·다이어그램 자동 생성 부재. Spring Modulith와 함께 쓰면 두 장점 모두 살림.
- **Konsist (Kotlin DSL) 단독**: DSL 가독성 좋으나 라이브러리 신생, Spring Boot 종속 추적 부재.
- **Gradle custom task (정규식 grep)**: false positive 위험, Facade 예외 처리 복잡, 룰 추가 비용. 비추.
- **모든 도구 미적용**: 1차 실패 패턴 재현. ADR-0001 절대 규칙이 무의미해짐.

## Consequences

**긍정:**
- 도메인 경계 위반이 빌드 단계에서 즉시 발견 — PR 머지 차단 자동화.
- Spring Modulith의 PlantUML 자동 생성으로 03_아키텍처 다이어그램 동기화 비용 0.
- v1 in-process 이벤트(`ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)`) 패턴이 Modulith 추적과 자연스럽게 정합.
- v2 분리 시 `@ApplicationModule` 메타데이터를 그대로 살려 별도 서비스로 이관 가능.

**부정:**
- `@NamedInterface`로 공개 API를 명시하는 학습 곡선 (W1 첫 주 페어 작업으로 흡수).
- Spring Modulith가 비교적 최근 라이브러리(1.0이 2023)라 한국 자료 적음. 영문 공식 문서 의존.
- ArchUnit 룰 추가/조정 시 테스트 코드 길어짐 — 룰 N개 도달 시 별도 분류 클래스로 정리.

## 검증 방법

W1 Lock-in 5/22까지:
1. `qtai-server`의 6개 도메인 패키지(`gatewayauth`, `bff`, `bible`, `journal`, `ai`, `simulator`) 모두 `@ApplicationModule` 메타데이터 선언 완료.
2. 각 도메인의 `api/` 하위 패키지에 `@NamedInterface("api")` Facade Interface 1개 이상 존재.
3. `QtaiModulesTest.verifyModuleBoundaries()` 통과 (위반 0건).
4. `Documenter`가 `docs/modules/` 디렉토리에 PlantUML 다이어그램 자동 생성.
5. 의도적 위반 케이스(다른 도메인 Entity import)를 추가하면 `./gradlew build` fail로 PR 머지 차단됨을 강태오가 팀에 시연.

## 후속 결정

- ArchUnit 보조 룰은 W1 초기 5개로 시작, 위반 패턴이 드러날 때마다 추가. ADR로 박제 불필요 — `18_코드_품질_게이트.md` §2.4에 룰 목록 유지.
- Spring Modulith는 1.x 메이저 안정화 단계라 W4까지 마이너 버전 자동 패치 허용, 메이저 업데이트는 별도 PR.
