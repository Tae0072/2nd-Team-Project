# ADR-0016: v2 MSA Migration Plan — 학습 목표 기반 트리거 + AI 도메인 우선 분리

## 상태
Accepted (2026-05-14)

## 날짜
2026-05-14

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (강사 면담 후 최종 확정 — W2 첫째 주)

## Context
ADR-0001(Modular Monolith v1)과 ADR-0013(RAG 폐기)은 "v2 분리 시 도입"이라는 모호한 트리거를 사용한다. 트리거를 정하지 않으면 영원히 v1으로 끝나거나, 반대로 시연 직전 무리한 분리 작업으로 사고가 날 수 있다. 본 ADR에서 **언제·무엇을·어떤 순서로** 분리할지 박제한다.

회의록 §4 "일단 모놀리식으로 만든 후, 나중에 쪼갤 수 있는 구조"와 §4-2 "초기에 코드를 다 터지게 만드는 것. 서로 코드를 의존하지 않게 만들어야 나중에 쪼갈 때 안 망함"이 본 ADR의 출발점이다.

## Decision

**v2 분리는 학습 목표 기반 트리거로 W4~W5에 진행한다.**

### 트리거

v2 분리 작업을 시작하는 조건은 다음 두 가지를 모두 만족할 때다:

1. **v1 Modular Monolith가 W3(6/5 금)까지 시연 가능 수준으로 안정화** — 오늘 QT 조회, AI 1회성 Q&A, 묵상 기록 자동 저장, 익명 나눔 흐름이 모두 작동.
2. **강사가 MSA·Kafka·K8s 학습을 발표 평가에 포함시킬 의사를 확인** — W2 첫째 주(5/26~5/29) 강태오·강사 면담 결과로 결정.

두 조건이 모두 충족되면 W4(6/8 월) 시작 시 v2 분리 작업을 개시한다. 한쪽이라도 미달이면 v1 시연으로 마감하고 **발표 자료에 "v2 분리 계획"을 후속 작업 절로 포함**한다.

### 첫 분리 대상: AI 도메인

다음 이유로 `com.qtai.ai` 도메인을 v2의 첫 분리 대상으로 한다:

- 외부 LLM(DeepSeek) 호출이라 다른 도메인과의 결합도가 가장 낮다.
- in-process publisher(`ApplicationEventPublisher`)만 Kafka publisher로 교체하면 분리 완료. 1주 작업 분량.
- AI 도메인 분리만으로도 SSE 스트리밍 + Kafka 이벤트 발행 + 별도 컨테이너 배포 + K8s 학습 효과를 모두 시연 가능.
- Journal 도메인은 in-process 핸들러가 많아 분리 비용이 큼 → v2.1로 미룸.

### v2 분리 시 변경 사항

| 항목 | v1 (현재) | v2 (분리 후) |
| --- | --- | --- |
| 배포 단위 | `qtai-server` 단일 컨테이너 | `qtai-server` + `qtai-ai-service` 2 컨테이너 |
| Gradle 모듈 | 단일 모듈 | `qtai-server` + `qtai-ai-service` 멀티 모듈 |
| AI 호출 | `com.qtai.ai.api.AiSessionFacade` Interface 호출 | HTTP `RestClient` (`http://qtai-ai-service:8085`) |
| `ai.session.completed` 이벤트 | Spring `ApplicationEventPublisher` | Kafka KRaft single-node |
| Schema Registry | 없음 | Apicurio Registry 2.5+ |
| 컨테이너 오케스트레이션 | Docker Compose | Kubernetes Minikube + Helm |
| DB | 단일 `qtai_db` | `qtai_db` + `ai_db` 2 schema (또는 단일 DB 유지하되 권한 격리) |
| 시크릿 관리 | Docker `.env` | K8s Secret |
| 관측성 | 단일 프로세스 메트릭 | 멀티 프로세스 + 분산 트레이싱 강화 |

### 분리 작업 일정 (W4 시작 가정)

| 주차 | 작업 |
| --- | --- |
| W4 월~수 (6/8~10) | Gradle 멀티 모듈 분리, `qtai-ai-service` 빈 모듈 생성, build 통과 |
| W4 목~금 (6/11~12) | Kafka KRaft single-node Docker Compose 추가, Schema Registry 추가, `ai.session.completed` envelope을 Kafka publisher로 교체 |
| W5 월~화 (6/15~16) | K8s Minikube + Helm umbrella chart, 2 서비스 K8s 배포, 통합 테스트 |
| W5 수 (6/17) | 시연 — v1 Modular Monolith로 메인 시연 + v2 분리 데모 슬라이드 |

