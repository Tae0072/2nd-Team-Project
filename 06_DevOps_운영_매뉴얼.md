��� QT-AI (큐티 AI 앱) — DevOps 운영 매뉴얼 v1.0

> **문서 버전:** v1.0
> **작성일:** 2026-05-07
> **연관 문서:** [01_프로젝트_계획서 v1.4](./01_프로젝트_계획서.md) / [02_ERD_문서 v1.3](./02_ERD_문서.md) / [03_아키텍처_정의서 v1.3](./03_아키텍처_정의서.md) / [04_API_명세서 v1.5](./04_API_명세서.md) / [05_보안_명세서 v1.0](./05_보안_명세서.md)
> **DevOps 키워드:** GitHub Actions · Docker buildx · ghcr.io · Helm · Minikube · Flyway · Loki/Prometheus/Jaeger · Rollback · Incident Runbook · 온콜
> **W1 Lock-in 산출물:** 본 문서 + `.github/workflows/ci.yml` + `.github/workflows/cd.yml` + `helm/qtai-umbrella/` + `helm/qtai-infra/` + Grafana 대시보드 JSON
> **목적:** 03번 아키텍처 청사진을 **실행 가능한 운영 절차**로 변환. 6명이 W2~W5 매주 동일한 절차로 배포·롤백·모니터링·사고 대응을 수행할 수 있도록 박제. 1차(HMS)에서 "시연 직전 부랴부랴 배포" 사고를 본질적으로 차단.

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-07 | 강태오 | 초기 작성 — 운영 정책·환경 정의·CI/CD 5단계·이미지·Helm·배포·Rollback·관측성·백업·Incident Runbook·온콜·체크리스트 + 1차 실패 ↔ 가드레일 매핑 |

---

## 목차

