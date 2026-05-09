# 📋 QT-AI — Lead (강태오) 상세 일정표

문서 버전: v1.0
작성일: 2026-05-08
담당자: 강태오
역할: 책임개발자 (Tech Lead) — Gateway + BFF Aggregator + DevOps 총괄
개발 기간: W0(5/8~5/11) ~ W5(6/17)
연관 문서: 00_개발_일정_총괄표 / 01_프로젝트_계획서 v1.3 / 03_아키텍처_정의서 v1.2 / 06_DevOps_운영_매뉴얼 v1.0

---

## 0. Lead 역할 핵심 선언

> **"내가 막히면 팀 전체가 막힌다."**
> Lead는 기능 개발 속도보다 5명이 병렬로 달릴 수 있는 기반을 만드는 것이 최우선이다.
> 나의 블로커를 팀보다 먼저 Slack에 공유하고, 모든 의사결정에 24시간 이내 응답을 보장한다.

### Lead만 가진 권한 & 책임

| 권한 | 책임 |
|------|------|
| main / develop 브랜치 PR 머지 | 코드 품질·보안·컨벤션 최종 게이트 |
| 아키텍처·기술스택 최종 결정 | ADR 작성 + 팀 설명 의무 |
| K8s 클러스터 접근 | 운영 사고 시 1차 대응 |
| Scope 추가/삭제 결정 | Foundation Lock-in + Out-Scope 백로그 관리 |
| PR 머지 거부권 | 이유 명시 + 24시간 내 재검토 |

---

## 1. 소유권 선언 (Code Ownership)

```
gateway-service/          ← 전담 소유 (타인 수정 시 Lead 사전 협의 필수)
  └── filter/
      ├── AuthFilter.kt        (JWT 검증 → X-User-Id 주입)
      └── NoBufferingFilter.kt (SSE buffering 우회)
  └── config/
      ├── RouteConfig.kt       (6 서비스 라우팅)
      └── RateLimitConfig.kt

bff-service/              ← 전담 소유
  └── usecase/
      ├── DashboardUseCase.kt  (4 서비스 병렬 호출)
      └── NotificationUseCase.kt
  └── websocket/
      └── StompConfig.kt       (WebSocket 세션 레지스트리)

helm/                     ← 전담 소유
  ├── qtai-umbrella/
  └── qtai-infra/

.github/workflows/        ← 전담 소유 (ci.yml, cd.yml)
shared-kernel/            ← 전담 소유
```

**침범 규칙**: 위 경로를 수정하는 PR은 반드시 강태오를 리뷰어 지정. Lead 없이 머지 금지.

---

## 2. 일별 상세 일정

### 🟦 W0 — 문서 폭주 & 환경 골격 (5/8~5/11) — 완료 ✅

| 일자 | 오전 | 오후 | 산출물 |
|------|------|------|--------|
| 5/8 목 | 01~03번 문서 작성 | 04~06번 문서 작성 | 문서 6종 v1.0 |
| 5/9 금 | 07~12번 문서 작성 | 13~18번 문서 작성 | 문서 12종 v1.0 |
| 5/10 토 | 19~21번 문서, ADR 12종 | events/schema JSON 8종 | 전체 문서 완성 |
| 5/11 일 | OpenAPI 5종, ci.yml | Gradle 멀티모듈 골격, gradlew | **W0 산출물 전체 GitHub push** ✅ |

**W0 완료 기준 (전부 ✅)**
- [x] `./gradlew build -x test` → BUILD SUCCESSFUL (6 modules)
- [x] OpenAPI 5종 + .spectral.yaml
- [x] .github/workflows/ci.yml (Gradle + Spectral + gitleaks + Flutter + Python)
- [x] gradle-wrapper.jar git track
- [x] events/schema JSON 8종
- [x] .env.example 전체 환경변수

---

### 🟩 W1 — Foundation Lock-in (5/12~5/22) ← **현재 주차**

**W1 집중 목표**: "5/22 18:00까지 Foundation 5항목 전부 ✅. 기능 0줄이어도 5가지가 끝나면 W1 성공."

| 일자 | 오전 (9~12) | 오후 코어 (13~18) | 저녁 |
|------|------------|-------------------|------|
| 5/12 월 | 킥오프 (10:00, 30분). Gradle 6 module 최종 확인 | K8s namespace `qtai` + Helm infra chart (MySQL·Redis·Kafka·ChromaDB) 기동 | Gateway 라우팅 6개 서비스 초기 설정 |
| 5/13 화 | Stand-up. AuthFilter (JWT 검증 → X-User-Id) 구현 | Kafka 토픽 8종 자동 생성 스크립트 | K8s Secret 4종 (anthropic, mysql, jwt-keys, google-oauth) |
| 5/14 수 | Stand-up. NoBufferingFilter (SSE buffering 우회) | BFF Aggregator `/me/dashboard` 병렬 호출 골격 | shared-kernel BaseEntity, ErrorResponse 최종화 |
| 5/15 목 | Stand-up. K8s 스켈레톤 6 pod `/actuator/health` 200 확인 | STOMP WebSocket 기본 설정 (BFF StompConfig) | 팀원 환경 막힘 지원 |
| 5/16 금 | Stand-up. CI yml Spectral lint 통과 확인 | 전원 bootRun 지원 (막힌 팀원 즉시 페어) | 1차 페이스 점검 준비 |
| 5/19 월 | Stand-up. Loki + Prometheus scrape 설정 | Grafana 기본 대시보드 JSON import | Jaeger agent 연결 확인 |
| 5/20 화 | Stand-up. NetworkPolicy default-deny + 허용 매트릭스 | OpenTelemetry traceId 전파 (traceparent 헤더) | 팀원 W1 체크리스트 점검 |
| 5/21 수 | Stand-up. 팀원 PR 리뷰 + 머지 | BFF dashboard 실데이터 연결 (Auth + Bible) | Foundation 사전 점검 |
| 5/22 목 | Stand-up. Foundation 최종 점검 회의 | **W1 Lock-in 게이트 체크 (18:00)** | W1 회고 작성 |

