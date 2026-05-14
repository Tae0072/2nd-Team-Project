# ADR-0001: Modular Monolith v1 + 도메인 패키지 경계

## 상태
Accepted (2026-05-14 강사 지도 후 재결정 — 기존 MSA 4-서비스 결정을 본 ADR로 갈아엎음)

## 날짜
2026-05-14

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (2026-05-14 오전 회의)

## Context
2026-05-13까지 본 ADR은 "MSA 4 서비스 분리 + Gateway Auth + Bible Journal 통합"이었다. 2026-05-14 오전 회의에서 강사 지도로 결정이 뒤집혔다. 학생 프로젝트에서 MSA로 쪼개기는 인터페이스 설계·서비스 간 통신 설계의 학습 곡선과 일정 부담이 과도하고, 1차(HMS) 실패의 원인이 모놀리스 자체가 아니라 모놀리스 안에서 도메인 경계가 깨졌기 때문이었다. v1은 **하나의 배포 단위로 만들되, 처음부터 도메인 경계를 코드 레벨에서 강제**해 v2 분리 시 무리 없이 쪼개질 수 있는 구조를 만든다.

## Decision
**v1 배포 단위는 단일 Spring Boot 서비스 `qtai-server` 1개**다.

| 도메인 패키지 | Owner | 책임 |
| --- | --- | --- |
| `com.qtai.gatewayauth` | Bible팀 (이지윤·이승욱·김지민) | JWT 발급·검증, Google OAuth, Refresh Rotation, 라우팅 필터 |
| `com.qtai.bff` | 강태오 + Bible팀 | 화면별 어그리게이션, WebSocket 알림 |
| `com.qtai.bible` | Bible팀 | 성경 본문, 쉬운 설명, 해설, Kafka(v2)/in-process 이벤트(v1) |
| `com.qtai.journal` | Bible팀 | 묵상일지 이벤트 소싱, 익명 나눔 |
| `com.qtai.ai` | 강상민 (주도) | DeepSeek Q&A, 해설 생성, 편집자 에이전트, SSE |
| `com.qtai.simulator` | 김태혁 | 본문 장면 시뮬레이터 |

### 도메인 경계 절대 규칙

1. **다른 도메인의 클래스(Entity, Service, Repository) 직접 import 금지.**
2. **데이터 공유는 DTO로만.** 도메인 A의 `XxxResponse` → 도메인 B의 `XxxRequest`로 변환.
3. **기능 호출은 Interface로.** 호출하는 쪽은 가짜 구현체(Mock)로 작동 가능해야 한다.
4. **DTO 명명은 도메인 prefix 강제.** `BibleVerseResponse`, `AiSessionRequest` 등.
5. **위반 시 PR 자동 거절.** 강태오가 검증 스크립트를 작성하고 팀에 시연 후 머지 게이트에 결합한다.

### DB / 인프라

- 단일 DB `qtai_db`. 도메인별 테이블 prefix(`bible_*`, `ai_*`, `journal_*`, `auth_*`).
- 도메인 간 통신은 **Spring `ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)`**. Kafka는 v2로 보류.
- Container Orchestration은 Docker Compose. K8s/Helm은 v2로 보류.

## Alternatives
- **MSA 4-서비스 유지 (이전 결정)**: 학습 곡선과 일정 부담 과도. 강사 판단으로 폐기.
- **모놀리스 + 도메인 경계 없음 (1차 실패 패턴)**: 재발 우려로 거부.
- **6 서비스 (Auth·Journal 독립 포함)**: 5/12 결정으로 이미 폐기됨.

## Consequences
**긍정:**
- 인터페이스 설계·서비스 간 통신 설계 부담 제거로 W1 Foundation Lock-in이 현실화된다.
- 단일 SpringBootTest 컨텍스트로 통합 테스트가 단순해진다.
- in-process 이벤트로 Kafka·Schema Registry·K8s 운영 부담 제거.
- 도메인 경계를 코드 레벨(import 금지 + PR 검증)에서 강제해 v2 분리 시 충돌 최소화.

**부정:**
- Kafka·K8s·MSA 학습 가치 일부 손실 (v2에서 회복).
- 단일 서비스 안에서 도메인 경계가 깨지면 1차 실패 재현 위험 → PR 검증 스크립트가 핵심 방어선.
- 기존 MSA 기준 문서 다수가 동시 갱신 필요 (02_ERD, 03_아키텍처, 04_API, 06_DevOps, 11_개발환경셋업, 15_체크리스트, 17_데이터시드, 20_W1_Foundation 등).

## 검증 방법
W1 Lock-in 5/22 18:00까지:
1. `qtai-server`가 `/actuator/health` `UP` 반환.
2. 도메인 패키지 6개 모두 `import` 검증 스크립트 통과 (다른 도메인 클래스 import 0건).
3. OpenAPI 4개(`apis/bff`, `apis/bible`, `apis/ai`, `apis/auth`)가 단일 서비스에서 모두 서빙되고 Spectral lint 통과.
4. in-process 이벤트 핸들러로 Journal DRAFT 생성·AI 세션 완료 흐름이 동일 트랜잭션 경계에서 동작.

## 슈퍼시드 이력
- 2026-05-13 v1: "MSA 4 서비스 + Gateway Auth + Bible Journal 통합" (Accepted)
- **2026-05-14 v2: Modular Monolith로 본문 갈아엎음 (현재)**
