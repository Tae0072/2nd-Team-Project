# QT-AI -- Lead (강태오) 상세 일정표 v2.0

> 이 문서 목적: W1~W5 기간 동안 강태오가 매일 "오늘 뭘 해야 하지?"를 보는 운영 매뉴얼.
> 명령어, 코드, 이유, 확인방법까지 모두 적혀 있다.

문서 버전: v2.0 | 작성일: 2026-05-08 | 담당자: 강태오 (Lead)
연관 문서: 03_아키텍처_정의서 v1.2 / 06_DevOps_운영_매뉴얼 v1.0

---

## 0. Lead 권한과 책임

**내가 가진 권한**
- `main`/`develop` 브랜치 PR 머지 -- 강태오만 가능
- K8s 클러스터/운영 서버 접근
- 아키텍처/기술스택 최종 결정
- Scope 추가/삭제 결정

**소유 파일 (다른 팀원 수정 시 강태오를 리뷰어 필수 지정)**
```
gateway-service/    bff-service/    helm/
.github/workflows/  shared-kernel/
```

> "내가 막히면 5명이 멈춘다" -- 블로커 발생 즉시 Slack #dev 공유

---

## 1. W1 시작 전 준비 (5/11 일요일 저녁)

### 레포 최신화 + 빌드 확인

```bash
cd C:\workspace\2nd-Team-Project
git pull origin main
git log --oneline -5    # 최신 커밋 5개 확인

.\gradlew.bat build -x test --no-daemon
# 결과: BUILD SUCCESSFUL  이 나와야 한다
# 실패하면 에러 메시지를 Slack #dev 에 공유하고 해결 후 월요일 시작
```

**왜 미리 하는가?**
월요일 아침에 빌드가 안 되면 팀 전체가 1시간을 낭비한다.
일요일 저녁에 미리 확인해두자.

### Minikube 기동 확인

```bash
minikube status
# "host: Running / kubelet: Running / apiserver: Running" 가 나와야 함

# 안 켜져 있으면:
minikube start --memory=6144 --cpus=4 --driver=docker
minikube status

kubectl cluster-info
# "Kubernetes control plane is running at https://..." 가 나와야 함
```

---

## 2. Foundation Lock-in 5항목 (5/22 18:00 데드라인)

5/22 18:00까지 아래 5가지 전부 완료해야 W2로 넘어갈 수 있다.
하나라도 안 되면 W2 시작 금지. 기능 0줄이어도 5가지만 끝나면 W1 성공.

```
(1) K8s 스켈레톤  -- 6개 pod가 Running + /actuator/health 200 응답
(2) Kafka 토픽 8종 -- 자동 생성 스크립트 동작
(3) Spectral lint  -- OpenAPI 5종 CI green
(4) Observability  -- Loki/Prometheus/Jaeger 대시보드 접속 가능
(5) AuthFilter     -- JWT 검증 + X-User-Id 헤더 주입 동작
```

---

## 3. Day1 -- 5/12(화): K8s 인프라 기동

### 왜 이 날 이걸 해야 하는가?

5명이 서비스를 개발하려면 MySQL, Redis, Kafka, ChromaDB가 먼저 있어야 한다.
내가 이것을 만들지 않으면:
- 이지윤: Auth DB 없어서 로그인 기능 구현 불가
- 강상민: ChromaDB 없어서 RAG 테스트 불가
- 이승욱: Kafka 없어서 Outbox 구현 불가

### namespace 생성

```bash
kubectl create namespace qtai

# 확인
kubectl get namespace qtai
# STATUS: Active  나오면 성공
```

### Helm으로 인프라 배포

Helm이란? K8s 애플리케이션을 패키지로 쉽게 설치하는 도구다.
`helm install` 한 줄이면 복잡한 MySQL도 설치된다.

```bash
# Helm 레포 추가
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
helm repo update
```

```bash
# MySQL 배포
helm install qtai-mysql bitnami/mysql \
  --namespace qtai \
  --set auth.rootPassword=qtai_root \
  --set auth.database=auth_db \
  --set primary.persistence.size=2Gi

# Redis 배포 (Auth Refresh Token 저장, Bible 캐시)
helm install qtai-redis bitnami/redis \
  --namespace qtai \
  --set auth.enabled=false \
  --set master.persistence.size=1Gi

# Kafka 배포 (이벤트 발행/구독)
helm install qtai-kafka bitnami/kafka \
  --namespace qtai \
  --set controller.replicaCount=1 \
  --set listeners.client.protocol=PLAINTEXT
```

```bash
# pod 상태 확인 (모두 Running 될 때까지 기다린다 -- 3~5분 소요)
kubectl get pods -n qtai -w
# Ctrl+C 로 중단
# mysql-0, redis-master-0, kafka-controller-0 이 모두 Running 이면 완료
```

### 서비스별 DB 생성

```bash
# MySQL 접속
kubectl exec -it qtai-mysql-0 -n qtai -- mysql -u root -pqtai_root

# MySQL 프롬프트에서 실행
CREATE DATABASE auth_db    CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE bible_db   CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE journal_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE ai_db      CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
SHOW DATABASES;   -- 4개 확인
EXIT;
```