### 분리하지 않는 것 (v2.1 이후)

- Journal 도메인 (in-process 핸들러 다수, 분리 비용 큼)
- Bible 도메인 (BFF가 가장 자주 호출, 분리 시 응답 지연 우려)
- Gateway Auth 도메인 (BFF와 합쳐서 보안 경계 단순화 유지)
- Simulator 도메인 (구현 자체가 W4 시점에 안정화돼 있을지 불확실)

### 발표 자료 필수 슬라이드

v2 분리 결과와 무관하게 발표 자료에는 다음 슬라이드를 포함한다:

1. **v1 Modular Monolith 다이어그램** — 단일 `qtai-server` + 6 도메인 패키지
2. **도메인 경계 강제 방법** — Spring Modulith + ArchUnit (ADR-0015)
3. **v2 분리 후 다이어그램 (시연 또는 계획)** — `qtai-server` + `qtai-ai-service` + Kafka + K8s
4. **분리 과정의 트레이드오프** — in-process 이벤트 vs Kafka, 단일 DB vs schema 분리, Docker Compose vs K8s
5. **1차(HMS) 실패 vs v1 + v2 가드레일** — 도메인 경계가 코드 레벨에서 강제됨

## Alternatives

- **시점 기반 트리거 (시연 후 W6~W7)**: 학기 끝나면 할 사람 없음. 거부.
- **마일스톤 기반 (베타 테스트 후)**: 학생 프로젝트에서 베타 자체를 안 할 가능성. 거부.
- **부하 기반 (QPS 임계치)**: 학생 트래픽에서 영원히 트리거 안 됨. 거부.
- **v1만으로 끝내기**: 강사가 MSA 학습을 평가에 포함시키면 학습 가치 손실. v2 분리 가능성 열어두는 본 ADR 채택.
- **모든 도메인 한꺼번에 분리**: W4~W5 일정에 무리. AI 도메인만 분리해도 학습 가치 충분.

## Consequences

**긍정:**
- v2 분리 트리거가 명확해져 W3 끝까지 v1 안정화에 집중 가능.
- AI 도메인 우선 선택으로 분리 작업 범위가 1주로 제한됨.
- 분리 실패 시에도 발표 자료의 "v2 분리 계획" 절로 학습 의도를 보여줄 수 있음.
- v1에서 envelope·idempotencyKey 패턴을 동일하게 유지(ADR-0007)했으므로 publisher 교체만으로 v2 이전 가능.

**부정:**
- W4~W5에 v2 작업을 하면서 v1 버그 수정·기능 마무리를 동시에 해야 함 → 사고 위험 증가. 강태오의 횡단 조율 부담.
- AI 도메인만 분리하면 "MSA"라기보다 "분리된 AI 서비스 + 모놀리식 본체" 형태. 발표 시 정확한 명명 필요.
- 강사 면담(W2 첫째 주)에서 MSA 학습을 평가에 안 넣겠다고 하면 v2 분리 자체가 사라짐 → 그 경우 본 ADR을 Superseded로 변경.

## 검증 방법

1. **W2 첫째 주(5/26~5/29):** 강태오·강사 면담 완료 → 본 ADR의 트리거 조건 2번 결과(Yes/No)를 본 ADR 본문 하단에 박제.
2. **W3 끝(6/5 금):** v1 안정화 검증(트리거 조건 1번). 트리거 조건 1·2 모두 Yes면 W4 분리 작업 시작 공지.
3. **W4 끝(6/12 금):** `qtai-ai-service`가 Kafka로 `ai.session.completed` 발행, `qtai-server`의 Journal 도메인 컨슈머가 수신해 오늘 Journal에 요약 첨부.
4. **W5 시연 직전(6/16):** K8s Minikube에 2 서비스 + Kafka + Schema Registry 배포 완료. 또는 발표 자료 후속 계획 절 작성 완료.

## 후속 결정 (강사 면담 후 갱신)

| 항목 | 상태 | 결정 시점 |
| --- | --- | --- |
| 강사의 MSA 학습 평가 포함 의사 | 미정 | W2 첫째 주 (5/26~5/29) |
| v1 W3 안정화 달성 여부 | 미정 | W3 끝 (6/5) |
| Journal 도메인 분리 (v2.1) | 미정 | 시연 6/17 이후 별도 ADR |
| K8s 외 Container Orchestration (Nomad, Swarm) 검토 | 거부 | 학습 가치 K8s 우선 |
