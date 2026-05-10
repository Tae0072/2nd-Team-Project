��� QT-AI (큐티 AI 앱) — 트러블슈팅 FAQ v1.0

> **문서 버전:** v1.0
> **작성일:** 2026-05-08
> **연관 문서:** [01_프로젝트_계획서 v1.4](./01_프로젝트_계획서.md) / [03_아키텍처_정의서 v1.3](./03_아키텍처_정의서.md) / [04_API_명세서 v1.5](./04_API_명세서.md) / [05_보안_명세서 v1.0](./05_보안_명세서.md) / [06_DevOps_운영_매뉴얼 v1.0](./06_DevOps_운영_매뉴얼.md) / [08_프론트엔드_Flutter_가이드 v1.0](./08_프론트엔드_Flutter_가이드.md) / [09_AI_프롬프트_운영_가이드 v1.0](./09_AI_프롬프트_운영_가이드.md)
> **owner:** 강태오 (Lead — 문서 작성 + 관리)
> **용도 키워드:** 디버깅 · 오류 해결 · CrashLoop · 401 · 502 · SSE buffering · Kafka lag · ChromaDB · Flutter DIO · Riverpod · Minikube · Gradle multi-module · MySQL migration · Redis · Loki · Jaeger
> **목적:** 6명 팀이 W1~W5 개발하면서 가장 자주 막히는 지점을 한 곳에 모아 평균 해결 시간을 최소화. 1차(HMS) 반복 실수 + 2차(QT-AI) MSA 도메인별 빠른 진단법 박제. **막혔을 때 이 문서를 먼저 보고 10분 안에 해결 안 되면 Lead(강태오)에게 ping.**

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-08 | 강태오 (Lead) | 초기 작성 — 16 sections — Gateway/BFF·Auth·AI·Journal·Bible·Flutter·Gradle·K8s·MySQL·Redis·Kafka·CI/CD·관측성·1차 사고 통합 매트릭스·W1 체크리스트 |

---

## 목차