1. [운영 정책 개요](#1-운영-정책-개요)
2. [환경 정의 (Environment)](#2-환경-정의-environment)
3. [CI/CD 파이프라인](#3-cicd-파이프라인)
4. [컨테이너 이미지 표준](#4-컨테이너-이미지-표준)
5. [Helm Chart 운영](#5-helm-chart-운영)
6. [배포 절차 (Deploy Runbook)](#6-배포-절차-deploy-runbook)
7. [Rollback 절차](#7-rollback-절차)
8. [관측성 운영 (Loki · Prometheus · Jaeger)](#8-관측성-운영-loki--prometheus--jaeger)
9. [백업·복구 절차](#9-백업복구-절차)
10. [Incident Runbook (시나리오별)](#10-incident-runbook-시나리오별)
11. [온콜·통신 정책](#11-온콜통신-정책)
12. [1차(HMS) 실패 패턴 ↔ DevOps 가드레일](#12-1차hms-실패-패턴--devops-가드레일)
13. [W1 Lock-in DevOps 체크리스트](#13-w1-lock-in-devops-체크리스트)

---

## 1. 운영 정책 개요

### 1.1 운영 원칙

| 원칙 | 적용 |
| --- | --- |
| **Everything as Code** | 인프라·배포·시크릿(참조)은 모두 git. 손으로 K8s 직접 변경 금지 (긴급 hotfix 제외 + 사후 PR) |
| **Repeatable Deployment** | 같은 git SHA → 같은 K8s 상태. Helm + immutable image tag |
| **Automated Rollback** | health check 실패 시 자동 rollback (Helm `--atomic`) |
| **Observability First** | 배포 후 메트릭·로그·trace로 검증. 검증 실패 시 자동 또는 수동 rollback |
| **Immutable Infrastructure** | 컨테이너 이미지에 SSH·exec 금지. 변경은 새 이미지 + redeploy |
| **Fail Fast** | CI에서 lint·test·security 실패 시 머지 차단. 운영에서 발견 X |
| **Least Surprise** | 배포 절차·rollback 절차 6 service 동일. 한 번 익히면 다 됨 |

### 1.2 RACI

| 영역 | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| GitHub Actions 작성·유지 | 강태오 | 강태오 | 전원 | 전원 |
| Helm Chart 작성·유지 | 강태오 | 강태오 | 전원 | 전원 |
| Dockerfile (service별) | service owner | 강태오 | 강태오 | 전원 |
| Flyway migration (service별) | service owner | service owner | 강태오 | 전원 |
| K8s 클러스터 운영 (Minikube) | 강태오 | 강태오 | — | 전원 |
| 배포 트리거 (`develop` 머지) | 각 PR 승인자 | 강태오 | — | 전원 |
| Rollback 결정 | 강태오 | 강태오 | service owner | 전원 |
| 관측성 대시보드 | 강태오 | 강태오 | service owner | 전원 |
| 사고 대응 | 강태오 (총괄) | 강태오 | 영향 service owner | 전원 |
| 온콜 (W4~W5 시연 직전) | 강태오 단독 (v1.0) | 강태오 | — | 전원 |

### 1.3 운영 시간대

| 활동 | 시간 |
| --- | --- |
| 정기 배포 (`develop` → `staging`) | 평일 11:00~17:00 KST (오전 스탠드업 후 ~ 오후 5시 전) |
| Hotfix 배포 | 24/7 (강태오 판단) |
| 사고 대응 | 24/7 (P0/P1 즉시) |
| 시연 (5/27, 6/3, 6/17 회고·시연일) | 시연 시간 ±1h freeze (배포 X) |
| 정기 점검 | 매주 금 17:00~18:00 (회고 + 다음주 배포 계획) |

> **freeze 정책:** 시연 또는 발표 시간 ±1h 동안 일체 배포·DB 변경 금지. 강태오가 Slack `#qtai-deploy`에 freeze 시작/종료 안내.

### 1.4 v1.0 운영 단순화 박제 (의도적 제외)

| 통제 | v1.0 | v1.1+ |
| --- | --- | --- |
| 다중 환경 (dev/staging/prod 분리) | ❌ Minikube 단일 환경 | 클라우드 배포 시 분리 |
| Blue/Green 배포 | ❌ Rolling Update만 | 다운타임 민감 시 |
| Canary 배포 | ❌ | 사용자 트래픽 분할 시 |
| 자동 스케일 (HPA) | ❌ replicas 고정 | 부하 가변 시 |
| 다중 노드 K8s | ❌ Minikube single node | 운영 환경 |
| 다중 가용 영역 (Multi-AZ) | ❌ | 클라우드 |
| Service Mesh (Istio/Linkerd) | ❌ | mTLS 필요 시 |
| GitOps (Argo CD/Flux) | ❌ GHA push 방식 | 운영 정착 후 |
| On-call rotation | ❌ 강태오 단독 | 팀 확장 시 |

> v1.0은 6주 시연 MVP라 단순화. v1.1 도입 시점·근거를 박제 → "왜 빠져 있는지" 설명 가능.

---

## 2. 환경 정의 (Environment)

### 2.1 환경 매트릭스

| 환경 | 위치 | 용도 | 배포 트리거 | 데이터 |
| --- | --- | --- | --- | --- |
| **local** | 개발자 PC (Docker Desktop) | 로컬 개발 + 단위 테스트 | 수동 | 각 개발자 격리 |
| **dev** | Minikube (강태오 PC 또는 공용) | 통합 테스트 + Mock 서버 | `develop` 푸시 시 자동 | 시드 데이터 + 가짜 사용자 |
| **demo** | 동일 Minikube `qtai-demo` namespace | 시연·발표용 | `main` 머지 시 수동 (강태오 승인) | 시연 시드 |

> **v1.0은 dev 환경이 사실상 운영.** 외부 접근 가능한 클라우드 배포는 v1.1.

### 2.2 환경별 설정 분리

```
helm/qtai-umbrella/
├── values.yaml              # 공통 기본값
├── values-dev.yaml          # dev override (low replicas, debug log)
└── values-demo.yaml         # demo override (시연용 시드, log 정상)
```

```bash
# 배포 시 환경별 values 지정
helm upgrade --install qtai ./helm/qtai-umbrella \
  --namespace qtai \
  --values ./helm/qtai-umbrella/values.yaml \
  --values ./helm/qtai-umbrella/values-dev.yaml \
  --atomic --timeout 5m
```

### 2.3 namespace 분리

| namespace | 용도 |
| --- | --- |
| `qtai` | 6 service + 4 인프라 (dev) |
| `qtai-demo` | 시연용 (dev와 격리) |
| `observability` | Loki·Prometheus·Jaeger·Grafana·OTel Collector (dev/demo 공유) |
| `kube-system` | K8s 자체 (DNS 등) |

> NetworkPolicy로 namespace 간 격리 (05번 § 6.1). `observability`는 모든 namespace에서 metrics·log·trace 수신 허용.

---

## 3. CI/CD 파이프라인

### 3.1 GitHub Actions 5단계

```
[Push to develop / PR]
    ↓
┌─────────────────────────────────────────────────────┐
│ 1. lint        — gitleaks + Spotless + Spectral     │  ← 머지 게이트
│ 2. test        — JUnit 5 + Testcontainers           │  ← 머지 게이트
│ 3. build       — Gradle multi-module build          │  ← 머지 게이트
│ 4. image       — Docker buildx → ghcr.io push       │  (push 시만)
│ 5. deploy-dev  — helm upgrade --install (dev ns)    │  (develop 머지 시만)
└─────────────────────────────────────────────────────┘
    ↓
[관측성 검증]
    └─ /actuator/health 통과 + Prometheus alert 0건 = 성공
    └─ 실패 시 Helm --atomic 자동 rollback
```

### 3.2 트리거 규칙

| 이벤트 | 단계 | 환경 |
| --- | --- | --- |
| PR (develop 향) | 1·2·3 | (배포 X) |
| `develop` push | 1·2·3·4·5 | dev |
| `main` push | 1·2·3·4 | (수동 승인 후 demo) |
| Tag `v*` | 1·2·3·4 | (수동 승인 후 demo) |

### 3.3 ci.yml 본격 작성 (W1)

> W0 placeholder는 이미 있음 (`.github/workflows/ci.yml` 빈 골격). W1에 강태오가 본격 작성.

```yaml
# .github/workflows/ci.yml (W1 본격)
name: CI

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop]

jobs:

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0    # gitleaks가 history 검사

      - name: Gitleaks (시크릿 탐지)
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Spotless (Java 코드 스타일)
        uses: gradle/gradle-build-action@v3
        with:
          arguments: spotlessCheck

      - name: Spectral (OpenAPI lint)
        run: |
          npm install -g @stoplight/spectral-cli@^6
          for spec in apis/*/openapi.yaml; do
            npx spectral lint "$spec"
          done

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: 21
      - uses: gradle/gradle-build-action@v3
      - name: 단위 + 통합 테스트
        run: ./gradlew test integrationTest
        # Testcontainers (cp-kafka 7.6+, mysql:8.0) 자동 부팅

      - name: OWASP Dependency-Check
        run: ./gradlew dependencyCheckAggregate
        # CVE 7.0+ 발견 시 fail

      - name: Test Report Upload
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-reports
          path: '**/build/reports/'

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 21 }
      - uses: gradle/gradle-build-action@v3
      - run: ./gradlew bootJar

      - name: Build artifact upload
        uses: actions/upload-artifact@v4
        with:
          name: jars
          path: '**/build/libs/*.jar'

  image:
    runs-on: ubuntu-latest
    needs: build
    if: github.event_name == 'push'    # PR에서는 이미지 빌드 X
    permissions:
      packages: write
    strategy:
      matrix:
        service: [gateway, bff-aggregator, auth-service, bible-service, ai-service, journal-service]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Build + Push (${{ matrix.service }})
        uses: docker/build-push-action@v5
        with:
          context: ${{ matrix.service }}
          file: ${{ matrix.service }}/Dockerfile
          push: true
          tags: |
            ghcr.io/tae0072/qtai-${{ matrix.service }}:${{ github.sha }}
            ghcr.io/tae0072/qtai-${{ matrix.service }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-dev:
    runs-on: ubuntu-latest
    needs: image
    if: github.ref == 'refs/heads/develop'
    environment: dev
    steps:
      - uses: actions/checkout@v4

      - name: kubeconfig 설정
        run: |
          mkdir -p ~/.kube
          echo "${{ secrets.KUBECONFIG_DEV }}" | base64 -d > ~/.kube/config
          chmod 600 ~/.kube/config

      - name: helm upgrade --install
        run: |
          helm upgrade --install qtai ./helm/qtai-umbrella \
            --namespace qtai \
            --values ./helm/qtai-umbrella/values.yaml \
            --values ./helm/qtai-umbrella/values-dev.yaml \
            --set image.tag=${{ github.sha }} \
            --atomic --timeout 5m \
            --wait

      - name: 배포 검증 (smoke test)
        run: |
          # /actuator/health 6 service 모두 통과 확인
          for svc in gateway auth bible ai journal bff-aggregator; do
            kubectl wait --for=condition=Available --timeout=120s \
              deployment/$svc -n qtai
          done
```

### 3.4 머지 게이트 정책

> 모든 PR은 다음 모두 통과해야 머지 가능. GitHub Branch Protection Rule:

- [ ] **gitleaks** — 시크릿 패턴 0건
- [ ] **Spotless** — 코드 스타일 위반 0건
- [ ] **Spectral** — OpenAPI lint error 0건
- [ ] **단위 테스트** — JUnit 통과
- [ ] **통합 테스트** — Testcontainers 통과
- [ ] **OWASP Dependency-Check** — CVE 7.0+ 0건
- [ ] **Reviewer 1명 승인** — service owner가 아닌 다른 사람 (Lead 자기 머지 금지 — 03번)
- [ ] **branch up-to-date** — develop 최신 반영

PR 머지 후 자동 develop 배포 → 실패 시 Slack `#qtai-deploy` 알람.

### 3.5 secrets 운영 (GitHub Secrets)

| Secret 이름 | 용도 |
| --- | --- |
| `GITHUB_TOKEN` | (자동) image push, Action 인증 |
| `KUBECONFIG_DEV` | dev cluster 접근 (base64 encoded) |
| `KUBECONFIG_DEMO` | demo cluster 접근 |
| `SLACK_WEBHOOK_DEPLOY` | `#qtai-deploy` 알람 |
| `SLACK_WEBHOOK_INCIDENT` | `#qtai-incident` 알람 |

> **금지:** Anthropic API key·Google OAuth·DB 비밀번호는 GitHub Secrets에 두지 않음 — K8s Secret만 (05번 § 5.4). GitHub Secrets는 CI/CD 자체 운영용만.

---

## 4. 컨테이너 이미지 표준

### 4.1 Dockerfile 표준 (Spring Boot 3 service)

```dockerfile
# {service}/Dockerfile (6 service 모두 동일 패턴)

# ===== 1단계: build =====
FROM eclipse-temurin:21-jdk-alpine AS build
WORKDIR /app

COPY build.gradle.kts settings.gradle.kts ./
COPY gradle/ gradle/
COPY gradlew ./
RUN ./gradlew --no-daemon dependencies

COPY src/ src/
RUN ./gradlew --no-daemon bootJar

# ===== 2단계: runtime =====
FROM eclipse-temurin:21-jre-alpine
WORKDIR /app

# 비루트 사용자 생성 (05번 § 5.5 securityContext.runAsNonRoot)
RUN addgroup -S qtai && adduser -S qtai -G qtai
USER qtai

COPY --from=build --chown=qtai:qtai /app/build/libs/*.jar app.jar

EXPOSE 8080

# JVM 옵션 (Alpine + container memory cgroup)
ENV JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75 -XX:+ExitOnOutOfMemoryError"

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=60s --retries=3 \
  CMD wget -q -O - http://localhost:8080/actuator/health/liveness || exit 1

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/app.jar"]
```

> **주의 사항:**
> - 멀티 stage build로 이미지 크기 ~200MB 유지 (build stage 200MB+ 분리)
> - `USER qtai` 로 비루트 실행 (privilege escalation 방어)
> - `--chown=qtai:qtai` 로 jar 소유권 비루트
> - JVM heap 자동 조정 (`MaxRAMPercentage`)
> - HEALTHCHECK는 K8s liveness probe와 별도 (Docker 자체 — 없어도 OK이지만 로컬 docker run 디버깅용)

### 4.2 이미지 명명 규칙

```
ghcr.io/tae0072/qtai-{service}:{git_sha}
ghcr.io/tae0072/qtai-{service}:latest
ghcr.io/tae0072/qtai-{service}:v{semver}    (release tag만)
```

| Tag | 용도 |
| --- | --- |
| `{git_sha}` (40자) | **운영 배포 표준** (immutable, 정확히 어느 commit인지 추적) |
| `latest` | dev 환경 편의용 — **운영 배포 금지** (mutable) |
| `v0.1.0` (semver) | release tag (v1.1) — 시연 직전 박제 |

### 4.3 .dockerignore 표준

```
# {service}/.dockerignore
.git
.gitignore
.gradle
build/
**/build/
**/.idea
**/*.iml
**/test/
README.md
*.md
.env*
!.env.example
*.pem
*.key
secrets.yaml
```

> 민감 파일·테스트·문서는 이미지에 포함 X. 이미지 layer 누출 방어 (05번 § 5.5).

### 4.4 이미지 보안 점검 (v1.1)

| 점검 | v1.0 | v1.1 |
| --- | --- | --- |
| Trivy 컨테이너 취약점 스캔 | ❌ Dependency-Check만 | GHA에 `trivy-action` 추가 |
| Cosign 이미지 서명 | ❌ | 운영 환경 도입 시 |
| SBOM (Software Bill of Materials) | ❌ | Syft 도입 검토 |

---

## 5. Helm Chart 운영

### 5.1 Chart 구조

```
helm/
├── qtai-umbrella/                         # 6 service umbrella chart
│   ├── Chart.yaml                         # version, dependencies
│   ├── values.yaml                        # 기본값 (replicas, image tag, 등)
│   ├── values-dev.yaml                    # dev override
│   ├── values-demo.yaml                   # demo override
│   ├── charts/                            # subchart 묶음 (선택)
│   └── templates/
│       ├── _helpers.tpl                   # 템플릿 함수
│       ├── gateway-deployment.yaml
│       ├── gateway-service.yaml
│       ├── gateway-networkpolicy.yaml     # 05번 § 6.1
│       ├── bff-deployment.yaml
│       ├── bff-service.yaml
│       ├── bff-networkpolicy.yaml
│       ├── auth-deployment.yaml
│       ├── auth-service.yaml
│       ├── auth-networkpolicy.yaml
│       ├── ... (bible/ai/journal 동일 패턴)
│       ├── default-deny-networkpolicy.yaml  # § 6.1.1
│       └── ingress.yaml                   # Gateway 외부 노출
│
└── qtai-infra/                            # 인프라 (MySQL, Redis, Kafka, ChromaDB)
    ├── Chart.yaml
    ├── values.yaml
    └── templates/
        ├── mysql-statefulset.yaml
        ├── mysql-pvc.yaml
        ├── redis-cache-deployment.yaml
        ├── redis-ws-deployment.yaml
        ├── kafka-statefulset.yaml         # KRaft single-node
        ├── schema-registry-deployment.yaml
        ├── chromadb-statefulset.yaml
        └── observability-stack.yaml       # Loki, Prometheus, Jaeger
```

### 5.2 values.yaml 표준 (qtai-umbrella)

```yaml
# helm/qtai-umbrella/values.yaml
global:
  imageRegistry: ghcr.io/tae0072
  imagePullPolicy: IfNotPresent
  imagePullSecrets:
    - name: ghcr-pull-secret

# 공통 secret 참조
secrets:
  qtaiSecretName: qtai-secrets    # 05번 § 5.4 K8s Secret

services:
  gateway:
    image:
      repository: qtai-gateway
      tag: latest                 # CI에서 git_sha로 override
    replicas: 1
    resources:
      requests: { cpu: 100m, memory: 256Mi }
      limits:   { cpu: 500m, memory: 512Mi }
    env:
      JAVA_OPTS: "-XX:MaxRAMPercentage=75"

  bff-aggregator:
    image: { repository: qtai-bff-aggregator, tag: latest }
    replicas: 2                   # WS 다중 Pod (03번 § 1.1)
    resources:
      requests: { cpu: 200m, memory: 512Mi }
      limits:   { cpu: 1000m, memory: 1Gi }

  auth-service:
    image: { repository: qtai-auth-service, tag: latest }
    replicas: 1
    resources:
      requests: { cpu: 200m, memory: 512Mi }
      limits:   { cpu: 500m, memory: 1Gi }

  bible-service:
    image: { repository: qtai-bible-service, tag: latest }
    replicas: 1
    resources:
      requests: { cpu: 200m, memory: 512Mi }
      limits:   { cpu: 500m, memory: 1Gi }

  ai-service:
    image: { repository: qtai-ai-service, tag: latest }
    replicas: 1
    resources:
      requests: { cpu: 500m, memory: 1Gi }    # LLM 호출용 여유 메모리
      limits:   { cpu: 1000m, memory: 2Gi }

  journal-service:
    image: { repository: qtai-journal-service, tag: latest }
    replicas: 1
    resources:
      requests: { cpu: 200m, memory: 512Mi }
      limits:   { cpu: 500m, memory: 1Gi }

# Health probe 표준
probes:
  liveness:
    path: /actuator/health/liveness
    initialDelaySeconds: 60
    periodSeconds: 30
  readiness:
    path: /actuator/health/readiness
    initialDelaySeconds: 30
    periodSeconds: 10

# securityContext 표준 (05번 § 5.5)
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

containerSecurityContext:
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop: ["ALL"]
```

### 5.3 values-dev.yaml override

```yaml
# helm/qtai-umbrella/values-dev.yaml
global:
  environment: dev

services:
  gateway:
    env:
      LOG_LEVEL: DEBUG
      SPRING_PROFILES_ACTIVE: dev
  ai-service:
    env:
      LOG_LEVEL: DEBUG
      ANTHROPIC_MODEL: claude-haiku-4-5    # dev는 저렴한 모델 (비용 절약)
```

### 5.4 _helpers.tpl 표준

```yaml
# helm/qtai-umbrella/templates/_helpers.tpl
{{/* 표준 라벨 */}}
{{- define "qtai.labels" -}}
app.kubernetes.io/name: {{ .name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: Helm
app.kubernetes.io/part-of: qtai
app.kubernetes.io/environment: {{ .Values.global.environment }}
{{- end -}}

{{/* 컨테이너 securityContext */}}
{{- define "qtai.containerSecurityContext" -}}
securityContext:
  readOnlyRootFilesystem: {{ .Values.containerSecurityContext.readOnlyRootFilesystem }}
  allowPrivilegeEscalation: {{ .Values.containerSecurityContext.allowPrivilegeEscalation }}
  capabilities:
    drop:
      {{- toYaml .Values.containerSecurityContext.capabilities.drop | nindent 6 }}
{{- end -}}
```

### 5.5 deployment 템플릿 예 (auth-service)

```yaml
# helm/qtai-umbrella/templates/auth-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: auth-service
  namespace: {{ .Release.Namespace }}
  labels:
    {{- include "qtai.labels" (dict "name" "auth-service" "Release" .Release "Chart" .Chart "Values" .Values) | nindent 4 }}
spec:
  replicas: {{ .Values.services.authService.replicas }}
  selector:
    matchLabels:
      app.kubernetes.io/name: auth-service
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0          # zero-downtime
  template:
    metadata:
      labels:
        app.kubernetes.io/name: auth-service
    spec:
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: auth-service
        image: "{{ .Values.global.imageRegistry }}/{{ .Values.services.authService.image.repository }}:{{ .Values.services.authService.image.tag }}"
        imagePullPolicy: {{ .Values.global.imagePullPolicy }}
        ports:
        - containerPort: 8080
        env:
        - name: SPRING_DATASOURCE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: {{ .Values.secrets.qtaiSecretName }}
              key: mysql-password
        - name: JWT_PRIVATE_KEY_PATH
          value: /etc/qtai/jwt/private.pem
        volumeMounts:
        - name: jwt-keys
          mountPath: /etc/qtai/jwt
          readOnly: true
        - name: tmp
          mountPath: /tmp
        resources:
          {{- toYaml .Values.services.authService.resources | nindent 10 }}
        {{- include "qtai.containerSecurityContext" . | nindent 8 }}
        livenessProbe:
          httpGet:
            path: {{ .Values.probes.liveness.path }}
            port: 8080
          initialDelaySeconds: {{ .Values.probes.liveness.initialDelaySeconds }}
          periodSeconds: {{ .Values.probes.liveness.periodSeconds }}
        readinessProbe:
          httpGet:
            path: {{ .Values.probes.readiness.path }}
            port: 8080
          initialDelaySeconds: {{ .Values.probes.readiness.initialDelaySeconds }}
          periodSeconds: {{ .Values.probes.readiness.periodSeconds }}
      volumes:
      - name: jwt-keys
        secret:
          secretName: {{ .Values.secrets.qtaiSecretName }}
          items:
          - key: jwt-private.pem
            path: private.pem
            mode: 0400
      - name: tmp
        emptyDir: {}              # readOnlyRootFilesystem이라 /tmp는 별도 mount
```

### 5.6 helm lint + helm template 머지 게이트

```yaml
# .github/workflows/ci.yml — lint job에 추가
- name: Helm lint
  run: |
    helm lint ./helm/qtai-umbrella --values ./helm/qtai-umbrella/values-dev.yaml
    helm lint ./helm/qtai-infra
- name: Helm template (rendering 검증)
  run: |
    helm template qtai ./helm/qtai-umbrella \
      --values ./helm/qtai-umbrella/values-dev.yaml \
      --debug | kubectl apply --dry-run=client -f -
```

---

## 6. 배포 절차 (Deploy Runbook)

### 6.1 정기 배포 절차 (`develop` → dev 환경)

```
[1] PR 머지 (develop)
    └─ 자동 트리거: GHA ci.yml deploy-dev job

[2] GHA가 helm upgrade --install --atomic 실행
    └─ --atomic: 실패 시 자동 rollback
    └─ --timeout 5m: 5분 안에 안 끝나면 rollback

[3] Pod readiness 확인
    └─ kubectl wait deployment/{각 service} --for=condition=Available

[4] Smoke test (자동)
    └─ /actuator/health 6 service 200 OK
    └─ /api/v1/auth/login 시도 → 200 또는 401 (검증된 응답 형식)

[5] Slack #qtai-deploy 알람
    └─ "✅ qtai dev 배포 완료 — {git_sha} ({커밋 메시지 1줄})"
    └─ 실패 시: "🚨 qtai dev 배포 실패 — rollback 완료 — 강태오 확인 필요"
```

### 6.2 수동 배포 절차 (강태오 로컬에서)

```bash
# 1. main 브랜치 최신화
git checkout main
git pull origin main

# 2. K8s 클러스터 컨텍스트 확인
kubectl config use-context minikube
kubectl get ns qtai

# 3. 시크릿 적재 확인 (없으면 W0 절차로 적재 — 05번 § 5.4)
kubectl get secret qtai-secrets -n qtai

# 4. 인프라 배포 (변경 시만)
helm upgrade --install qtai-infra ./helm/qtai-infra \
  --namespace qtai \
  --create-namespace \
  --atomic --timeout 10m

# 5. 인프라 ready 대기
kubectl wait --for=condition=Ready pod -l app=mysql -n qtai --timeout=5m
kubectl wait --for=condition=Ready pod -l app=kafka -n qtai --timeout=5m

# 6. 서비스 배포
GIT_SHA=$(git rev-parse HEAD)
helm upgrade --install qtai ./helm/qtai-umbrella \
  --namespace qtai \
  --values ./helm/qtai-umbrella/values.yaml \
  --values ./helm/qtai-umbrella/values-dev.yaml \
  --set image.tag=$GIT_SHA \
  --atomic --timeout 5m

# 7. 검증
kubectl get pods -n qtai
kubectl logs -f deployment/auth-service -n qtai

# 8. 외부 접근 확인 (Ingress 또는 minikube tunnel)
minikube tunnel    # 다른 터미널에서
curl http://qtai.local/actuator/health
```

### 6.3 Flyway DB Migration 운영

> 각 service Pod 시작 시 자동 실행 (`spring.flyway.enabled=true`).

| 시나리오 | 절차 |
| --- | --- |
| 새 컬럼 추가 | service owner가 `V{n+1}__add_column.sql` 작성 → PR → 머지 → 자동 배포 시 적용 |
| 컬럼 제거·이름 변경 | **2단계 배포 필수**: (1) 새 컬럼 추가 + 양쪽 쓰기 (2) 다음 배포에 옛 컬럼 제거 |
| 시드 데이터 추가 | `V{n+1}__seed_x.sql` 작성 (`INSERT IGNORE` 또는 `ON DUPLICATE KEY`) |
| 인덱스 추가 (대용량 테이블) | `ALGORITHM=INPLACE, LOCK=NONE` 명시 (MySQL 8) |
| 잘못된 V 버전 충돌 | `spring.flyway.repair=true` 일회성 적용 후 다시 false (운영자만) |

> **금지:** 운영 DB에 직접 `ALTER TABLE` 손으로. 모두 Flyway migration으로.

### 6.4 Hotfix 배포 절차

```
[발견] P0/P1 사고 또는 시연 직전 critical 버그

[1] 강태오 + service owner 즉시 통화
[2] hotfix 브랜치 생성: git checkout -b hotfix/{이슈번호}-{설명} main
[3] 최소 변경 + 단위 테스트
[4] PR 생성 → 1명 리뷰 (Lead 자기 머지 금지 규칙은 hotfix에도 적용 — 03번)
[5] develop·main 동시 머지
[6] dev·demo 환경 동시 배포
[7] 검증 → Slack #qtai-incident 보고
[8] 24h 안에 post-mortem (Notion)
```

---

## 7. Rollback 절차

### 7.1 자동 Rollback (Helm `--atomic`)

> `helm upgrade --atomic` 옵션 사용 시 다음 조건에 자동 rollback:
> - timeout 초과 (기본 5m)
> - Pod readiness 실패
> - 사용자 ctrl+c

```bash
# 자동 rollback이 발생하면 release는 이전 revision으로 복원됨
helm history qtai -n qtai
# REVISION  STATUS      DESCRIPTION
# 5         deployed    Upgrade complete   ← 현재 (rollback된 이전 버전)
# 6         failed      Upgrade timeout    ← 시도된 새 버전 (실패)
```

### 7.2 수동 Rollback

```bash
# 1. 현재 release history 확인
helm history qtai -n qtai

# 2. 직전 revision으로 rollback
helm rollback qtai 0 -n qtai
# 또는 특정 revision으로
helm rollback qtai 5 -n qtai --timeout 5m --wait

# 3. Pod 상태 확인
kubectl get pods -n qtai

# 4. Slack #qtai-deploy 알람 (수동)
```

### 7.3 DB Migration Rollback

> Flyway는 **forward-only** 원칙. `migrate-down` 미지원.

| 시나리오 | 대응 |
| --- | --- |
| 컬럼 추가만 했음 | 코드만 rollback, DB 컬럼은 그대로 (사용 안 함) |
| 컬럼 데이터 변경 | DB 백업에서 복원 (§ 9 백업 절차) |
| 데이터 손상 | 운영 환경 freeze + 강태오 + service owner 즉시 통화 |

> **운영 핵심 원칙:** "DB 변경은 backward-compatible로만." 항상 새 컬럼 추가 + 코드에서 양쪽 쓰기 → 다음 배포에 옛 컬럼 제거. 단일 배포에 컬럼 제거 + 코드 변경 동시 X.

### 7.4 시크릿 Rollback (05번 § 10.3 시나리오 참조)

JWT private key 유출 시 → 새 키 발급 + 점진적 rotation. K8s Secret 자체 rollback은 사용 안 함 (이전 버전이 유출본일 수 있음).

---

## 8. 관측성 운영 (Loki · Prometheus · Jaeger)

### 8.1 Stack 토폴로지 (03번 § 1.1 + § 8 정합)

```
[6 service]
   │
   │ /metrics  (Micrometer + Prometheus exporter)
   │ stdout JSON log (Logstash encoder)
   │ OTLP trace (OpenTelemetry SDK → otel-collector)
   ▼
┌─────────────── observability namespace ─────────────────┐
│                                                          │
│  Promtail (DaemonSet)  ─── Loki (StatefulSet)            │
│                              │                           │
│  Prometheus (Deployment)  ──┼─── Grafana (Deployment)    │
│                              │                           │
│  Jaeger (collector + UI) ───┘                            │
│                                                          │
│  OTel Collector (Deployment)                             │
└─────────────────────────────────────────────────────────┘
```

### 8.2 Loki 로그 수집

#### 8.2.1 Promtail 설정 (DaemonSet — 노드별 1개)

```yaml
# helm/qtai-infra/templates/promtail-daemonset.yaml (개념)
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: promtail
  namespace: observability
spec:
  selector:
    matchLabels: { app: promtail }
  template:
    spec:
      containers:
      - name: promtail
        image: grafana/promtail:3.1.0
        args:
        - -config.file=/etc/promtail/config.yml
        volumeMounts:
        - name: config
          mountPath: /etc/promtail
        - name: var-log
          mountPath: /var/log
          readOnly: true
        - name: var-lib-docker-containers
          mountPath: /var/lib/docker/containers
          readOnly: true
      volumes:
      - name: config
        configMap: { name: promtail-config }
      - name: var-log
        hostPath: { path: /var/log }
      - name: var-lib-docker-containers
        hostPath: { path: /var/lib/docker/containers }
```

```yaml
# Promtail config (configmap)
scrape_configs:
- job_name: kubernetes-pods
  kubernetes_sd_configs:
    - role: pod
  relabel_configs:
    # 자동으로 namespace, pod, container 라벨 추출
    - source_labels: [__meta_kubernetes_namespace]
      target_label: namespace
    - source_labels: [__meta_kubernetes_pod_label_app_kubernetes_io_name]
      target_label: service
  pipeline_stages:
    - json:
        expressions:
          level: level
          trace_id: trace_id
          audit_event: audit_event
    - labels:
        level:
        audit_event:
```

#### 8.2.2 Loki retention

| 로그 종류 | 보관 |
| --- | --- |
| application log | 30일 |
| audit log (`{audit_event=~".+"}`) | 90일 |
| Promtail 자체 | 7일 |

### 8.3 Prometheus 메트릭 + alert

#### 8.3.1 핵심 메트릭

| 메트릭 | 의미 | 알람 조건 |
| --- | --- | --- |
| `up{job="qtai"}` | service 가동 여부 | 5분 이상 0 → P0 |
| `http_server_requests_seconds_count{status=~"5.."}` | 5xx 응답 빈도 | rate > 1/s for 5m → P1 |
| `http_server_requests_seconds_count{status="429"}` | Rate limit 초과 | rate > 50/5m → P2 |
| `qtai_audit_event_total{audit_event="login.failure"}` | 로그인 실패 | rate > 1/min for 2m → P2 (brute-force) |
| `kafka_consumer_records_lag_max` | Kafka consumer lag | > 1000 for 10m → P1 |
| `kafka_publish_failure_total` | Kafka publish 실패 (03번 § 6.1) | > 0 → P1 |
| `jvm_memory_used_bytes / jvm_memory_max_bytes` | JVM heap 사용률 | > 90% for 10m → P1 |
| `mysql_global_status_threads_running` | MySQL 활성 쓰레드 | > 50 → P2 |
| `redis_connected_clients` | Redis 연결 수 | > 100 → P2 |
| `anthropic_api_request_duration_seconds` | Claude 응답 latency | p95 > 10s for 5m → P2 |
| `anthropic_api_failure_total` | Claude 호출 실패 | rate > 5/m → P1 |

#### 8.3.2 alert rule 예

```yaml
# helm/qtai-infra/templates/prometheus-alert-rules.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: qtai-alerts
  namespace: observability
spec:
  groups:
  - name: qtai.availability
    rules:
    - alert: ServiceDown
      expr: up{job="qtai"} == 0
      for: 5m
      labels: { severity: P0 }
      annotations:
        summary: "{{ $labels.instance }} service down for 5m"
        runbook: "https://github.com/Tae0072/2nd-Team-Project/blob/main/06_DevOps_운영_매뉴얼.md#103-시나리오-service-pod-crash"

    - alert: HighErrorRate
      expr: |
        sum(rate(http_server_requests_seconds_count{status=~"5..", job="qtai"}[5m])) by (instance) > 1
      for: 5m
      labels: { severity: P1 }
      annotations:
        summary: "{{ $labels.instance }} 5xx 에러율 > 1/s"

  - name: qtai.security
    rules:
    - alert: HighLoginFailureRate
      expr: rate(qtai_audit_event_total{audit_event="login.failure"}[5m]) > 1
      for: 2m
      labels: { severity: P2 }
      annotations:
        summary: "분당 1회 이상 로그인 실패 — brute-force 가능성 (05번 § 10)"

  - name: qtai.kafka
    rules:
    - alert: KafkaConsumerLag
      expr: kafka_consumer_records_lag_max > 1000
      for: 10m
      labels: { severity: P1 }
      annotations:
        summary: "Kafka consumer lag {{ $value }}"
```

### 8.4 Jaeger 분산 트레이싱

| 항목 | 표준 |
| --- | --- |
| Trace ID 전파 | W3C Trace Context (`traceparent` 헤더 — 04번 § 2.2) |
| Sampling rate | dev: 100%, demo: 10% |
| Retention | 7일 |
| Span 명명 | `{HTTP method} {operationId}` (예: `GET getJournals`) |

> **중요:** 모든 service 간 호출·Kafka publish/consume·Anthropic 호출은 모두 trace에 포함. 사용자 신고 시 `trace_id` (04번 § 2.4 ProblemDetail)로 즉시 조회.

### 8.5 Grafana 대시보드 표준

> W1에 강태오가 4개 대시보드 작성. JSON 파일을 `helm/qtai-infra/templates/grafana-dashboards/` 디렉토리에 박제.

| 대시보드 | 지표 |
| --- | --- |
| **QT-AI Overview** | 6 service up/down, request rate, error rate, p95 latency |
| **QT-AI Kafka** | producer rate, consumer lag, DLQ, schema registry 동기화 |
| **QT-AI Database** | MySQL connection pool, slow query, Redis hit rate, ChromaDB |
| **QT-AI Security** | login failure rate, rate limit 429, audit event 종류별 빈도 |

> **운영 시작 직전 (시연 -1주 5/15)**: 4개 대시보드 모두 가동 검증.

---

## 9. 백업·복구 절차

### 9.1 백업 대상

| 자원 | 백업 빈도 | 보관 | 도구 |
| --- | --- | --- | --- |
| MySQL (auth, bible, ai, journal schema) | 일 1회 (03:00 KST) | 7일 | mysqldump → PVC + S3 (v1.1) |
| ChromaDB | 일 1회 | 7일 | 컬렉션 export → PVC |
| Kafka topic (이벤트 자체) | ❌ v1.0 미백업 | — | 이벤트는 producer 재발행 보상 (03번 § 6.1) |
| K8s Secret (jwt-keys 등) | 적재 시 1회 (수동, 안전한 곳) | 영구 | 강태오 보관 |
| Helm release | 자동 (Helm history 10개) | — | `helm history` |

### 9.2 MySQL 일일 백업 (CronJob)

```yaml
# helm/qtai-infra/templates/mysql-backup-cronjob.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: mysql-backup
  namespace: qtai
spec:
  schedule: "0 18 * * *"        # UTC 18:00 = KST 03:00
  jobTemplate:
    spec:
      template:
        spec:
          restartPolicy: OnFailure
          containers:
          - name: mysqldump
            image: mysql:8.0
            command:
            - /bin/sh
            - -c
            - |
              TS=$(date +%Y%m%d-%H%M)
              mysqldump -h mysql -u root -p"$MYSQL_PASSWORD" \
                --databases auth_db bible_db ai_db journal_db \
                --single-transaction --triggers --routines --events \
                | gzip > /backup/qtai-${TS}.sql.gz
              # 7일 이전 백업 삭제
              find /backup -name "qtai-*.sql.gz" -mtime +7 -delete
            env:
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef: { name: qtai-secrets, key: mysql-password }
            volumeMounts:
            - name: backup
              mountPath: /backup
          volumes:
          - name: backup
            persistentVolumeClaim:
              claimName: mysql-backup-pvc
```

### 9.3 복구 시나리오

#### 9.3.1 단일 사용자 데이터 실수 삭제

```bash
# 1. 직전 백업에서 해당 사용자만 추출
kubectl exec -it mysql-0 -n qtai -- bash
mysql -u root -p
> SELECT * FROM auth_db.users WHERE id=5678;    # 현재 상태 확인

# 2. 백업에서 해당 row만 INSERT (Soft Delete 복원)
> SOURCE /backup/qtai-20260526.sql.gz의 users 부분 추출;
> UPDATE auth_db.users SET deleted_at=NULL, email='original@example.com'
   WHERE id=5678;
```

#### 9.3.2 전체 DB 손상 (P0)

```bash
# 1. 운영 freeze (Slack #qtai-incident 알림)
# 2. mysql StatefulSet scale 0
kubectl scale statefulset mysql --replicas=0 -n qtai

# 3. 백업 PVC 마운트한 임시 Pod에서 복구
kubectl run mysql-restore --image=mysql:8.0 --rm -it -n qtai -- bash
> gunzip < /backup/qtai-20260526.sql.gz | mysql -h mysql-restore -u root -p

# 4. mysql StatefulSet scale 1
kubectl scale statefulset mysql --replicas=1 -n qtai

# 5. 6 service Pod 재시작 (DB 재연결)
kubectl rollout restart deployment -n qtai

# 6. 검증 → 운영 재개
```

### 9.4 Disaster Recovery (DR) 시나리오 — v1.0 한계

> v1.0 Minikube 단일 노드라 DR 시나리오 제한적. 노드 자체 손상 시 처음부터 재배포 필요.

| 시나리오 | v1.0 대응 | v1.1 |
| --- | --- | --- |
| Pod crash | Helm rollback | 동일 |
| 노드 디스크 손상 | 백업에서 복구 (수 시간) | 다중 노드 + replication |
| 클러스터 전체 손상 | 처음부터 재배포 (수 시간) | Multi-AZ |
| 데이터센터 손상 | (해당 없음 — Minikube) | Multi-region |

---

## 10. Incident Runbook (시나리오별)

### 10.1 시나리오 분류 (05번 § 10.1 등급 정합)

| 시나리오 | 등급 | 평균 대응 시간 | 본 절차 |
| --- | --- | --- | --- |
| 1. JWT private key 유출 | P0 | 30분 | 05번 § 10.3 |
| 2. MySQL 다운 | P0 | 30분 | § 10.2 |
| 3. service Pod crash loop | P1 | 30분 | § 10.3 |
| 4. Kafka consumer lag 폭증 | P1 | 1h | § 10.4 |
| 5. Anthropic API 5xx 다발 | P1 | 1h | § 10.5 |
| 6. SSE 끊김 다발 | P2 | 1h | § 10.6 |
| 7. ChromaDB 응답 없음 | P2 | 1h | § 10.7 |
| 8. Refresh token 대량 차단 | P2 | 2h | § 10.8 |
| 9. CI/CD 머지 게이트 우회 시도 | P2 | 2h | § 10.9 |

### 10.2 시나리오: MySQL 다운 (P0)

**증상:**
- Prometheus alert: `up{app="mysql"} == 0`
- 6 service 모두 5xx 응답
- 사용자 로그인 불가

**대응:**
```
T+0: alert 수신
T+2: 강태오 Slack #qtai-incident 공지 ("MySQL down 조사 중")
T+5: kubectl describe pod mysql-0 -n qtai
       └─ OOMKilled? PVC mount 실패? Image pull 실패?
T+10: 원인별 대응
       ├─ OOMKilled → resources.limits 증가 (values.yaml) → helm upgrade
       ├─ PVC 손상 → § 9.3.2 복구 절차
       └─ 알 수 없음 → kubectl rollout restart statefulset/mysql -n qtai
T+20: 검증 (auth-service login 시도)
T+25: 정상 → Slack #qtai-incident "복구 완료"
T+24h: post-mortem 작성
```

### 10.3 시나리오: service Pod crash loop (P1)

**증상:**
- `kubectl get pods -n qtai` → STATUS = `CrashLoopBackOff`
- Prometheus alert: `up{job="qtai"} == 0`

**대응:**
```bash
# 1. 로그 확인
kubectl logs -n qtai pod/auth-service-xxxx --previous   # 직전 crash 로그

# 2. 원인별 분기
# 2-1) OOMKilled
kubectl describe pod auth-service-xxxx -n qtai | grep -i killed
# → resources.limits.memory 증가

# 2-2) DB 연결 실패
kubectl logs ... | grep -i "Connection refused"
# → MySQL 상태 확인 → § 10.2

# 2-3) Application 코드 NPE / Exception
kubectl logs ... | grep -i Exception
# → hotfix 또는 직전 release rollback (§ 7.2)

# 2-4) ConfigMap/Secret 로드 실패
kubectl describe pod ... | grep -i "MountVolume.SetUp failed"
# → kubectl get secret qtai-secrets -n qtai 존재 확인

# 3. 일시 조치 — 직전 release rollback
helm rollback qtai 0 -n qtai

# 4. 정밀 조치 — hotfix PR (§ 6.4)
```

### 10.4 시나리오: Kafka consumer lag 폭증 (P1)

**증상:**
- alert: `kafka_consumer_records_lag_max > 1000 for 10m`
- 사용자 작업이 늦게 반영 (예: AI 세션 완료 후 Journal 생성 지연)

**대응:**
```bash
# 1. 어느 토픽·그룹이 lag인지 확인
kubectl exec -it kafka-0 -n qtai -- \
  kafka-consumer-groups.sh --bootstrap-server localhost:9092 \
    --describe --group journal-service-ai-completion-consumer

# 2. consumer 단위 분석
# 2-1) consumer Pod 다운 → § 10.3
# 2-2) consumer 처리 시간 ↑ → 코드 hotfix
# 2-3) 단순 backlog → consumer Pod replicas 증가
kubectl scale deployment journal-service --replicas=2 -n qtai

# 3. DLQ 확인 (영구 실패 메시지)
kubectl exec -it kafka-0 -n qtai -- \
  kafka-console-consumer.sh --bootstrap-server localhost:9092 \
    --topic ai.session.completed.DLQ --from-beginning --max-messages 10

# 4. journal.creation.failed 토픽 발행 검증 (Saga 보상 — 03번 § 6.1)
```

### 10.5 시나리오: Anthropic API 5xx 다발 (P1)

**증상:**
- alert: `anthropic_api_failure_total rate > 5/m`
- AI 응답 SSE 504 응답 (04번 § 6.3 `LLM_TIMEOUT`)

**대응:**
- Anthropic Status 페이지 확인 → provider 사이드 장애면 대기 + 사용자 안내
- 자체 사이드 → API key 만료? Rate limit (분당 호출 한도) ? `kubectl logs -n qtai deployment/ai-service`
- 일시 fallback (v1.1): 다른 모델 (claude-haiku-4-5)로 자동 전환. v1.0은 사용자 안내만

### 10.6 시나리오: SSE 끊김 다발 (P2)

**증상:**
- 사용자 신고: AI 응답이 도중에 끊김
- BFF 또는 ai-service 로그에 `Stream closed prematurely`

**대응:**
- Gateway 로그 확인: `kubectl logs deployment/gateway -n qtai | grep -i sse`
- 04번 § 9.6 금지 filter 적용되어 있는지 (응답 buffering filter는 SSE 깨뜨림)
- timeout 설정 확인 (Gateway readTimeout, ai-service idle timeout)

### 10.7 시나리오: ChromaDB 응답 없음 (P2)

**대응:**
- ChromaDB Pod 상태 확인 → 재시작
- AI Service는 RAG 응답 없으면 신학 가드레일 위반 → 사용자에게 `ASSISTANT 턴 거부` (03번 § 3.3)

### 10.8 시나리오: Refresh token 대량 차단 (P2)

**증상:**
- audit log `refresh.blocked` 빈도 ↑
- 사용자 강제 로그아웃 신고

**대응:**
- Redis-WS 상태 확인 (정상 작동인가)
- Distributed Lock 로직 확인 (04번 § 4.4)
- 의심 시 1차로 사용자 재로그인 안내 + 본질 원인 hotfix

### 10.9 시나리오: CI/CD 머지 게이트 우회 시도 (P2)

**증상:**
- gitleaks 또는 Spectral 우회 commit 발견
- branch protection 룰 위반

**대응:**
- 즉시 revert PR
- branch protection 룰 강화 (admin도 우회 불가)
- 강태오가 commit 작성자와 1:1 대화 + post-mortem

---

## 11. 온콜·통신 정책

### 11.1 v1.0 단순화

| 시기 | 온콜 | 비고 |
| --- | --- | --- |
| W1~W3 (5/18~6/5) | ❌ 9-to-5 best effort | 강태오 평일 9~18 KST |
| W4~W5 (6/8~6/17 시연 직전) | 강태오 단독 24/7 | 시연 D-7 강화 |
| 시연 당일 (5/27, 6/3, 6/17) | 전원 비상 대기 | freeze + 즉시 대응 |

> v1.1에 이지윤·이승욱 추가 온콜 검토.

### 11.2 통신 채널 (04번 § 1.4 정합)

| 채널 | 용도 | 알람 트리거 |
| --- | --- | --- |
| `#qtai-deploy` | 배포 시작·완료·실패 알람 | GHA → Slack webhook 자동 |
| `#qtai-incident` | 사고 대응 (P0/P1) | Prometheus alertmanager → webhook 자동 |
| `#qtai-api` | API 변경·계약 논의 | 수동 |
| 강태오 DM | P0 즉시 호출 | alertmanager → SMS (v1.1) / 현재는 Slack DM 푸시 |

### 11.3 사고 보고 템플릿 (Notion)

```markdown
# Incident Report — {YYYY-MM-DD} {제목}

## 요약
- 등급: P0 / P1 / P2 / P3
- 발생 시각: 2026-MM-DD HH:MM KST
- 복구 시각: 2026-MM-DD HH:MM KST
- 영향 범위: 사용자 N명 / N분 다운

## 타임라인
- T+0: 증상 인지
- T+M: 1차 대응
- T+N: 복구 완료

## 원인 (Root Cause)
- 직접 원인:
- 근본 원인:

## 영향
- 사용자: N명 (어떤 식으로)
- 데이터: 손실 X / N건 손실 / N건 일시 누락

## 재발 방지
- [ ] {조치 1} (담당: 강태오, 기한: M-D)
- [ ] {조치 2}
- [ ] ADR-XXXX 발행 (필요 시)

## 학습
- 잘한 점:
- 개선할 점:
```

---

## 12. 1차(HMS) 실패 패턴 ↔ DevOps 가드레일

| 1차 실패 | MSA에서 증폭 위험 | 본 문서 가드레일 |
| --- | --- | --- |
| **시연 직전 부랴부랴 배포** (운영 환경 부재) | 6 service × 인프라 4 = 10 컴포넌트 동시 배포 → 폭증 | § 3 GHA 5단계 + § 5 Helm Chart + § 6 매주 정기 배포 W2부터 |
| **DB 변경 손으로** | service 4개의 DB 변경 충돌 | § 6.3 Flyway 강제 + 직접 ALTER 금지 |
| **롤백 절차 없음** | 망가진 release 그대로 시연 | § 7 Helm rollback `--atomic` + revision history |
| **로그 없이 디버깅** | 6 service 로그 흩어짐 | § 8.2 Loki + Promtail 라벨링 |
| **메트릭 없이 운영** | 어느 service가 느린지 모름 | § 8.3 Prometheus + alert 11개 룰 |
| **trace 없이 분산 디버깅** | 6 service 호출 흐름 불투명 | § 8.4 Jaeger + W3C Trace Context |
| (신규) **이미지 mutable tag 운영** | rollback 시 이전 이미지 재현 불가 | § 4.2 git_sha tag 표준 |
| (신규) **시크릿 GitHub Secrets에 적재** | runner 침해 시 모든 시크릿 노출 | § 3.5 K8s Secret만 (05번 § 5.4 정합) |
| (신규) **머지 게이트 우회** | lint·test 안 거친 코드 운영 | § 3.4 Branch Protection + Reviewer 1명 + Lead 자기 머지 금지 |
| (신규) **백업 없이 운영** | 데이터 사고 시 복구 불가 | § 9 일 1회 mysqldump CronJob |
| (신규) **사고 대응 절차 부재** | 사고 시 강태오만 우왕좌왕 | § 10 9개 시나리오 runbook + § 11 통신 채널 |
| (신규) **post-mortem 없음** | 같은 사고 반복 | § 11.3 24h 안에 Notion 보고서 |

---

## 13. W1 Lock-in DevOps 체크리스트

### 13.1 W0 (5/15까지) — 강태오 사전 작업

- [ ] `.github/workflows/ci.yml` 실제 본문 작성 (lint·test·build·image·deploy-dev 5단계)
- [ ] `.github/workflows/security.yml` 작성 (gitleaks + Dependency-Check — 05번 § 5.3.3)
- [ ] GitHub Branch Protection (develop, main) 설정 — 머지 게이트 8가지
- [ ] GitHub Secrets 적재 (`KUBECONFIG_DEV`, `SLACK_WEBHOOK_*`)
- [ ] Minikube 가동 (4 CPU, 6Gi RAM 이상) — 03번 § 9.2
- [ ] Minikube 첫 부팅 + `kubectl create ns qtai` + `kubectl create ns observability`
- [ ] K8s Secret `qtai-secrets` 적재 (jwt-keys, mysql-password, anthropic-api-key, google-oauth-client-id) — 05번 § 5.4

### 13.2 W1 (5/22 금까지) — 6 service hello-world 배포

- [ ] 6 service Dockerfile 표준 (§ 4.1) 동일 패턴 적용
- [ ] `helm/qtai-umbrella/Chart.yaml` 본격 작성 (subchart 6개 또는 단일 chart 6 deployment)
- [ ] `helm/qtai-umbrella/values.yaml` + `values-dev.yaml` 작성
- [ ] `helm/qtai-umbrella/templates/` 디렉토리에 6 service deployment + service + networkpolicy yaml
- [ ] `helm/qtai-infra/` MySQL StatefulSet + Redis-Cache + Redis-WS + Kafka KRaft + Schema Registry + ChromaDB
- [ ] Flyway migration `V1__init.sql` 4 schema (auth, bible, ai, journal) — 02번 § 8.5
- [ ] 6 service `/actuator/health` 통과 + Helm 첫 배포 성공
- [ ] Loki + Promtail + Prometheus + Grafana + Jaeger + OTel Collector 가동
- [ ] 4개 Grafana 대시보드 가동 (§ 8.5)
- [ ] alert rule 11개 적용 (§ 8.3.2)
- [ ] CronJob mysql-backup 가동 (§ 9.2)

### 13.3 W2~W5 매주 점검

- [ ] 매주 금 17:00 회고: 이번주 배포 횟수·실패 횟수·rollback 횟수
- [ ] alert 발생 빈도 검토 (false positive는 룰 조정)
- [ ] CI/CD 평균 시간 추이 (test 단계 비대 시 분리 검토)
- [ ] 의존성 신규 CVE 발견 검토 (Dependency-Check 결과)
- [ ] Helm release history 정리 (10개 초과 시 prune)

### 13.4 시연 직전 (6/15~6/17)

- [ ] freeze 시작 — Slack #qtai-deploy 공지
- [ ] demo 환경에 `main` 머지 + 수동 배포
- [ ] smoke test 6 service 전체
- [ ] 4 대시보드 가동 확인
- [ ] alert silence 설정 (시연 1h 전부터 — false alert로 시연 방해 방지)
- [ ] 백업 마지막 1회 수동 트리거 + 복구 dry-run 검증
- [ ] 강태오 단말기·노트북·전원·인터넷 백업 점검

---

## 📋 운영 매뉴얼 핵심 요약

**1차(HMS) 실패 — 운영 환경 부재 — 본질 차단:**
- § 3 GHA 5단계 + § 6 매주 정기 배포 W2부터 (시연 직전 X)
- § 7 Helm `--atomic` 자동 rollback
- § 8 관측성 stack 6 service 가시화
- § 9 일 1회 백업 + 복구 시나리오
- § 10 9개 사고 시나리오 runbook

**MSA 신규 운영 위협 11가지 가드레일:**
1. 이미지 mutable tag → § 4.2 git_sha
2. 시크릿 GHA에 적재 → § 3.5 K8s Secret만
3. 머지 게이트 우회 → § 3.4 Branch Protection 8가지
4. 백업 없음 → § 9 CronJob
5. 사고 대응 부재 → § 10 9개 runbook + § 11 채널
6. post-mortem 없음 → § 11.3 템플릿
7. DB 변경 손으로 → § 6.3 Flyway 강제
8. 로그 흩어짐 → § 8.2 Loki + 라벨
9. 메트릭 없음 → § 8.3 Prometheus + 11 alert
10. trace 없음 → § 8.4 Jaeger + W3C
11. namespace 격리 없음 → § 2.3 + 05번 § 6.1 NetworkPolicy

**Foundation Lock-in 운영 산출물 (W1 5/22):**
- `.github/workflows/ci.yml` (5단계)
- `.github/workflows/security.yml` (gitleaks + Dependency-Check)
- `helm/qtai-umbrella/` (6 service deployment + service + networkpolicy)
- `helm/qtai-infra/` (MySQL + Redis + Kafka + Schema Registry + ChromaDB + 관측성 stack)
- 4 Grafana 대시보드
- 11 Prometheus alert rule
- mysql-backup CronJob
- 9 시나리오 incident runbook (본 § 10)

---

> **다음 작성 문서 후보:** `07_테스트_전략` (단위·통합·E2E·부하) · `08_프론트엔드_가이드` (Flutter 표준) · `09_AI_프롬프트_운영` (강상민 owner — 신학 가드레일 · A/B testing · 환각 회귀)