### K8s Secret 생성

**왜 Secret을 쓰는가?**
비밀번호나 API 키를 코드에 직접 쓰면 GitHub에 올라간다.
gitleaks가 CI에서 이것을 감지해서 빌드를 실패시킨다.
Secret은 K8s 내부에만 저장되고 코드에는 환경변수 이름만 쓴다.

```bash
# JWT 키쌍 생성 (Auth Service가 사용)
openssl genrsa -out jwt_private.pem 2048
openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem

# K8s Secret으로 등록
kubectl create secret generic qtai-jwt-keys -n qtai \
  --from-file=jwt_private.pem \
  --from-file=jwt_public.pem

# 로컬 파일 즉시 삭제 (Git에 올라가면 안 됨)
Remove-Item jwt_private.pem, jwt_public.pem

# Anthropic API Key Secret
kubectl create secret generic qtai-anthropic -n qtai \
  --from-literal=api-key="sk-ant-api03-여기에실제키입력"

# MySQL 접속 정보 Secret
kubectl create secret generic qtai-mysql-creds -n qtai \
  --from-literal=username=qtai \
  --from-literal=password=qtai_pass

# 확인
kubectl get secrets -n qtai
# 4개 Secret이 목록에 나와야 함
```

---

## 4. Day2 -- 5/13(수): Gateway AuthFilter 테스트 + Kafka 토픽

### AuthFilter가 하는 일

```
클라이언트 --> [Gateway 8080] --> [AuthFilter] --> [각 서비스]
                    |
                JWT 없으면 --> 401 Unauthorized 반환

AuthFilter 통과 후:
  요청 헤더에 "X-User-Id: 1001" 추가 --> 각 서비스에 전달
  각 서비스는 JWT 직접 검증 불필요 (Gateway가 이미 함)
```

**로컬 테스트**

```bash
# gateway-service 실행
.\gradlew.bat :gateway-service:bootRun

# 다른 터미널에서: JWT 없이 요청 --> 401 확인
curl -i http://localhost:8080/bible/passages/JHN/3
# 기대: HTTP/1.1 401 Unauthorized

# /auth 경로는 필터 제외 (로그인 요청은 토큰 없이 가야 함)
curl -i -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"x\",\"password\":\"x\"}"
# 기대: 401이 아닌 응답 (auth-service 없으면 502)
```

### Kafka 토픽 8종 생성 스크립트 (scripts/kafka-topics.sh)

```bash
#!/bin/bash
KAFKA_POD=$(kubectl get pods -n qtai -l app.kubernetes.io/name=kafka \
  -o jsonpath='{.items[0].metadata.name}')

TOPICS=(
  "journal.created" "journal.updated" "journal.deleted"
  "journal.creation.failed" "ai.session.completed"
  "user.activity.tracked" "user.deactivated" "notification.requested"
)

for TOPIC in "${TOPICS[@]}"; do
  kubectl exec -n qtai $KAFKA_POD -- kafka-topics.sh \
    --bootstrap-server localhost:9092 \
    --create --if-not-exists --topic "$TOPIC" \
    --partitions 3 --replication-factor 1
  echo "Created: $TOPIC"
done

kubectl exec -n qtai $KAFKA_POD -- kafka-topics.sh \
  --bootstrap-server localhost:9092 --list
```

```bash
bash scripts/kafka-topics.sh
# 토픽 8개 이름이 출력되어야 함
```

---

## 5. Day3~5 -- 5/14~5/16: K8s 스켈레톤 6 pod 배포

### 전체 흐름

```
1. Docker 이미지 빌드: .\gradlew.bat :서비스명:bootBuildImage
2. Minikube 로컬 이미지로 로드
3. Deployment + Service yaml 작성
4. kubectl apply 로 배포
5. /actuator/health 로 동작 확인
```

**gateway-service 배포 예시**

```bash
# Minikube Docker 환경으로 전환 (이 터미널에서만 유효)
& minikube -p minikube docker-env --shell powershell | Invoke-Expression

# 이미지 빌드
.\gradlew.bat :gateway-service:bootBuildImage --imageName=gateway-service:latest

# K8s에 배포
kubectl apply -f helm/qtai-umbrella/templates/gateway.yaml

# 로그 확인
kubectl logs -n qtai deployment/gateway-service
# "Started GatewayServiceApplication" 이 나오면 성공
```

K8s Deployment yaml 핵심 구조:
```yaml
# helm/qtai-umbrella/templates/gateway.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: gateway-service
  namespace: qtai
spec:
  replicas: 1
  selector:
    matchLabels:
      app: gateway-service
  template:
    spec:
      containers:
      - name: gateway-service
        image: gateway-service:latest
        imagePullPolicy: Never    # Minikube 로컬 이미지
        ports:
        - containerPort: 8080
        env:
        - name: JWT_PUBLIC_KEY_PATH
          value: /run/secrets/jwt_public.pem
        volumeMounts:
        - name: jwt-keys
          mountPath: /run/secrets
          readOnly: true
        livenessProbe:
          httpGet:
            path: /actuator/health
            port: 8080
          initialDelaySeconds: 30
      volumes:
      - name: jwt-keys
        secret:
          secretName: qtai-jwt-keys
```

