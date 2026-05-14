# NOTICE — v2.0 Modular Monolith 전환 (2026-05-14)

> **레포 구조 안내:** 본 문서 레포(`2nd-Team-Project`)는 명세·결정·문서의 단일 진실 원천이다. 실제 구현은 `QT-AI-2nd-Team-Project` 레포에서 진행한다.

## v1.0 잔재 디렉토리 (v2.0에서 통합 예정)

다음 디렉토리는 **v1.0 MSA 가정의 잔재**이고, 2026-05-14 v2.0 Modular Monolith 결정(ADR-0001)으로 모두 `qtai-server/` 단일 모듈의 도메인 패키지로 통합된다.

| v1.0 디렉토리 | v2.0 위치 | 비고 |
| --- | --- | --- |
| `gateway-service/` | `qtai-server/src/main/java/com/qtai/gatewayauth/` | Spring Cloud Gateway는 v1에서 사용 안 함 — `com.qtai.gatewayauth` 도메인 패키지로 통합 |
| `bff-service/` | `qtai-server/src/main/java/com/qtai/bff/` | BFF Aggregator는 도메인 패키지로 통합 |
| `bible-service/` | `qtai-server/src/main/java/com/qtai/bible/` | Bible 도메인 패키지 |
| `ai-service/` | `qtai-server/src/main/java/com/qtai/ai/` | AI 도메인 패키지 (DeepSeek + 해설 생성) |
| `auth-service/` | (폐기) | 5/12 결정 — JWT/OAuth는 `gatewayauth` 도메인에서 처리 |
| `journal-service/` | `qtai-server/src/main/java/com/qtai/journal/` | 5/12 결정 — Journal은 Bible 도메인 옆 별도 패키지 |
| `shared-kernel/` | `qtai-server/src/main/java/com/qtai/common/` (또는 유지) | 공통 BaseEntity·DTO 등 — ADR-0009 v1.0 소스 복사 정책 |
| (신규) | `qtai-server/src/main/java/com/qtai/simulator/` | 2026-05-14 신설 — 김태혁 시뮬레이터 도메인 (ADR-0014·22번 FS-12) |

## v2 분리 시 (ADR-0016 트리거 충족)

W4(6/8)부터 다음 순서로 분리:
1. **AI 도메인 우선** — `qtai-server`에서 `com.qtai.ai`를 별도 Gradle 모듈 `qtai-ai-service`로 분리
2. in-process publisher → Kafka publisher 교체 (envelope 구조 동일 유지)
3. Kafka KRaft + Schema Registry Docker Compose 추가
4. v2.1 이후 — Journal/Bible 분리 검토

## 본 레포에서 실제 코드 작업이 일어나면 안 되는 이유

- 본 레포는 **문서·명세·결정 단일 원천**
- 실제 코드는 `QT-AI-2nd-Team-Project` 레포에서 작업 (CLAUDE.md 참조)
- v1.0 잔재 디렉토리 안에 코드가 있어도 그것은 W0 골격 단계 산출물이며, v2.0 구조로 마이그레이션 대상

## v1.0 잔재 인프라 파일

| 파일/디렉토리 | 상태 |
| --- | --- |
| `helm/qtai-umbrella/` · `helm/qtai-infra/` | **v2 분리 시 도입 (보류)** — Chart.yaml에 명시 |
| `events/schema/*.json` | v1 in-process 이벤트도 동일 envelope 구조 사용. **v2 Kafka 전환 시 그대로 활용** |
| `apis/auth/openapi.yaml` · `apis/journal/openapi.yaml` | **폐기** — 각 디렉토리의 `DEPRECATED.md` 참조 |
| `test.md`, `05_요구사항_정의서 - 복사본.txt` | 디버그 파일 — 정리 권고 |

## 참조

- `DECISIONS.md` §0~§10 — 단일 기준표
- `AGENTS.md` — AI 에이전트 협업 가이드
- `docs/adr/0001-msa-service-boundary.md` — Modular Monolith 결정
- `docs/adr/0016-v2-migration-plan.md` — v2 분리 트리거
- `README.md` — 프로젝트 개요