1. [개요·진단 원칙·빠른 분류](#1-개요진단-원칙빠른-분류)
2. [빠른 진단 명령어 모음](#2-빠른-진단-명령어-모음)
3. [Gateway·BFF — 407·502·CORS·SSE buffering](#3-gatewaybff--407502corsse-buffering)
4. [Auth Service — JWT·401·Refresh·Google OAuth](#4-auth-service--jwt401refreshgoogle-oauth)
5. [AI Service — LLM timeout·환각·ChromaDB·인젝션](#5-ai-service--llm-timeout환각chromadb인젝션)
6. [Journal Service — Kafka·Saga·이벤트 순서](#6-journal-service--kafkasaga이벤트-순서)
7. [Bible Service — 성경 데이터·verse_exists·API](#7-bible-service--성경-데이터verse_existsapi)
8. [Flutter 클라이언트 — Riverpod·DIO·SSE·STOMP](#8-flutter-클라이언트--riverpoddiossestomp)
9. [Gradle 빌드 — 6 module·Kotlin DSL·의존성](#9-gradle-빌드--6-modulekotlin-dsl의존성)
10. [Docker·Kubernetes (Minikube) — Pod·Service·PVC](#10-dockerkubernetes-minikube--podservicepvc)
11. [MySQL·Flyway — 연결·마이그레이션·schema](#11-mysqlflyway--연결마이그레이션schema)
12. [Redis·캐시 — 연결·TTL·Distributed Lock](#12-redis캐시--연결ttldistributed-lock)
13. [Kafka — 토픽·컨슈머 lag·멱등성·Saga 보상](#13-kafka--토픽컨슈머-lag멱등성saga-보상)
14. [CI/CD — GitHub Actions·Spectral·OpenAPI·빌드 실패](#14-cicd--github-actionsspectropenapibild-실패)
15. [관측성 — Grafana·Prometheus·Jaeger·Loki](#15-관측성--grafanaprometheustempeloki)
16. [1차(HMS) 사고 통합 매트릭스 + W1 막힘 가이드](#16-1차hms-사고-통합-매트릭스--w1-막힘-가이드)

---

## 1. 개요·진단 원칙·빠른 분류

### 1.1 이 문서를 사용하는 방법

1. **증상**으로 섹션 찾기 — 각 섹션 제목에 HTTP 코드·증상 키워드 박제
2. **10분 룰** — 해당 섹션 체크리스트 보고 10분 안에 해결 안 되면 즉시 Lead(강태오) ping
3. **해결 후 기록** — 새 패턴 발견 시 해당 섹션 끝에 "추가 케이스" 형태로 PR (Reviewer: 강태오)
4. **W1 막힘** — § 16에 W1 체크리스트 아이템별 막힘 대응 수록

### 1.2 빠른 분류표 (증상 → 섹션)

| 증상 | 섹션 |
| --- | --- |
| 502 Bad Gateway / 503 | § 3.1 |
| 404 Not Found (API endpoint) | § 3.2 |
| CORS error (preflight) | § 3.3 |
| SSE stream이 바로 끊김 / buffering | § 3.4 |
| 401 Unauthorized | § 4.1 |
| Refresh Token 갱신 무한 루프 | § 4.2 |
| Google OAuth 실패 | § 4.3 |
| LLM timeout / 응답 없음 | § 5.1 |
| ChromaDB 연결 실패 | § 5.2 |
| AI 응답 품질 갑자기 떨어짐 | § 5.3 |
| 프롬프트 인젝션 차단 오작동 | § 5.4 |
| Kafka 메시지 미수신 | § 13.1 |
| Journal 자동 생성 안 됨 | § 6.1 |
| Saga 보상 트랜잭션 미실행 | § 6.2 |
| `verse_exists` API 틀린 결과 | § 7.1 |
| Flutter DIO 401 반복 | § 8.1 |
| Riverpod Provider cycle / crash | § 8.2 |
| SSE 첫 토큰 안 옴 | § 8.3 |
| STOMP 연결 끊김 | § 8.4 |
| Gradle build 실패 | § 9.1 |
| Pod CrashLoopBackOff | § 10.1 |
| Pod Pending / ImagePullBackOff | § 10.2 |
| MySQL 연결 실패 | § 11.1 |
| Flyway migration 실패 | § 11.2 |
| Redis 연결 / 분산락 실패 | § 12.1 |
| Kafka consumer group lag | § 13.2 |
| GitHub Actions 빌드 실패 | § 14.1 |
| Spectral lint 실패 | § 14.2 |
| Grafana 대시보드 데이터 없음 | § 15.1 |
| Jaeger trace 없음 | § 15.2 |

### 1.3 진단 원칙 5가지

| # | 원칙 | 의미 |
| --- | --- | --- |
| 1 | **로그 먼저** | 증상 재현 전에 `kubectl logs -f pod/...` 또는 Loki 켜고 시작 |
| 2 | **한 번에 하나** | 두 가지 동시에 변경 X — 무엇이 고쳤는지 모름 |
| 3 | **환경 변수 확인** | 70% 문제는 잘못된 env 변수 (URL·포트·시크릿). 먼저 `kubectl describe pod` |
| 4 | **1차 사고 먼저 의심** | § 16 매트릭스 — 1차에서 반복된 패턴이 2차에서도 나타날 가능성 높음 |
| 5 | **혼자 30분 이상 X** | 30분 넘으면 Lead에게 화면 공유 요청. 시간 낭비가 가장 큰 리스크 |

---

## 2. 빠른 진단 명령어 모음

### 2.1 K8s 상태 확인 (Minikube)

```bash
# 전체 pod 상태
kubectl get pods -n qtai --watch

# 특정 pod 로그 실시간
kubectl logs -f deployment/auth-service -n qtai

# pod 상세 (이벤트·env·volume 확인)
kubectl describe pod <pod-name> -n qtai

# ConfigMap / Secret 목록
kubectl get configmap -n qtai
kubectl get secret -n qtai

# Service endpoint 확인
kubectl get svc -n qtai
kubectl describe svc gateway -n qtai

# Minikube service URL 확인
minikube service gateway -n qtai --url

# 최근 이벤트 (전체)
kubectl get events -n qtai --sort-by='.lastTimestamp' | tail -20
```

### 2.2 DB 빠른 접속

```bash
# MySQL (auth-db 예시)
kubectl exec -it deployment/auth-db -n qtai -- psql -U qtai_user -d auth_db
# 테이블 목록: \dt
# 연결 수: SELECT count(*) FROM pg_stat_activity;

# Redis
kubectl exec -it deployment/redis -n qtai -- redis-cli ping
# KEYS *
# TTL <key>
```

### 2.3 Kafka 빠른 점검

```bash
# 토픽 목록
kubectl exec -it deployment/kafka -n qtai -- kafka-topics.sh --bootstrap-server localhost:9092 --list

# consumer group lag
kubectl exec -it deployment/kafka -n qtai -- kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 --group qtai-journal-group --describe

# 특정 토픽 최근 메시지 (마지막 5개)
kubectl exec -it deployment/kafka -n qtai -- kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic ai.session.completed \
  --from-beginning --max-messages 5
```

### 2.4 AI Service / ChromaDB 점검

```bash
# ChromaDB health
kubectl exec -it deployment/ai-service -n qtai -- curl http://chromadb:8000/api/v1/heartbeat

# 임베딩 모델 로드 확인 (ai-service pod 내 Python)
kubectl exec -it deployment/ai-service -n qtai -- python3 -c "
from sentence_transformers import SentenceTransformer
m = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
print('OK:', m.encode('test').shape)
"

# Anthropic API key 유효성 (비용 없음)
kubectl exec -it deployment/ai-service -n qtai -- curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" -H "anthropic-version: 2023-06-01"
```

### 2.5 Flutter / 개발 환경

```bash
# SDK 버전 확인
flutter --version
dart --version

# 의존성 트리 확인
flutter pub deps

# analyze 실행
flutter analyze

# 테스트 실행
flutter test

# 특정 test 파일
flutter test test/auth/auth_interceptor_test.dart

# 빌드 (Android dev flavor)
flutter build apk --flavor dev --debug
```

### 2.6 Gradle multi-module 점검

```bash
# 전체 빌드
./gradlew build

# 특정 모듈 빌드
./gradlew :auth-service:build

# 의존성 트리
./gradlew :auth-service:dependencies

# 테스트만
./gradlew :auth-service:test

# bootRun (dev 프로파일)
./gradlew :gateway:bootRun --args='--spring.profiles.active=dev'
```

---

## 3. Gateway·BFF — 407·502·CORS·SSE buffering

### 3.1 502 Bad Gateway

**증상:** `502 Bad Gateway` — Flutter 또는 curl에서 Gateway 응답.

**원인 트리:**

```
Gateway → 백엔드 서비스 pod 도달 불가
  ├─ 1. 백엔드 pod 자체가 죽음 (CrashLoop)
  ├─ 2. K8s Service selector 불일치 (label mismatch)
  ├─ 3. 포트 불일치 (Service targetPort vs containerPort)
  ├─ 4. NetworkPolicy deny (default deny 정책)
  └─ 5. Readiness probe 실패 → pod Terminating 중
```

**진단 체크리스트:**

```bash
# 1. 백엔드 pod 상태
kubectl get pods -n qtai | grep auth-service

# 2. Service endpoint 확인 (NONE이면 selector 불일치)
kubectl get endpoints auth-service -n qtai

# 3. Pod 로그 마지막 50줄
kubectl logs deployment/auth-service -n qtai --tail=50

# 4. Gateway 로그 확인 (라우팅 오류)
kubectl logs deployment/gateway -n qtai --tail=50 | grep -i error

# 5. NetworkPolicy 확인
kubectl get networkpolicy -n qtai
```

**빠른 확인 — Service selector:**
```yaml
# K8s Service (auth-service.yaml)
spec:
  selector:
    app: auth-service  # ← Pod의 label과 정확히 일치?

# Pod (Deployment.yaml)
spec:
  template:
    metadata:
      labels:
        app: auth-service  # ← 위와 일치해야
```

**1차 사고 매핑:** 1차 HMS에서 컨테이너 포트 설정 오타 → 연결 실패. `containerPort: 8080` vs `targetPort: 8081` 불일치.

### 3.2 404 Not Found (API endpoint)

**증상:** Flutter에서 특정 API endpoint 404.

**체크:**

1. **Gateway 라우팅 규칙 확인** — `application.yml`의 `spring.cloud.gateway.routes[*].predicates`
2. **Path prefix strip** — `StripPrefix=2`가 있으면 `/api/v1/auth/login` → `/auth/login` 으로 도달. 백엔드 서비스의 `@RequestMapping`이 `/auth/login`인지 확인
3. **서비스 이름** — `lb://auth-service` 의 `auth-service`가 K8s Service 이름과 일치?
4. **method 불일치** — GET으로 호출했는데 POST endpoint

```bash
# Gateway 라우팅 actuator로 확인
kubectl exec -it deployment/gateway -n qtai -- \
  curl http://localhost:8080/actuator/gateway/routes | python3 -m json.tool
```

### 3.3 CORS error (preflight)

**증상:** Flutter Web 또는 개발 중 `Access-Control-Allow-Origin` 헤더 없음.

**v1.0 Flutter 앱은 CORS 불필요** (네이티브 앱은 same-origin 정책 적용 안 됨). Swagger UI 또는 개발 브라우저 테스트 시만 발생.

**Gateway CORS 설정 확인:**
```yaml
spring:
  cloud:
    gateway:
      globalcors:
        cors-configurations:
          '[/**]':
            allowedOrigins:
              - "http://localhost:*"
              - "http://10.0.2.2:*"
            allowedMethods: ["GET","POST","PUT","PATCH","DELETE","OPTIONS"]
            allowedHeaders: ["*"]
            allowCredentials: true
            maxAge: 3600
```

**⚠️ allowCredentials: true 이면 allowedOrigins에 `*` 금지.** 구체적 origin 명시.

### 3.4 SSE stream 즉시 끊김 / buffering

**증상:** AI 큐티 turn 호출 시 첫 token 오지 않고 오래 대기하다가 한 번에 응답, 또는 즉시 연결 끊김.

**원인 1: Gateway buffering**
Gateway가 SSE response를 버퍼링해서 모아뒀다가 보냄. 08번 § 9.3 정합.

**해결 — Gateway에 NoBuffering filter 적용:**
```yaml
# gateway/src/main/resources/application.yml
spring:
  cloud:
    gateway:
      routes:
        - id: ai-service-sse
          uri: lb://ai-service
          predicates:
            - Path=/api/v1/ai/sessions/*/turns
            - Method=POST
          filters:
            - StripPrefix=2
            - RemoveResponseHeader=Transfer-Encoding
            - name: SetResponseHeader
              args:
                name: X-Accel-Buffering
                value: "no"
```

또는 커스텀 `NoBufferingGatewayFilter`:
```java
@Component
public class NoBufferingGatewayFilter implements GatewayFilterFactory<Object> {
    @Override
    public GatewayFilter apply(Object config) {
        return (exchange, chain) -> {
            if (exchange.getRequest().getHeaders()
                    .getAccept().stream()
                    .anyMatch(mt -> mt.includes(MediaType.TEXT_EVENT_STREAM))) {
                exchange.getResponse().getHeaders()
                    .set("X-Accel-Buffering", "no");
            }
            return chain.filter(exchange);
        };
    }
}
```

**원인 2: Flutter DIO receiveTimeout**
기본 30초 timeout이 SSE 연결에 적용돼 30초 후 끊김. 08번 § 6.1 + § 8.2 정합.

```dart
// SSE 전용 Dio options
options: Options(
  responseType: ResponseType.stream,
  receiveTimeout: const Duration(minutes: 5),  // SSE는 기본 30s 초과
  headers: {'Accept': 'text/event-stream'},
)
```

**원인 3: Nginx / Ingress 버퍼링**
Minikube ingress가 response 버퍼링. ingress annotation 추가:
```yaml
nginx.ingress.kubernetes.io/proxy-buffering: "off"
nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
```

### 3.5 BFF Aggregator — STOMP CONNECT 실패

**증상:** Flutter STOMP 연결 후 CONNECTED 프레임 안 옴 또는 ERROR 프레임.

**체크:**
1. BFF WebSocket endpoint URL: `wss://qtai.local/api/v1/ws/notifications` — Gateway에서 패스스루 여부 (§ 3.4와 동일 — SSE filter 우회 설정 확인)
2. STOMP CONNECT 헤더에 `Authorization: Bearer <accessToken>` 있는지
3. BFF가 JWT 검증 후 user_id를 STOMP 세션에 저장하는지 (04번 § 10.2)

```bash
# BFF STOMP 로그 확인 (CONNECT/CONNECTED/ERROR 프레임)
kubectl logs deployment/bff -n qtai --tail=100 | grep -i stomp
```

---

## 4. Auth Service — JWT·401·Refresh·Google OAuth

### 4.1 401 Unauthorized

**증상:** API 호출 시 401 응답. Flutter에서 자동 Refresh 후 재시도해도 401.

**진단 트리:**

```
401 응답
  ├─ 1. Access Token 만료 → Flutter가 Refresh 시도
  │      └─ Refresh Token도 만료·폐기 → 로그아웃 필요
  ├─ 2. 잘못된 JWT 서명 (RS256 key mismatch)
  ├─ 3. JWT audience/issuer 불일치
  ├─ 4. Refresh Distributed Lock 경쟁 (race condition)
  └─ 5. Gateway가 user_id 헤더 안 전달 (service가 user_id 못 읽음)
```

**빠른 확인:**
```bash
# Auth Service 로그 — JWT 검증 오류 grep
kubectl logs deployment/auth-service -n qtai --tail=100 | grep -i "jwt\|token\|401\|unauthorized"

# JWT 디버깅 (jwt.io에서 payload 확인 or curl)
# Access Token decode (payload 부분)
echo "<JWT>" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool
```

**Refresh Token 만료 여부 확인:**
```sql
-- REFRESH_TOKENS 테이블에서 확인
SELECT user_id, expires_at, revoked_at, is_used
FROM REFRESH_TOKENS
WHERE user_id = :userId
ORDER BY created_at DESC LIMIT 5;
```

**Gateway user_id 헤더 확인:**
```yaml
# Gateway filter — Auth 검증 후 X-User-Id 헤더 주입 (04번 § 4)
filters:
  - name: AuthFilter
    # AuthFilter는 JWT 검증 후 X-User-Id, X-User-Role 헤더를 downstream에 추가
```
서비스에서 `@RequestHeader("X-User-Id")` 로 받는지 확인.

### 4.2 Refresh Token 갱신 무한 루프

**증상:** Flutter 앱이 401 → refresh → 401 → refresh를 반복. 화면 멈춤.

**원인:** `AuthInterceptor`의 `_retried` extra flag 누락 또는 `QueuedInterceptor` 미사용.

**08번 § 6.4 패턴 확인:**
```dart
// ⚠️ _retried flag 없으면 재귀 무한 루프
options: Options(
  extra: {'_retried': true},  // refresh 요청에 이 flag 필수
)

// onError에서 검사
if (err.requestOptions.extra['_retried'] == true) {
  return handler.next(err);  // 재시도 X
}
```

**단일 flight 확인** — `Completer` 또는 `synchronized` 없으면 동시 401 → 여러 refresh 호출:
```dart
// 이미 refresh 진행 중이면 동일 Completer 대기
if (_refreshCompleter != null) {
  return _refreshCompleter!.future;
}
```

**백엔드 원인** — Refresh Token Rotation (05번 § 3.2): Refresh 사용 즉시 폐기 + 새 Refresh 발급. 동시 요청 2개가 같은 Refresh Token 사용하면 두 번째는 폐기됨 → 401.

```bash
# DB에서 폐기된 Refresh Token 확인
kubectl exec -it deployment/auth-db -n qtai -- psql -U qtai_user -d auth_db \
  -c "SELECT id, user_id, revoked_at, revoke_reason FROM REFRESH_TOKENS WHERE revoke_reason = 'REUSE_DETECTED' ORDER BY revoked_at DESC LIMIT 10;"
```

### 4.3 Google OAuth 실패

**증상:** Google 로그인 후 앱에서 오류. "ID Token missing" 또는 "Invalid ID Token".

**체크:**

| 단계 | 확인 사항 |
| --- | --- |
| Flutter | `GoogleSignIn(serverClientId: ...)` 의 `serverClientId`가 Google Console의 Web Application Client ID인지 |
| Flutter | `account.authentication`의 `idToken`이 null인지 (일부 구형 기기 발생) |
| Auth Service | `/auth/oauth/google` 에서 Google JWK 검증 (04번 § 4.8) — `https://www.googleapis.com/oauth2/v3/certs` 접근 가능한지 |
| K8s | ai-service pod에서 `curl https://www.googleapis.com/oauth2/v3/certs` 응답 오는지 (NetworkPolicy 외부 허용 여부) |
| Google Console | Authorized redirect URI에 `http://10.0.2.2:*` (dev) 추가 여부 |

```bash
# Auth Service에서 Google JWK 접근 확인
kubectl exec -it deployment/auth-service -n qtai -- curl -v \
  "https://www.googleapis.com/oauth2/v3/certs"
```

**idToken null 해결:**
```dart
final auth = await account.authentication;
if (auth.idToken == null) {
  // serverClientId 설정이 잘못됐거나 기기 호환성 문제
  await _googleSignIn.signOut();  // 완전 재로그인 시도
  throw const OAuthIdTokenMissingException();
}
```

---

## 5. AI Service — LLM timeout·환각·ChromaDB·인젝션

### 5.1 LLM timeout / 응답 없음

**증상:** SSE turn 요청 후 `LLM_TIMEOUT` error event 또는 무반응.

**체크 순서:**

```bash
# 1. AI Service pod 상태
kubectl get pod -n qtai | grep ai-service

# 2. Anthropic API key 유효성 (실제 모델 목록 호출)
kubectl exec -it deployment/ai-service -n qtai -- \
  curl https://api.anthropic.com/v1/models \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01"

# 3. Anthropic API status 확인 (외부)
# https://status.anthropic.com 접속

# 4. AI Service 로그 — timeout / rate limit grep
kubectl logs deployment/ai-service -n qtai --tail=100 | \
  grep -i "timeout\|rate_limit\|429\|503"
```

**timeout 값 확인** (09번 § 3.4):
- AI Service → Anthropic: 4분
- Gateway → AI Service: 5분
- Flutter → Gateway: 5분

Flutter 쪽이 5분 미만이면 Flutter가 먼저 끊음:
```dart
receiveTimeout: const Duration(minutes: 5)  // SSE DIO options
```

**Anthropic 429 (rate limit):**
```bash
# 현재 사용 중인 동시 호출 수 확인
kubectl exec -it deployment/ai-service -n qtai -- \
  curl http://localhost:8080/actuator/metrics/ai.concurrent.calls.active
```

동시 10개 semaphore 한도 (09번 § 10.4) — 시연 중 초과 시 한도 상향 검토.

### 5.2 ChromaDB 연결 실패

**증상:** AI Service 로그에 `ChromaDB connection refused` 또는 `Collection not found`.

```bash
# ChromaDB pod 상태
kubectl get pod -n qtai | grep chromadb

# ChromaDB health check
kubectl exec -it deployment/ai-service -n qtai -- \
  curl http://chromadb:8000/api/v1/heartbeat

# Collection 존재 여부
kubectl exec -it deployment/ai-service -n qtai -- python3 - <<'EOF'
import chromadb
c = chromadb.HttpClient(host='chromadb', port=8000)
print(c.list_collections())
EOF

# PVC 마운트 확인 (데이터 유실 방지)
kubectl get pvc -n qtai | grep chromadb
kubectl describe pvc chromadb-pvc -n qtai
```

**Collection 없는 경우 — 시드 재실행:**
```bash
kubectl exec -it deployment/ai-service -n qtai -- \
  python3 scripts/rag_index.py --seed-only
```

**임베딩 모델 미로드 — 처음 시작 시 수 분 소요 (다운로드):**
```bash
kubectl logs deployment/ai-service -n qtai | grep -i "model\|embedding\|loading"
# "Loading model..." → 정상 로딩 중. 완료까지 대기
```

### 5.3 AI 응답 품질 갑자기 떨어짐 (드리프트)

**증상:** golden-set 회귀 실패 / 사용자 불만.

**진단:**
```bash
# nightly 회귀 결과 확인 (GitHub Actions)
# .github/workflows/ci.yml의 eval job 로그

# 수동 회귀 실행
kubectl exec -it deployment/ai-service -n qtai -- \
  python3 tests/eval/run_eval.py --set golden --verbose
```

**원인 + 해결:**

| 원인 | 해결 |
| --- | --- |
| Anthropic 모델 silently 업데이트 | `claude-sonnet-4-5` 버전 고정 확인 (09번 § 3.1) |
| 시스템 프롬프트 변경 (누군가 PR merge) | git log `prompts/` — 마지막 변경자 확인 + ADR 있는지 |
| RAG 시드 변경 (문서 재인덱싱) | ChromaDB collection version 확인 |
| temperature 파라미터 변경 | 09번 § 3.2 기준값 대비 확인 |

### 5.4 프롬프트 인젝션 차단 오작동

**증상:** 정상 입력이 인젝션으로 차단됨 (false positive) 또는 인젝션이 통과됨 (false negative).

**false positive — 정상 입력 차단:**
```bash
# injection_patterns_v1.yaml에서 오매칭 패턴 확인
kubectl exec -it deployment/ai-service -n qtai -- \
  cat src/main/resources/safety/injection_patterns_v1.yaml

# 로그에서 차단 사유 확인
kubectl logs deployment/ai-service -n qtai | grep "PROMPT_INJECTION_DETECTED" | tail -10
```

정규식이 너무 광범위한 경우 → 패턴 수정 + injection-set 30건 회귀 확인 후 PR.

**false negative — 인젝션 통과:**
injection-set에 새 case 추가 + 패턴 강화 → PR (Reviewer: 강태오 + 이지윤).

---

## 6. Journal Service — Kafka·Saga·이벤트 순서

### 6.1 Journal 자동 생성 안 됨

**증상:** AI 큐티 세션 완료 후 "묵상 노트가 자동으로 생성되었습니다" 알림 미수신 + Journal 없음.

**진단 체인:**

```
AI Service → Kafka 토픽 ai.session.completed 발행
  → Journal Service consume
  → JOURNAL INSERT
  → Kafka 토픽 notification.requested 발행
    → BFF Aggregator consume
    → STOMP MESSAGE 발행
      → Flutter 알림 표시
```

각 단계 확인:

```bash
# 1. ai.session.completed 토픽에 메시지 있는지
kubectl exec -it deployment/kafka -n qtai -- kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic ai.session.completed \
  --from-beginning --max-messages 5

# 2. Journal Service consumer lag
kubectl exec -it deployment/kafka -n qtai -- kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 --group qtai-journal-group --describe

# 3. Journal Service 로그
kubectl logs deployment/journal-service -n qtai --tail=50 | grep -i "journal\|error\|kafka"

# 4. notification.requested 토픽 확인
kubectl exec -it deployment/kafka -n qtai -- kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic notification.requested \
  --from-beginning --max-messages 5
```

**AI_SESSIONS 상태 확인:**
```sql
-- ai-service DB에서 세션 상태
SELECT id, user_id, status, current_step, updated_at
FROM AI_SESSIONS
WHERE status = 'COMPLETED'
ORDER BY updated_at DESC LIMIT 10;
```

`COMPLETED`인데 Kafka 메시지 없으면 → AI Service가 발행 실패. `AFTER_COMMIT` publish 타이밍 확인 (03번 § 2.3).

### 6.2 Saga 보상 트랜잭션 미실행

**증상:** Journal 생성 실패 시 AI 세션 상태가 `COMPLETED`로 남음 (사용자에게 오류 미전달).

**보상 흐름 확인 (03번 § 2.6):**

```
journal.creation.failed 토픽 발행
  → AI Service consume
  → AI_SESSIONS.status = JOURNAL_CREATION_FAILED
  → BFF → Flutter STOMP: "자동 생성에 실패했습니다"
```

```bash
# journal.creation.failed 토픽 확인
kubectl exec -it deployment/kafka -n qtai -- kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 --topic journal.creation.failed \
  --from-beginning --max-messages 5

# AI Service가 보상 메시지 consume하는지 확인
kubectl logs deployment/ai-service -n qtai | grep "journal.creation.failed"
```

**보상 배치 (v1.0):** 매일 24:00에 `JOURNAL_CREATION_FAILED` 상태 세션 재시도 배치. 배치 로그 확인:
```bash
kubectl logs deployment/ai-service -n qtai | grep "compensation batch"
```

### 6.3 이벤트 순서 역전 (Event Sourcing)

**증상:** Journal 수정 이벤트가 생성보다 먼저 처리됨 → 정합성 깨짐.

**확인:**
```sql
-- JOURNAL_EVENTS 테이블에서 순서 확인
SELECT journal_id, event_type, sequence_number, occurred_at
FROM JOURNAL_EVENTS
WHERE journal_id = :journalId
ORDER BY sequence_number;
```

`sequence_number`가 비어있거나 순서 역전된 경우 → 03번 § 2.5 + 04번 § 8.4의 순서 보장 로직 확인. Kafka 파티션 키가 `journal_id`인지 확인 (동일 파티션 = 순서 보장).

```bash
# 토픽 파티션 수 + 키 확인
kubectl exec -it deployment/kafka -n qtai -- kafka-topics.sh \
  --bootstrap-server localhost:9092 --topic journal.updated --describe
# Partition count = 3, partition key = journal_id → 동일 journal은 같은 partition
```

---

## 7. Bible Service — 성경 데이터·verse_exists·API

### 7.1 `verse_exists` API 틀린 결과

**증상:** 실재하는 성경 구절인데 `false` 반환, 또는 없는 구절인데 `true`.

**확인:**
```bash
# Bible Service 직접 호출
kubectl exec -it deployment/bible-service -n qtai -- \
  curl "http://localhost:8080/api/v1/bible/books/GEN/chapters/1/verses/1/exists"
# 예상: true

# 존재하지 않는 구절
kubectl exec -it deployment/bible-service -n qtai -- \
  curl "http://localhost:8080/api/v1/bible/books/JHN/chapters/22/verses/1/exists"
# 예상: false (요한복음은 21장까지)
```

**BOOKS / KR_BIBLE 테이블 확인:**
```sql
-- book_code 화이트리스트 확인
SELECT code, kr_name, total_chapters FROM BOOKS ORDER BY testament, book_order;

-- 요한복음 최대 장 확인
SELECT MAX(chapter) FROM KR_BIBLE WHERE book_code = 'JHN';  -- 21 이어야

-- 특정 구절 존재 여부
SELECT COUNT(*) FROM KR_BIBLE WHERE book_code = 'GEN' AND chapter = 1 AND verse = 1;
```

**데이터 미시드:**
```bash
# Bible Service DB 데이터 수 확인
kubectl exec -it deployment/bible-db -n qtai -- psql -U qtai_user -d bible_db \
  -c "SELECT COUNT(*) FROM KR_BIBLE;"
# 예상: 31,102 (개역개정 전체 절 수)
# 0이면 시드 migration 미실행 → Flyway migration 재실행
```

### 7.2 성경 본문 API 느림

**증상:** `/api/v1/bible/books/{bookCode}/chapters/{chapter}/verses/{verse}` 응답 1초+.

**인덱스 확인:**
```sql
-- KR_BIBLE 인덱스 (book_code + chapter + verse 복합 인덱스)
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'kr_bible';
-- idx_kr_bible_bcv (book_code, chapter, verse) 인덱스 있어야

-- 없으면 추가
CREATE INDEX CONCURRENTLY idx_kr_bible_bcv ON KR_BIBLE(book_code, chapter, verse);
```

**캐시 미적용:**
```bash
# Redis에 성경 구절 캐시 있는지
kubectl exec -it deployment/redis -n qtai -- redis-cli KEYS "bible:*" | head -10
# 없으면 Bible Service의 @Cacheable 어노테이션 확인
```

---

## 8. Flutter 클라이언트 — Riverpod·DIO·SSE·STOMP

### 8.1 DIO 401 반복 (Refresh 실패)

**증상:** 앱 실행 시 또는 API 호출마다 401 → 로그인 화면으로 계속 이동.

```dart
// AuthInterceptor 디버그 출력 추가 (임시)
@override
void onError(DioException err, ErrorInterceptorHandler handler) async {
  debugPrint('[AuthInterceptor] onError: ${err.response?.statusCode} '
      'path=${err.requestOptions.path} '
      'retried=${err.requestOptions.extra['_retried']}');
  // ...
}
```

**체크리스트:**

| # | 확인 | 방법 |
| --- | --- | --- |
| 1 | Refresh Token이 secure_storage에 있는지 | `await storage.readRefreshToken()` null 아닌지 |
| 2 | Refresh API endpoint URL | `${Env.current.baseUrl}/auth/refresh` 경로 맞는지 |
| 3 | Refresh 요청에 `_retried: true` extra | 무한 루프 방지 (§ 4.2) |
| 4 | Refresh 완료 후 새 Access Token을 interceptor에 set | `setAccessToken(newAccess)` 호출 여부 |
| 5 | 백엔드 Refresh Token 폐기 여부 | § 4.2 + DB 확인 |

**secure_storage 초기화 문제 (Android):**
```dart
// AndroidOptions에 encryptedSharedPreferences: true 설정
aOptions: AndroidOptions(encryptedSharedPreferences: true)
// 처음 앱 설치 후 Keystore 초기화 시간 (~1초) 대기 필요
```

### 8.2 Riverpod Provider cycle / 앱 crash

**증상:** 앱 시작 시 `ProviderException` 또는 `StackOverflowError`.

```dart
// Provider 의존 cycle 탐지
// aProvider → bProvider → aProvider → crash

// 확인 방법: Riverpod DevTools
// flutter pub global activate flutter_devtools
// flutter pub global run flutter_devtools
```

**빠른 해결:**
```
1. 순환 의존 Provider 찾기 — IDE에서 Provider 정의 찾고 watch 체인 추적
2. 공통 상태를 별도 Provider로 분리
3. ref.watch → ref.read 변경 (콜백 안에서는 항상 read)
```

**05번 의존 그래프 표준 (`core/di/providers.dart`):**
```
tokenStorage (leaf) ← authInterceptor ← dio ← authApi ← authState
```
이 방향이 역전되면 cycle.

### 8.3 SSE 첫 token 안 옴

**증상:** AI turn 요청 후 첫 `event: token` 안 오고 오래 대기.

**단계별 확인:**

```bash
# 1. Gateway에서 AI Service까지 경로 확인
kubectl exec -it deployment/gateway -n qtai -- \
  curl -X POST http://ai-service:8080/api/v1/ai/sessions/1/turns \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"step":"A","content":"테스트"}' \
  --no-buffer -v 2>&1 | head -50
```

**Flutter DIO 설정 확인:**
```dart
// 반드시 stream 모드
Options(
  responseType: ResponseType.stream,  // ← 이게 없으면 버퍼링
  headers: {'Accept': 'text/event-stream'},
)
```

**LineSplitter 처리 확인:**
```dart
// UTF-8 decode → LineSplitter 순서 맞는지
.transform(utf8.decoder)
.transform(const LineSplitter())
```

**AI Service에서 Anthropic 호출 중인지:**
```bash
kubectl logs deployment/ai-service -n qtai -f | grep "Anthropic call"
```

### 8.4 STOMP 연결 끊김 / 재연결 반복

**증상:** 알림이 중간에 끊김. 로그에 STOMP reconnect 반복.

**재연결 backoff 확인 (08번 § 7.2):**
```dart
// exponential backoff — max 30s
// 1 → 2 → 4 → 8 → 16 → 30 → 30 ...
Duration(seconds: (1 << (_reconnectAttempt > 5 ? 5 : _reconnectAttempt)).clamp(1, 30))
```

**서버 heartbeat 확인:**
```dart
heartbeatOutgoing: const Duration(seconds: 10),
heartbeatIncoming: const Duration(seconds: 10),
```
BFF도 동일 heartbeat 설정 여부 확인 (미스매치 시 BFF가 연결 끊음).

**JWT 만료 시 STOMP 재연결:**
```dart
// _handleStompError에서 UNAUTHORIZED 감지 → AuthState 업데이트
void _handleStompError(StompFrame frame) {
  if (frame.headers['message']?.contains('UNAUTHORIZED') ?? false) {
    disconnect();
    // RiverPod AuthState가 unauthenticated로 전환 → 재로그인 → 새 Access Token
    // → NotificationLifecycle이 새 token으로 재연결
  }
}
```

### 8.5 Flutter analyze / test 실패

**증상:** CI에서 `flutter analyze` 오류 또는 `flutter test` 실패.

**빠른 fix:**
```bash
# 코드 생성 파일 재생성 (freezed·riverpod_generator·json_serializable)
flutter pub run build_runner build --delete-conflicting-outputs

# lint 자동 수정
dart fix --apply

# import 정렬
dart format lib/

# domain layer에 flutter/dio import 없는지 확인
grep -r "package:flutter\|package:dio" lib/features/*/domain/
# 결과 없어야 (§ 3.4 원칙)
```

---

## 9. Gradle 빌드 — 6 module·Kotlin DSL·의존성

### 9.1 Gradle build 실패

**증상:** `./gradlew build` 실패.

```bash
# 상세 오류 확인
./gradlew build --stacktrace 2>&1 | tail -50

# 캐시 완전 클린 후 재빌드
./gradlew clean build

# 특정 모듈만
./gradlew :auth-service:build --info
```

**빠른 확인 체크리스트:**

| # | 확인 | 명령 |
| --- | --- | --- |
| 1 | JDK 버전 | `java -version` (21 이어야) |
| 2 | Gradle 버전 | `./gradlew --version` |
| 3 | settings.gradle.kts에 모듈 포함 | `include(":auth-service", ":bible-service", ...)` |
| 4 | 모듈 간 의존성 방향 | 공통 모듈(common)만 참조, 서비스 간 직접 의존 X |
| 5 | BaseEntity 복사 여부 | `common/src/main/kotlin/.../BaseEntity.kt` 존재 |

### 9.2 Spring Boot 3.x 환경에서 메서드 환각 (1차 사고 재발 방지)

**⚠️ 1차 가장 큰 사고 — 반드시 확인:**

Spring Boot 3.x에서 제거된 메서드:
```
❌ WebSecurityConfigurerAdapter  → ✅ SecurityFilterChain Bean으로
❌ antMatchers()                 → ✅ requestMatchers()
❌ authorizeRequests()           → ✅ authorizeHttpRequests()
❌ HttpMethod.GET.matches()      → ✅ HttpMethod.GET.name()
❌ @EnableWebSecurity + extends  → ✅ @Configuration + @EnableWebSecurity
```

```bash
# Spring Boot 3.x 제거된 클래스 사용 여부 scan
grep -r "WebSecurityConfigurerAdapter\|antMatchers\|authorizeRequests" \
  --include="*.kt" --include="*.java" .
# 결과 없어야
```

### 9.3 의존성 충돌 (버전 불일치)

**증상:** `./gradlew build` 시 `NoSuchMethodError` 또는 `IncompatibleClassChangeError`.

```bash
# 의존성 트리 확인 (충돌 부분 표시)
./gradlew :auth-service:dependencies | grep -A5 "CONFLICT\|---"

# BOM 사용 권장 (Spring Boot parent BOM)
# build.gradle.kts
plugins {
  id("org.springframework.boot") version "3.4.x"
}
// Spring Boot BOM이 하위 의존성 버전 자동 관리
```

---

## 10. Docker·Kubernetes (Minikube) — Pod·Service·PVC

### 10.1 Pod CrashLoopBackOff

**증상:** `kubectl get pods`에서 상태가 `CrashLoopBackOff`.

**진단:**
```bash
# 이전 crash 로그 확인 (현재 로그가 비어있을 때)
kubectl logs deployment/<service> -n qtai --previous

# 종료 코드 확인
kubectl describe pod <pod-name> -n qtai | grep -A5 "Last State"
# Exit Code 1 = 애플리케이션 오류
# Exit Code 137 = OOM Kill (메모리 부족)
# Exit Code 139 = segfault
```

**빈번한 원인 + 해결:**

| 종료 코드 | 원인 | 해결 |
| --- | --- | --- |
| 1 (애플리케이션 오류) | 환경 변수 누락 (DB URL·API key 등) | `kubectl describe pod` → Env 섹션 확인 |
| 1 (DB 연결 실패) | MySQL pod 미시작 or 포트 오류 | `kubectl get pods -n qtai` — DB pod 먼저 확인 |
| 137 (OOM) | JVM heap 부족 | Deployment resources.limits.memory 증가 |
| 1 (Flyway 실패) | migration 스크립트 오류 | 로그에서 `FlywayException` 확인 |

**환경 변수 확인:**
```bash
kubectl exec -it <pod-name> -n qtai -- env | grep -i "db\|url\|key\|secret" | sort
```

### 10.2 Pod Pending / ImagePullBackOff

**증상:** Pod이 `Pending` 상태에서 시작 안 됨, 또는 `ImagePullBackOff`.

**Pending 원인:**
```bash
# 스케줄링 실패 원인 확인
kubectl describe pod <pod-name> -n qtai | grep -A10 "Events:"
# "Insufficient memory" → Node 리소스 부족
# "no nodes available" → Minikube 노드 재시작 필요
```

```bash
# Minikube 리소스 확인
minikube status
kubectl top nodes

# Minikube 재시작 (리소스 증가)
minikube stop
minikube start --memory=8192 --cpus=4
```

**ImagePullBackOff 원인:**
```bash
# 이미지 이름·태그 오타
kubectl describe pod <pod-name> -n qtai | grep "image\|Image"

# Minikube 내부에서 이미지 빌드해야 Docker Desktop이 아닌 경우
eval $(minikube docker-env)
./gradlew :auth-service:bootBuildImage
# 또는
docker build -t auth-service:latest .
```

### 10.3 Service ClusterIP로 접근 안 됨

**증상:** 서비스 간 호출 실패 (`Connection refused`).

```bash
# Service 확인
kubectl get svc -n qtai

# Endpoint 확인 (없으면 selector 오류)
kubectl get endpoints <service-name> -n qtai

# 임시 curl pod으로 직접 확인
kubectl run curl-test --image=curlimages/curl --rm -it --restart=Never \
  -n qtai -- curl http://auth-service:8080/actuator/health
```

---

## 11. MySQL·Flyway — 연결·마이그레이션·schema

### 11.1 MySQL 연결 실패

**증상:** 서비스 시작 시 `Connection refused` 또는 `FATAL: password authentication failed`.

**확인 순서:**

```bash
# 1. MySQL pod 상태
kubectl get pods -n qtai | grep db

# 2. MySQL 로그
kubectl logs deployment/auth-db -n qtai --tail=30

# 3. 직접 접속 테스트
kubectl exec -it deployment/auth-db -n qtai -- \
  psql -U qtai_user -d auth_db -c "SELECT 1"

# 4. 서비스의 DB 환경 변수 확인
kubectl exec -it deployment/auth-service -n qtai -- env | grep "SPRING_DATASOURCE"
```

**빈번한 오류:**

| 오류 | 원인 | 해결 |
| --- | --- | --- |
| `FATAL: role "qtai_user" does not exist` | DB 초기화 미완료 | `initdb.sql` migration 재실행 |
| `FATAL: database "auth_db" does not exist` | DB 미생성 | Helm chart `initdbScripts` 확인 |
| `Connection refused` (포트) | Service targetPort 오류 | `5432` 포트 매핑 확인 |
| `too many connections` | Connection pool 초과 | HikariCP `maximumPoolSize` 줄이거나 pgBouncer 도입 |
| `password authentication failed` | Secret 값 오류 | K8s Secret 값 재확인 |

**HikariCP 설정 (application.yml):**
```yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 10       # pod당 최대 연결 수
      minimum-idle: 2
      connection-timeout: 30000   # 30초
      idle-timeout: 600000        # 10분
```

### 11.2 Flyway migration 실패

**증상:** 서비스 시작 시 `FlywayException: Validate failed` 또는 migration 오류.

```bash
# Flyway 오류 로그
kubectl logs deployment/auth-service -n qtai | grep -i "flyway\|migration"
```

**빈번한 오류:**

| 오류 | 원인 | 해결 |
| --- | --- | --- |
| `Validate failed: Migration checksum mismatch` | 이미 적용된 V{N} 파일 수정 | 새 V{N+1} 파일로 변경사항 반영 |
| `Found more than one migration with version N` | 파일명 중복 (팀원 충돌) | git blame + 버전 번호 조율 |
| `Table already exists` | 중복 CREATE TABLE | `IF NOT EXISTS` 추가 또는 V 버전 정리 |
| `column does not exist` | 테이블 생성 전 컬럼 참조 | migration 파일 순서·의존 관계 확인 |

**긴급 수정 (개발 환경만):**
```bash
# flyway_schema_history 리셋 (⚠️ 개발 환경 전용 — 절대 운영 X)
kubectl exec -it deployment/auth-db -n qtai -- psql -U qtai_user -d auth_db \
  -c "DELETE FROM flyway_schema_history WHERE version = 'N';"
# 서비스 재시작
kubectl rollout restart deployment/auth-service -n qtai
```

### 11.3 @Transactional 누락 (1차 가장 큰 사고)

**증상:** 여러 DB 작업 중 일부 실패해도 이전 작업이 롤백 안 됨.

**1차 HMS 핵심 패턴 재발 방지:**
```kotlin
// ❌ @Transactional 없음 — 중간 실패 시 부분 저장
fun createSession(userId: Long): AiSession {
    val session = sessionRepository.save(...)  // 저장됨
    val turn = turnRepository.save(...)        // 실패해도 session은 저장됨
    return session
}

// ✅ @Transactional 있음 — 원자적 처리
@Transactional
fun createSession(userId: Long): AiSession {
    val session = sessionRepository.save(...)
    val turn = turnRepository.save(...)
    return session
}
```

```bash
# 서비스 전체 @Transactional 누락 점검
grep -r "fun.*Repository\|fun.*save\|fun.*delete" \
  --include="*.kt" src/main/kotlin \
  | grep -v "@Transactional" | grep -v "test"
# 결과 있으면 → 검토 후 @Transactional 추가
```

---

## 12. Redis·캐시 — 연결·TTL·Distributed Lock

### 12.1 Redis 연결 실패

**증상:** `RedisConnectionException: Unable to connect to localhost:6379` 또는 서비스 시작 실패.

```bash
# Redis pod 상태
kubectl get pods -n qtai | grep redis

# Redis ping
kubectl exec -it deployment/redis -n qtai -- redis-cli ping
# 응답: PONG

# 서비스 Redis 환경 변수 확인
kubectl exec -it deployment/auth-service -n qtai -- env | grep REDIS
```

**application.yml 확인:**
```yaml
spring:
  data:
    redis:
      host: redis            # K8s Service 이름
      port: 6379
      timeout: 3000ms        # 3초 연결 타임아웃
      lettuce:
        pool:
          max-active: 8
          max-idle: 8
          min-idle: 0
```

### 12.2 Distributed Lock 실패 (Refresh Token)

**증상:** 동시 Refresh 요청 시 race condition — 두 번째 요청이 폐기된 token으로 401.

**05번 § 3.3 + 03번 § 2.4 Distributed Lock 패턴 확인:**

```kotlin
// ✅ Redis 분산 락 — Refresh 단일 실행 보장
fun refreshTokens(refreshToken: String): TokenPair {
    val lockKey = "lock:refresh:${extractUserId(refreshToken)}"
    val lock = redisTemplate.opsForValue()
        .setIfAbsent(lockKey, "locked", Duration.ofSeconds(10))
    if (lock != true) {
        throw RefreshLockConflictException()  // 다른 요청이 진행 중
    }
    try {
        return doRefresh(refreshToken)
    } finally {
        redisTemplate.delete(lockKey)
    }
}
```

```bash
# 락 키 확인 (락이 걸린 채 남아있으면)
kubectl exec -it deployment/redis -n qtai -- redis-cli KEYS "lock:refresh:*"
# TTL 확인
kubectl exec -it deployment/redis -n qtai -- redis-cli TTL "lock:refresh:123"
# -1이면 TTL 없음 (만료 안 됨) → 락이 박혀있음 → DEL로 해제
```

---

## 13. Kafka — 토픽·컨슈머 lag·멱등성·Saga 보상

### 13.1 Kafka 메시지 미수신

**증상:** 토픽에 메시지 있는데 consumer가 처리 안 함.

```bash
# Consumer group 상태 (LAG 확인)
kubectl exec -it deployment/kafka -n qtai -- kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 --group qtai-journal-group --describe

# 출력 예시:
# TOPIC                    PARTITION  CURRENT-OFFSET  LOG-END-OFFSET  LAG
# ai.session.completed     0          5               10              5  ← lag=5 메시지 쌓임
```

**LAG 원인:**

| 원인 | 증상 | 해결 |
| --- | --- | --- |
| Consumer pod 죽음 | pod CrashLoop | § 10.1 |
| 처리 예외 무한 재시도 | LAG 증가 없음, 같은 offset 반복 | DLQ 또는 예외 무시 처리 |
| 파티션 수 > consumer 수 | 일부 파티션 unassigned | consumer 수 늘리기 |
| `max.poll.records` 너무 낮음 | 처리 속도 느림 | 값 증가 |
| commit 안 함 (auto-commit=false) | offset 안 갱신 | `acknowledgment.acknowledge()` 호출 여부 확인 |

**Spring Kafka 설정 확인:**
```yaml
spring:
  kafka:
    consumer:
      group-id: qtai-journal-group
      auto-offset-reset: earliest
      enable-auto-commit: false  # 수동 commit (멱등성)
      max-poll-records: 10
    listener:
      ack-mode: manual
```

### 13.2 멱등성 위반 — 중복 메시지 처리

**증상:** Journal이 같은 세션에서 2개 생성 (중복).

**원인:** 재시도 시 consumer가 같은 메시지를 두 번 처리.

**03번 § 2.3 + ADR-0007 멱등성 DB UNIQUE 패턴 확인:**
```sql
-- JOURNALS 테이블에 session_id UNIQUE 제약 있는지
SELECT constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_name = 'journals' AND constraint_type = 'UNIQUE';
-- session_id UNIQUE 있어야

-- 중복 journal 확인
SELECT session_id, COUNT(*) FROM JOURNALS
GROUP BY session_id HAVING COUNT(*) > 1;
```

**Spring Kafka consumer 멱등성 처리:**
```kotlin
@KafkaListener(topics = ["ai.session.completed"])
fun onSessionCompleted(event: AiSessionCompletedEvent, ack: Acknowledgment) {
    try {
        journalService.createFromSession(event.sessionId)  // UNIQUE 위반 시 skip
    } catch (e: DataIntegrityViolationException) {
        log.warn("Duplicate journal for session ${event.sessionId} — skipping")
    } finally {
        ack.acknowledge()  // 항상 commit — 재처리 방지
    }
}
```

### 13.3 토픽 없음 (auto.create.topics.enable=false)

**증상:** 서비스 시작 시 `Topic not found` 또는 produce/consume 실패.

```bash
# 토픽 목록
kubectl exec -it deployment/kafka -n qtai -- kafka-topics.sh \
  --bootstrap-server localhost:9092 --list

# 없는 토픽 수동 생성 (개발 환경)
kubectl exec -it deployment/kafka -n qtai -- kafka-topics.sh \
  --bootstrap-server localhost:9092 --create \
  --topic ai.session.completed --partitions 3 --replication-factor 1
```

**Helm chart values.yaml에 토픽 8종 전부 있는지 확인** (03번 § 2.2):
```
ai.session.completed
journal.created / journal.updated / journal.deleted
journal.creation.failed
notification.requested
user.deactivated
user.activity.tracked
```

---

## 14. CI/CD — GitHub Actions·Spectral·OpenAPI·빌드 실패

### 14.1 GitHub Actions 빌드 실패

**증상:** PR 후 CI 빌드 실패 — 로컬은 되는데 CI 안 됨.

**자주 나오는 오류:**

| 오류 | 원인 | 해결 |
| --- | --- | --- |
| `Error: JDK 21 not found` | 워크플로에 JDK setup 누락 | `actions/setup-java@v4` + `java-version: '21'` |
| `./gradlew: Permission denied` | gradlew 실행 권한 없음 | `git add --chmod=+x gradlew && git commit` |
| `flutter --version not found` | Flutter action 미설정 | `subosito/flutter-action@v2` + `flutter-version` 추가 |
| `OutOfMemoryError` | CI runner 메모리 부족 | `GRADLE_OPTS=-Xmx2g` 환경 변수 추가 |
| Spectral lint 실패 | OpenAPI 스펙 오류 | § 14.2 참조 |
| test 실패 (로컬 OK) | 시간대 차이, 환경 변수 미전달 | `env:` 섹션에 필요 변수 추가 |

**CI workflow 환경 변수 확인** (`.github/workflows/ci.yml`):
```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  SPRING_PROFILES_ACTIVE: ci
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          java-version: '21'
          distribution: 'temurin'
```

### 14.2 Spectral OpenAPI lint 실패

**증상:** CI에서 `Spectral lint failed: X errors`.

```bash
# 로컬 Spectral 실행
npx @stoplight/spectral-cli lint apis/auth/openapi.yaml \
  --ruleset .spectral.yaml

# 전체 API 스펙 lint
for f in apis/*/openapi.yaml; do
  echo "=== $f ==="; npx @stoplight/spectral-cli lint "$f" --ruleset .spectral.yaml
done
```

**빈번한 Spectral 오류:**

| 오류 | 의미 | 해결 |
| --- | --- | --- |
| `oas3-api-servers: undefined` | `servers:` 섹션 누락 | `servers:` 추가 |
| `operation-operationId: undefined` | `operationId` 누락 | 각 endpoint에 고유 operationId 추가 |
| `component-description: undefined` | `description` 누락 | schema / response에 description 추가 |
| `no-$ref-siblings` | `$ref`와 같은 레벨에 다른 키 | `$ref` 단독 사용 또는 allOf로 묶기 |
| `oas3-unused-component` | 정의된 schema 미사용 | 사용하거나 삭제 |

### 14.3 Docker 이미지 빌드 실패

```bash
# 로컬 buildx 빌드 (arm64/amd64 호환)
docker buildx build --platform linux/amd64 \
  -t auth-service:latest ./auth-service

# Spring Boot layered jar 빌드 (권장)
./gradlew :auth-service:bootBuildImage --imageName=qtai/auth-service:latest

# Minikube용 이미지 빌드 (Minikube docker env 사용)
eval $(minikube docker-env)
./gradlew :auth-service:bootBuildImage --imageName=auth-service:local
# Deployment imagePullPolicy: Never 설정 필수
```

---

## 15. 관측성 — Grafana·Prometheus·Jaeger·Loki

### 15.1 Grafana 대시보드 데이터 없음

**증상:** 대시보드가 비어있음 / `No data` 표시.

```bash
# Prometheus pod 상태
kubectl get pods -n qtai | grep prometheus

# Prometheus target 상태 확인 (서비스가 scrape되고 있는지)
# port-forward 후 브라우저에서 확인
kubectl port-forward svc/prometheus -n qtai 9090:9090
# http://localhost:9090/targets 접속

# 서비스의 /actuator/prometheus endpoint 확인
kubectl exec -it deployment/auth-service -n qtai -- \
  curl http://localhost:8080/actuator/prometheus | head -30
```

**metric 없는 경우:**
```kotlin
// Spring Boot Actuator + Micrometer 설정 확인
// build.gradle.kts
implementation("io.micrometer:micrometer-registry-prometheus")

// application.yml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus,metrics
  metrics:
    export:
      prometheus:
        enabled: true
```

### 15.2 Jaeger trace 없음 (분산 추적)

**증상:** Grafana Explore → Jaeger에서 traceId 검색 결과 없음.

**체크:**

1. **Flutter TraceInterceptor** (08번 § 6.4.1) — 요청에 `traceparent` 헤더 있는지 확인
   ```bash
   # Gateway 로그에서 traceparent 헤더 확인
   kubectl logs deployment/gateway -n qtai | grep "traceparent"
   ```

2. **Spring Boot OpenTelemetry 설정** (06번 § 12):
   ```yaml
   management:
     tracing:
       sampling:
         probability: 1.0  # 100% 샘플링 (시연)
   spring:
     application:
       name: auth-service
   # OTEL exporter endpoint
   otel:
     exporter:
       otlp:
         endpoint: http://Jaeger:4317
   ```

3. **Jaeger pod 상태**:
   ```bash
   kubectl get pods -n qtai | grep Jaeger
   kubectl logs deployment/Jaeger -n qtai --tail=30
   ```

### 15.3 Loki 로그 없음

**증상:** Grafana → Explore → Loki에서 로그 조회 안 됨.

```bash
# Loki pod 상태
kubectl get pods -n qtai | grep loki

# Promtail (로그 수집기) 상태
kubectl get pods -n qtai | grep promtail

# Promtail이 pod 로그 수집 중인지
kubectl logs daemonset/promtail -n qtai --tail=20
```

**로그 레벨 확인:**
```yaml
# application.yml
logging:
  level:
    root: INFO
    com.qtai: DEBUG
  pattern:
    console: '{"timestamp":"%d{ISO8601}","level":"%level","service":"auth-service","traceId":"%X{traceId}","message":"%msg"}%n'
```

JSON 형태 구조화 로그여야 Loki에서 `{service="auth-service"}` 쿼리로 필터링 가능.

---

## 16. 1차(HMS) 사고 통합 매트릭스 + W1 막힘 가이드

### 16.1 1차(HMS) 핵심 사고 ↔ 2차(QT-AI) 재발 방지 통합 매트릭스

| # | 1차 사고 | 2차에서 재발 위험 형태 | 본질적 가드레일 (문서) | 빠른 진단 |
| --- | --- | --- | --- | --- |
| 1 | **Spring Boot 2.x→3.x 메서드 환각** | `antMatchers()` 등 제거된 API 사용 | § 9.2 (삭제 메서드 scan) | `grep -r "antMatchers"` |
| 2 | **@Transactional 누락** | 멀티 테이블 INSERT 중 부분 실패 | § 11.3 | `grep -rL "@Transactional" *Service.kt` |
| 3 | **평문 시크릿 commit** | `ANTHROPIC_API_KEY`·`POSTGRES_PASSWORD` 코드 직접 | 05번 § 2 + § 10.1 | `git log --all -S "sk-ant"` |
| 4 | **Race condition** | Refresh Token 동시 갱신·단계 전환 race | § 12.2 + 09번 § 9.5 | Redis lock 키 TTL 확인 |
| 5 | **에러 직접 노출** | 502 원인 메시지를 Flutter에 raw 전달 | § 4.1 + 08번 § 12 | `code` enum 매핑 확인 |
| 6 | **타임아웃 미설정** | Anthropic 호출 무한 대기·앱 멈춤 | § 5.1 + 09번 § 10.3 | DIO timeout·WebClient timeout 확인 |
| 7 | **운영 가시성 없음** | 장애 발생 시 어디서 깨진지 모름 | § 15 + 06번 § 12 | Grafana 대시보드 3종 확인 |
| 8 | **DB 인덱스 없음** | 성경 구절 조회 지연·서비스 전체 느려짐 | § 7.2 | `\d+ kr_bible` 인덱스 확인 |
| 9 | **Kafka 멱등성 없음** | Journal 중복 생성 | § 13.2 + ADR-0007 | UNIQUE 제약 확인 |
| 10 | **보안 헤더 미전달** | 다른 사용자 데이터 접근 | 05번 § 3 + § 4.1 | `X-User-Id` 헤더 Gateway 주입 확인 |
| 11 | **LLM 환각** | 존재하지 않는 성경 구절 인용 | 09번 § 8.2 + § 7.1 | `verse_exists` API 검증 확인 |
| 12 | **NUL·invisible char** | 파일에 제어 문자 → GitHub binary 인식 | 재발 방지 스크립트 (§ 16.3) | byte scan |

### 16.2 W1 아이템별 막힘 + 빠른 대응

| W1 체크리스트 아이템 | 막힘 증상 | 빠른 해결 | 페어 핑 |
| --- | --- | --- | --- |
| Minikube 환경 구성 | pod 안 뜸 | § 10.2 + `minikube start --memory=8192` | 강태오 |
| Gradle 6 module 빌드 | `:auth-service:build` 실패 | § 9.1 + `./gradlew :auth-service:build --stacktrace` | 강태오 |
| MySQL 연결 | 서비스 CrashLoop | § 11.1 → `kubectl describe pod` | 강태오 |
| Flyway V1 migration | `FlywayException` | § 11.2 → 파일명 중복 확인 | 강태오 |
| Kafka 토픽 생성 | produce/consume 실패 | § 13.3 → 수동 토픽 생성 | 강태오 |
| Anthropic API key 설정 | AI Service CrashLoop | § 5.1 → K8s Secret 확인 | 강상민 |
| ChromaDB 시드 5개 | collection 없음 | § 5.2 → `rag_index.py --seed-only` | 강상민 |
| SSE 1턴 E2E | 첫 token 안 옴 | § 3.4 + § 8.3 | 강상민 ↔ 김지민 |
| STOMP CONNECT | ERROR 프레임 | § 3.5 + § 8.4 | 강태오 ↔ 김지민 |
| flutter test 통과 | analyze 오류 | § 8.5 → `build_runner build` | 김지민 |
| JWT Refresh | 401 무한 루프 | § 4.2 + § 8.1 | 이지윤 ↔ 김지민 |
| verse_exists API | 틀린 결과 | § 7.1 → 성경 시드 확인 | 김태혁 |
| Spectral lint | CI 실패 | § 14.2 → `operationId` 추가 | 강태오 |

### 16.3 문서·코드 파일 제어 문자 검증 스크립트

문서 작성 후 push 전 반드시 실행 (PowerShell here-string 사고 재발 방지):

```powershell
# 전체 .md 파일 제어 문자 검증 (0x00-0x1F 중 LF/CR/TAB 제외)
Get-ChildItem -Path "C:\Users\G\Desktop\2nd-team-work\project" -Filter "*.md" | ForEach-Object {
  $bytes = [System.IO.File]::ReadAllBytes($_.FullName);
  $bad = 0;
  foreach ($byte in $bytes) {
    if ($byte -lt 0x20 -and $byte -ne 0x09 -and $byte -ne 0x0A -and $byte -ne 0x0D) {
      $bad++;
    }
  }
  if ($bad -gt 0) { Write-Host "WARN $($_.Name): $bad 개 제어 문자" }
  else { Write-Host "OK   $($_.Name)" }
}
```

**재발 방지 룰:**
- PowerShell `@"..."@` (double-quoted here-string) 안에서 backtick 포함 마크다운 X
- 마크다운 파일은 Filesystem `write_file`로 직접 작성
- push 전 위 스크립트 실행

### 16.4 페이스 점검 (W2~W4) 기준

| 주차 | 화 11:30 체크 | ✅ 기준 | 황색 경보 (Lead 페어) |
| --- | --- | --- | --- |
| W2 5/26 | 1턴 LLM 응답 + 검증 5종 동작 여부 | 정상 1턴 완성 | 24h 내 미해결 |
| W3 6/2 | injection 30건 100% 차단 여부 | 0건 통과 | 1건이라도 통과 |
| W4 6/9 | 시연 시나리오 3분 dry-run | 끊김 없이 완주 | 중간 오류 2회+ |

**30분 이상 막힌 경우 에스컬레이션:**
1. 본 문서 해당 섹션 확인 (10분)
2. Lead(강태오)에게 Slack ping + 현재 오류 메시지 첨부 (1분)
3. 화면 공유 10분 페어 → 30분 안에 해결 시도
4. 30분 후에도 미해결 → W1 cut 항목 검토 또는 대안 구현

> **팀 문화:** 막혔을 때 혼자 1시간 씨름하는 것보다 15분 만에 Lead에게 핑하는 게 전체 일정에 훨씬 이롭다. 부끄럽지 않다.

---

> **본 문서 v1.0 이후 발견된 새 케이스는 해당 섹션 끝에 추가하고 PR 올릴 것.** Reviewer: 강태오 (Lead). 문서 자체가 살아있는 FAQ가 되도록.