나머지 5개 서비스 포트: auth=8081, bible=8082, bff=8083, journal=8084, ai=8085

---

## 6. Day6~9 -- 5/19~5/22: Observability + BFF + Foundation 최종 점검

### Observability 배포

```bash
# Loki + Prometheus + Grafana
helm install qtai-monitoring grafana/loki-stack \
  --namespace qtai \
  --set grafana.enabled=true \
  --set prometheus.enabled=true \
  --set prometheus.server.persistence.enabled=false

# Jaeger (분산 추적)
helm install qtai-jaeger jaegertracing/jaeger \
  --namespace qtai \
  --set allInOne.enabled=true \
  --set storage.type=memory

# Grafana 로컬 접속: http://localhost:3000 (admin/admin)
kubectl port-forward svc/qtai-monitoring-grafana 3000:80 -n qtai &
```

### BFF DashboardUseCase -- 4개 서비스 병렬 호출

**왜 WebFlux(Mono)를 쓰는가?**
순서대로 호출하면 응답시간이 합산된다. 병렬이 2배 이상 빠르다.

```kotlin
// bff-service/.../usecase/DashboardUseCase.kt
@Service
class DashboardUseCase(private val webClient: WebClient) {

    fun getDashboard(userId: Long): Mono<Map<String, Any?>> {
        val userMono = webClient.get()
            .uri("http://auth-service:8081/auth/me")
            .header("X-User-Id", userId.toString())
            .retrieve().bodyToMono(Map::class.java)
            .onErrorReturn(emptyMap<String, Any>())

        val verseMono = webClient.get()
            .uri("http://bible-service:8082/bible/passages/JHN/3/16")
            .retrieve().bodyToMono(Map::class.java)
            .onErrorReturn(emptyMap<String, Any>())

        // zip: 둘 다 응답할 때까지 기다렸다가 합친다
        return Mono.zip(userMono, verseMono).map { tuple ->
            mapOf("user" to tuple.t1, "todayVerse" to tuple.t2)
        }
    }
}
```

### W1 Lock-in 최종 체크 (5/22 18:00)

```bash
# (1) K8s 6 pod 모두 Running
kubectl get pods -n qtai

# (2) Kafka 토픽 8종
KAFKA_POD=$(kubectl get pods -n qtai -l app.kubernetes.io/name=kafka \
  -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n qtai $KAFKA_POD -- kafka-topics.sh \
  --bootstrap-server localhost:9092 --list

# (3) CI Spectral green -- GitHub Actions 탭 확인

# (4) Grafana 접속
kubectl port-forward svc/qtai-monitoring-grafana 3000:80 -n qtai &
curl http://localhost:3000/api/health   # {"database":"ok",...}

# (5) AuthFilter 401
kubectl port-forward svc/gateway-service 8080:8080 -n qtai &
curl -i http://localhost:8080/bible/passages/JHN/3
# HTTP/1.1 401 Unauthorized  나와야 함
```

---

## 7. 자주 쓰는 명령어 모음

```bash
# pod 실시간 로그
kubectl logs -f -n qtai deployment/auth-service

# pod 안으로 들어가기 (디버깅)
kubectl exec -it -n qtai deployment/auth-service -- /bin/sh

# pod 재시작
kubectl rollout restart deployment/gateway-service -n qtai

# 포트 포워딩
kubectl port-forward svc/qtai-mysql 3306:3306 -n qtai &

# 배포 현황
helm list -n qtai

# Minikube 재시작
minikube stop && minikube start --memory=6144 --cpus=4 --driver=docker
```

---

## 8. Claude 활용 가이드

**물어보면 좋은 것**
- "Kotlin WebFlux Mono.zip() 패턴 알려줘"
- "이 K8s yaml 에러 원인이 뭐야: [에러 메시지 붙여넣기]"
- "Helm chart values.yaml 에서 이 옵션이 무슨 의미인지 설명해줘"

**절대 붙여넣으면 안 되는 것**
- ANTHROPIC_API_KEY (sk-ant-api03-...)
- JWT private key 파일 내용
- MySQL root 비밀번호

**Claude 코드를 쓰기 전 꼭 확인할 것**
1. import 하는 라이브러리가 build.gradle.kts에 있는가?
2. Spring Boot 3.4.x에서 지원하는 API인가?
3. 코드를 그대로 복붙하지 말고, 한 줄씩 읽고 이해한 후 사용

---

## 9. W2~W5 주간 요약

| 주차 | 강태오 핵심 작업 |
|------|----------------|
| W2 (5/26~5/29) | BFF /me/dashboard 실데이터 연결, Gateway CORS, 팀원 PR 리뷰 |
| W3 (6/1~6/5) | Kafka E2E 흐름 검증, Feature Freeze 선언(6/3), SSE P95 측정 |
| W4 (6/8~6/12) | v1.0.0-demo 태그, 30분 pod 유지 확인, 부하 테스트, dry-run |
| W5 (6/15~6/17) | D-30분 헬스체크, 리허설 진행 주도, 발표 기술 파트 담당 |