**W1 Lead 산출물 (완료 기준)**

| 산출물 | 파일 | 완료 기준 |
|--------|------|-----------|
| AuthFilter | `gateway-service/.../AuthFilter.kt` | JWT 검증 → X-User-Id 헤더 주입 동작 |
| NoBufferingFilter | `gateway-service/.../NoBufferingFilter.kt` | SSE curl 테스트 첫 토큰 즉시 수신 |
| K8s 스켈레톤 | `helm/qtai-umbrella/` | 6 pod Running + health 200 |
| Kafka 토픽 8종 | `scripts/kafka-topics.sh` | `kafka-topics.sh --list` 8개 확인 |
| Loki·Prometheus·Jaeger | `helm/qtai-infra/` | 3종 대시보드 접속 가능 |
| BFF dashboard 골격 | `bff-service/.../DashboardUseCase.kt` | `/me/dashboard` 200 반환 (partial 허용) |

**W1 Lock-in 게이트 (5/22 18:00)**
- [ ] 서비스 경계 확정 (ADR-0001 팀 합의)
- [ ] OpenAPI 5종 Spectral lint green + Prism mock 가동
- [ ] Kafka 토픽 8종 생성 확인
- [ ] K8s 6 pod Running + `/actuator/health` 200
- [ ] Loki·Prometheus·Jaeger 기동 확인

---

### 🟨 W2 — 서비스별 핵심 도메인 병렬 (5/26~5/29)

**W2 Lead 집중**: BFF 집계 완성 + 팀원 통합 지원 + NetworkPolicy 완성

| 일자 | 주요 작업 |
|------|-----------|
| 5/26 화 | 페이스 점검 (11:30). Gateway 통합 라우팅 검증 — curl 6 서비스 health |
| 5/27 수 | NetworkPolicy 6×6 매트릭스 완성. BFF `/me/dashboard` 5 서비스 실데이터 |
| 5/28 목 | PATCH `/ai/sessions/{id}/advance` 라우팅 검증. Prometheus Alert 설정 |
| 5/29 금 | W2 페이스 점검 + PR 리뷰 집중 머지 |

---

### 🟧 W3 — Kafka 통합 + E2E 1차 (6/1~6/5)

| 일자 | 주요 작업 |
|------|-----------|
| 6/1 월 | Kafka journal.created → notification.requested E2E 흐름 검증 |
| 6/2 화 | 페이스 점검 (11:30). STOMP WebSocket 패스스루 최종 확인 |
| 6/3 수 | **Feature Freeze 선언** + W3C Trace Context propagation 전 구간 확인 |
| 6/4 목 | K8s HPA AI Service 설정. Tempo + Loki 통합 분산 추적 1회 |
| 6/5 금 | SSE P95 ≤ 2000ms 측정. E2E 시나리오 1차 통과 여부 확인 |

---

### 🟥 W4 — 완성도 + 시연 환경 (6/8~6/12)

| 일자 | 주요 작업 |
|------|-----------|
| 6/8 월 | 시연 빌드 tag `v1.0.0-demo` 후보 생성 |
| 6/9 화 | 페이스 점검 + 시연 dry-run 1회 주도 |
| 6/10 수 | 전 pod Running 30분 지속 확인. Grafana "AI 운영" 대시보드 데이터 확인 |
| 6/11 목 | 부하 테스트 (k6 SSE 동시 10명). 병목 수정 |
| 6/12 금 | tag `v1.0.0-demo` 확정. 백업 영상 녹화 지원 |

---

### ⬛ W5 — 발표 준비 (6/15~6/17)

| 일자 | 주요 작업 |
|------|-----------|
| 6/15 월 | PPT 기술 파트 작성. D-30분 헬스체크 스크립트 최종 검증 |
| 6/16 화 | 리허설 1회차 진행 주도. 백업 영상 최종 녹화 |
| 6/17 수 | **시연 D-Day** — D-30분 헬스체크 실행, 발표 진행 |

---

## 3. AI 에이전트 활용 가이드 (Lead용)

| 단계 | Claude 활용처 | 주의사항 |
|------|--------------|----------|
| W0 | 문서 21종 초안 (완료) | 아키텍처 결정은 직접 판단 |
| W1 | K8s yaml, Helm values 골격 생성 | Pod resource limit 실측 필요 |
| W2 | BFF 병렬 호출 코드, WebFlux 패턴 | Reactor 오퍼레이터 동작 직접 검증 |
| W3 | Kafka consumer 설정, OpenTelemetry 설정 | 실제 토픽명·컨슈머 그룹명 직접 확인 |
| W4 | 시연 시나리오 스크립트, 트러블슈팅 | 운영 민감 정보 입력 금지 |