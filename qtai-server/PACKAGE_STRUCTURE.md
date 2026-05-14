# qtai-server 패키지 골격 기준 — QT-AI v2.3

> **문서 버전:** v0.1
> **작성일:** 2026-05-15
> **기준 문서:** `03_아키텍처_정의서.md`, `18_코드_품질_게이트.md`
> **문서 역할:** 단일 `qtai-server` Modular Monolith의 패키지 경계와 공개 영역을 고정한다.

---

## 1. 기준 패키지

```text
src/main/java/com/qtai/
    gatewayauth/
        api/
        application/
        domain/
        infrastructure/
    bff/
        api/
        application/
        domain/
        infrastructure/
    bible/
        api/
        application/
        domain/
        infrastructure/
        journal/
        songs/
    ai/
        api/
        application/
        domain/
        infrastructure/
    simulator/
        api/
        application/
        domain/
        infrastructure/
```

---

## 2. 공개 경계

| 도메인 | 외부 공개 가능 패키지 | 직접 import 금지 |
| --- | --- | --- |
| `gatewayauth` | `com.qtai.gatewayauth.api` | `application`, `domain`, `infrastructure` |
| `bff` | 외부 Controller와 화면 응답 DTO | 다른 도메인 Repository 직접 접근 |
| `bible` | `com.qtai.bible.api` | 내부 Entity, Service, Repository |
| `ai` | `com.qtai.ai.api` | 내부 client, batch, Entity, Repository |
| `simulator` | `com.qtai.simulator.api` | 내부 Entity, Service, Repository |

다른 도메인이 import할 수 있는 타입은 원칙적으로 `api/` 하위 Port와 DTO뿐이다.

---

## 3. 하위 모듈 기준

| 하위 모듈 | 위치 | 기준 |
| --- | --- | --- |
| 묵상 노트 | `com.qtai.bible.journal` | 별도 최상위 도메인 또는 독립 서비스로 분리하지 않음 |
| 찬양 큐레이션 | `com.qtai.bible.songs` | 운영자 큐레이션과 사용자 곡 참조 저장만 담당 |

`JournalCommandPort`, `JournalQueryPort`, `SongCommandPort`, `SongQueryPort`는 필요 시 `com.qtai.bible.api`에 공개한다.

---

## 4. 금지 구조

| 금지 | 이유 |
| --- | --- |
| `auth-service`, `bible-service`, `ai-service` 같은 독립 서비스 | v1은 단일 `qtai-server` 기준 |
| `journal` 최상위 도메인 | 묵상은 `bible` 내부 하위 모듈 |
| `songs` 최상위 도메인 | 찬양은 `bible` 내부 하위 모듈 |
| 다른 도메인의 Entity/Service/Repository 직접 import | 도메인 경계 붕괴 |
| 사용자 요청 Controller에서 LLM client 직접 호출 | AI는 배치 또는 관리자 트리거 전용 |

---

## 5. 현재 상태

| 항목 | 상태 |
| --- | --- |
| 패키지 골격 기준 | 이 문서에서 v0.1로 신규 작성 |
| 실제 Spring Boot 프로젝트 | 아직 생성 전 |
| 다음 권장 작업 | 도메인 경계 테스트 기준 작성 |
