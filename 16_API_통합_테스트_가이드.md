��� QT-AI (큐티 AI 앱) — API 통합 테스트 가이드 v1.0

> **문서 버전:** v1.1
> **작성일:** 2026-05-08
> **연관 문서:** [04_API_명세서 v1.5](./04_API_명세서.md) / [07_테스트_전략 v1.0](./07_테스트_전략.md) / [10_트러블슈팅_FAQ v1.0](./10_트러블슈팅_FAQ.md)
> **owner:** 강태오 (Lead) · 각 서비스 owner (서비스별 계약 테스트)
> **목적:** 서비스 간 API 계약이 실제로 동작하는지 검증. OpenAPI 스펙 → Prism mock → Spring RestAssured / Flutter DIO 계약 테스트 흐름 박제.

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-08 | 강태오 (Lead) | 초기 작성 |
| v1.1 | 2026-05-13 | Codex | Gateway Auth 계약, Bible Service 묵상 통합, DeepSeek SSE 기준으로 정합성 보강 |

---

## 목차

1. [테스트 계층 + 도구 선택](#1-테스트-계층--도구-선택)
2. [Prism mock 서버 활용 (W1)](#2-prism-mock-서버-활용-w1)
3. [Gateway Auth 계약 테스트](#3-gateway-auth-계약-테스트)
4. [AI Service SSE 계약 테스트](#4-ai-service-sse-계약-테스트)
5. [Bible Service 묵상 Kafka 계약 테스트](#5-bible-service-묵상-kafka-계약-테스트)
6. [Flutter 클라이언트 통합 테스트](#6-flutter-클라이언트-통합-테스트)
7. [전체 E2E 시나리오 (W3 기준)](#7-전체-e2e-시나리오-w3-기준)
8. [CI 통합 게이트](#8-ci-통합-게이트)

---

## 1. 테스트 계층 + 도구 선택

### 1.1 테스트 피라미드 (07번 § 1과 정합)

```
          [E2E] 10%
         ────────────
       [Integration] 30%
      ──────────────────
    [Unit] 60%
   ────────────────────
```

| 계층 | 도구 | 목적 |
| --- | --- | --- |
| Unit | JUnit 5 + MockK / Mockito | 도메인 로직·UseCase 검증 |
| Integration | Spring Boot Test + Testcontainers (MySQL·Kafka) | 서비스 내부 DB·메시지 검증 |
| Contract | Prism mock + RestAssured / Flutter DIO | OpenAPI 계약 정합성 |
| E2E | TestContainers + Rest-Assured + Flutter integration_test | 전체 흐름 검증 |

### 1.2 Prism mock 서버

OpenAPI 파일 기반으로 실제 백엔드 없이 mock 응답 제공. W1에 Flutter·프론트 개발 병렬화 핵심 도구.

```bash
# 설치
npm install -g @stoplight/prism-cli

# Gateway Auth mock (포트 4010)
prism mock apis/auth/openapi.yaml --port 4010

# Bible Service mock (포트 4012)
prism mock apis/bible/openapi.yaml --port 4012

# AI Service mock (포트 4013)
prism mock apis/ai/openapi.yaml --port 4013

# BFF Aggregator mock (포트 4015)
prism mock apis/bff/openapi.yaml --port 4015
```

**Prism 동작 원리:** OpenAPI의 `examples` 값을 응답으로 반환. 존재하지 않는 endpoint 요청 시 404. `--validate-request` 플래그로 요청 스키마도 검증.

```bash
# 요청 스키마 검증까지 활성화
prism mock apis/auth/openapi.yaml --port 4010 --validate-request
```

---

## 2. Prism mock 서버 활용 (W1)

### 2.1 Flutter W1 병렬 개발 흐름

```
백엔드 개발 중  →  Prism mock 서버  →  Flutter 개발
(강태오·강상민)       (4010~4015)       (김지민)
```

```dart
// flutter-app/lib/core/config/env.dart — dev flavor
static const Env _dev = Env._(
  flavor: Flavor.dev,
  baseUrl: 'http://10.0.2.2:4015/api/v1',  // BFF Prism mock
  ...
);
```

**W1 완료 기준:** `fvm flutter test` 에서 Prism mock 상대로 계약 테스트 5건 통과.

### 2.2 계약 테스트 vs 통합 테스트 전환

| 주차 | 백엔드 대상 | 비고 |
| --- | --- | --- |
| W1 | Prism mock | 백엔드 미완성 |
| W2 | 실제 서비스 (dev Minikube) | Gateway Auth·Bible 완성 후 |
| W3+ | 실제 서비스 전체 | E2E |

---

## 3. Gateway Auth 계약 테스트

### 3.1 RestAssured 계약 테스트

```kotlin
// gateway/src/test/java/com/qtai/gateway/auth/contract/GatewayAuthContractTest.java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@TestPropertySource(properties = ["spring.profiles.active=test"])
class GatewayAuthContractTest {

    @LocalServerPort
    private var port: Int = 0

    @BeforeEach
    fun setup() {
        RestAssured.port = port
        RestAssured.basePath = "/api/v1"
    }

    @Test
    fun `POST login returns 200 with access and refresh tokens`() {
        given()
            .contentType(ContentType.JSON)
            .body("""{"email":"test@qtai.dev","password":"Test1234!"}""")
        .`when`()
            .post("/auth/login")
        .then()
            .statusCode(200)
            .body("accessToken", notNullValue())
            .body("refreshToken", notNullValue())
            .body("tokenType", equalTo("Bearer"))
    }

    @Test
    fun `POST login with wrong password returns 401 ProblemDetail`() {
        given()
            .contentType(ContentType.JSON)
            .body("""{"email":"test@qtai.dev","password":"wrong"}""")
        .`when`()
            .post("/auth/login")
        .then()
            .statusCode(401)
            .contentType("application/problem+json")
            .body("code", equalTo("INVALID_CREDENTIALS"))
    }

    @Test
    fun `POST refresh returns new token pair`() {
        // 1. 로그인 먼저
        val loginResponse = given()
            .contentType(ContentType.JSON)
            .body("""{"email":"test@qtai.dev","password":"Test1234!"}""")
            .post("/auth/login")
        val refreshToken = loginResponse.jsonPath().getString("refreshToken")

        // 2. refresh 호출
        given()
            .contentType(ContentType.JSON)
            .body("""{"refreshToken":"$refreshToken"}""")
        .`when`()
            .post("/auth/refresh")
        .then()
            .statusCode(200)
            .body("accessToken", notNullValue())
            .body("refreshToken", not(equalTo(refreshToken)))  // Rotation
    }
}
```

### 3.2 Testcontainers 설정

```kotlin
// gateway/src/test/java/com/qtai/gateway/auth/TestContainersConfig.java
@TestConfiguration
class TestContainersConfig {

    companion object {
        @JvmStatic
        val mysql: MySQLContainer<*> = MySQLContainer("mysql:8.0")
            .withDatabaseName("auth_test")
            .withUsername("test_user")
            .withPassword("test_pass")

        @JvmStatic
        val redis: GenericContainer<*> = GenericContainer("redis:7")
            .withExposedPorts(6379)

        @JvmStatic
        @DynamicPropertySource
        fun datasourceProperties(registry: DynamicPropertyRegistry) {
            registry.add("spring.datasource.url") { mysql.jdbcUrl }
            registry.add("spring.datasource.username") { mysql.username }
            registry.add("spring.datasource.password") { mysql.password }
            registry.add("spring.data.redis.host") { redis.host }
            registry.add("spring.data.redis.port") { redis.getMappedPort(6379).toString() }
        }

        init {
            mysql.start()
            redis.start()
        }
    }
}
```

---

## 4. AI Service SSE 계약 테스트

### 4.1 DeepSeek mock 서버 (WireMock)

```kotlin
// ai-service/src/test/java/com/qtai/ai/contract/AiServiceSseContractTest.java
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
class AiServiceSseContractTest {

    // WireMock으로 DeepSeek OpenAI 호환 API mock
    @RegisterExtension
    static WireMockExtension deepSeekMock = WireMockExtension.newInstance()
        .options(wireMockConfig().port(18443))
        .build();

    @Test
    fun `POST turns returns SSE stream with token and end events`() {
        // DeepSeek mock 응답 설정
        deepSeekMock.stubFor(
            post(urlEqualTo("/chat/completions"))
                .willReturn(aResponse()
                    .withStatus(200)
                    .withHeader("Content-Type", "text/event-stream")
                    .withBody("""
                        event: content_block_delta
                        data: {"type":"content_block_delta","delta":{"type":"text_delta","text":"창세기"}}

                        event: message_stop
                        data: {"type":"message_stop"}

                        """.trimIndent()
                    )
                )
        )

        // AI Service SSE 호출
        val client = WebTestClient.bindToServer()
            .baseUrl("http://localhost:$port")
            .build()

        val events = mutableListOf<String>()
        client.post()
            .uri("/api/v1/ai/sessions/1/turns")
            .contentType(MediaType.APPLICATION_JSON)
            .bodyValue("""{"step":"A","content":"이 구절에서 누가 등장하나요?"}""")
            .accept(MediaType.TEXT_EVENT_STREAM)
            .exchange()
            .expectStatus().isOk
            .returnResult(String::class.java)
            .responseBody
            .collectList()
            .block(Duration.ofSeconds(10))

        // SSE 이벤트 검증
        assertThat(events).anyMatch { it.contains("\"event\":\"token\"") }
        assertThat(events).anyMatch { it.contains("\"event\":\"end\"") }
    }
}
```

### 4.2 SSE 이벤트 형식 검증

```kotlin
data class SseEvent(val event: String, val data: Map<String, Any>)

fun parseSseEvents(rawStream: String): List<SseEvent> {
    val events = mutableListOf<SseEvent>()
    var currentEvent = ""
    val dataBuf = StringBuilder()

    for (line in rawStream.lines()) {
        when {
            line.startsWith("event:") -> currentEvent = line.removePrefix("event:").trim()
            line.startsWith("data:") -> {
                val raw = line.removePrefix("data:").trim()
                if (raw == "[DONE]") {
                    events += SseEvent("end", emptyMap())
                    return events
                }
                dataBuf.append(raw)
            }
            line.isEmpty() && currentEvent.isNotEmpty() -> {
                val data = jacksonObjectMapper().readValue<Map<String, Any>>(dataBuf.toString())
                events += SseEvent(currentEvent, data)
                currentEvent = ""
                dataBuf.clear()
            }
        }
    }
    return events
}
```

---

## 5. Bible Service 묵상 Kafka 계약 테스트

### 5.1 EmbeddedKafka 통합 테스트

```kotlin
// bible-service/src/test/java/com/qtai/bible/journal/kafka/JournalKafkaIntegrationTest.java
@SpringBootTest
@EmbeddedKafka(
    partitions = 3,
    topics = ["ai.session.completed", "notification.requested", "journal.created"]
)
class JournalKafkaIntegrationTest {

    @Autowired
    lateinit var kafkaTemplate: KafkaTemplate<String, String>

    @Autowired
    lateinit var journalRepository: JournalRepository

    @Test
    fun `ai session completed event creates journal exactly once (idempotency)`() {
        val sessionId = 42L
        val userId = 1L
        val event = """
            {
              "eventId": "550e8400-e29b-41d4-a716-446655440000",
              "eventType": "ai.session.completed",
              "data": {
                "sessionId": $sessionId,
                "userId": $userId,
                "summary": "창세기 1장 묵상 요약"
              }
            }
        """.trimIndent()

        // 동일 메시지 2번 발행
        kafkaTemplate.send("ai.session.completed", "session-$sessionId", event)
        kafkaTemplate.send("ai.session.completed", "session-$sessionId", event)

        // 충분한 처리 시간 대기
        Thread.sleep(3000)

        // Journal이 정확히 1개만 생성됐는지 확인 (멱등성 — ADR-0007)
        val journals = journalRepository.findBySessionId(sessionId)
        assertThat(journals).hasSize(1)
    }

    @Test
    fun `journal creation publishes notification requested event`() {
        val consumer = KafkaTestUtils.getRecords(
            consumerFactory().createConsumer("test-group", ""),
            Duration.ofSeconds(5)
        )

        // notification.requested 토픽에 메시지 있는지 확인
        assertThat(consumer.records("notification.requested")).isNotEmpty
    }
}
```

---

## 6. Flutter 클라이언트 통합 테스트

### 6.1 DIO mock (Mockito)

```dart
// flutter-app/test/auth/auth_interceptor_test.dart
void main() {
  group('AuthInterceptor', () {
    late MockDio mockDio;
    late TokenStorage mockStorage;
    late AuthInterceptor interceptor;

    setUp(() {
      mockDio = MockDio();
      mockStorage = MockTokenStorage();
      interceptor = AuthInterceptor(mockDio, mockStorage);
    });

    test('401 응답 시 refresh 호출 후 원래 요청 재시도', () async {
      // Arrange
      when(mockStorage.readRefreshToken())
          .thenAnswer((_) async => 'valid-refresh-token');
      when(mockDio.post('/auth/refresh', data: any))
          .thenAnswer((_) async => Response(
                data: {
                  'accessToken': 'new-access-token',
                  'refreshToken': 'new-refresh-token'
                },
                statusCode: 200,
                requestOptions: RequestOptions(path: '/auth/refresh'),
              ));

      // Act — 401 에러 시뮬레이션
      final err = DioException(
        type: DioExceptionType.badResponse,
        response: Response(
          statusCode: 401,
          requestOptions: RequestOptions(path: '/journals'),
        ),
        requestOptions: RequestOptions(path: '/journals'),
      );
      final handler = RequestInterceptorHandler();

      await interceptor.onError(err, handler);

      // Assert
      verify(mockDio.post('/auth/refresh', data: any)).called(1);
    });

    test('refresh도 401이면 로그인 화면으로 유도', () async {
      when(mockStorage.readRefreshToken())
          .thenAnswer((_) async => 'expired-refresh');
      when(mockDio.post('/auth/refresh', data: any))
          .thenThrow(DioException(
            type: DioExceptionType.badResponse,
            response: Response(
              statusCode: 401,
              requestOptions: RequestOptions(path: '/auth/refresh'),
            ),
            requestOptions: RequestOptions(path: '/auth/refresh'),
          ));

      // refresh 실패 → 토큰 폐기 확인
      verify(mockStorage.clearRefreshToken()).called(1);
    });
  });
}
```

### 6.2 Widget 통합 테스트 (Prism mock 상대)

```dart
// flutter-app/integration_test/auth_flow_test.dart
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('로그인 → 대시보드 진입 E2E', (tester) async {
    // Prism mock 서버가 localhost:4010에서 실행 중이어야 함
    app.main();
    await tester.pumpAndSettle();

    // 로그인 화면 확인
    expect(find.text('로그인'), findsOneWidget);

    // 이메일 입력
    await tester.enterText(find.byKey(const Key('email_field')), 'test@qtai.dev');
    await tester.enterText(find.byKey(const Key('password_field')), 'Test1234!');
    await tester.tap(find.byKey(const Key('login_button')));
    await tester.pumpAndSettle(const Duration(seconds: 3));

    // 대시보드 진입 확인
    expect(find.text('대시보드'), findsOneWidget);
  });
}
```

```bash
# 실행 (Prism mock 먼저 기동 필요)
prism mock apis/bff/openapi.yaml --port 4015 &
fvm flutter drive \
  --driver=test_driver/integration_test.dart \
  --target=integration_test/auth_flow_test.dart \
  --flavor dev
```

---

## 7. 전체 E2E 시나리오 (W3 기준)

### 7.1 W3 통합 시나리오 테스트 목록

```kotlin
// e2e/src/test/java/com/qtai/e2e/QTaiE2eTest.java
// 전체 K8s 환경에서 실행 — W3 통합 시 1회

class QTaiE2eTest {

    val gatewayUrl = "http://qtai-gateway.qtai.svc.cluster.local"

    @Test
    @Order(1)
    fun `회원가입 → 로그인 → JWT 획득`() { ... }

    @Test
    @Order(2)
    fun `성경 구절 조회 (창세기 1장 1절)`() { ... }

    @Test
    @Order(3)
    fun `AI 큐티 세션 생성 → A 단계 1턴 SSE 수신`() { ... }

    @Test
    @Order(4)
    fun `A→B→C→D 단계 진행 → 세션 완료`() { ... }

    @Test
    @Order(5)
    fun `Kafka ai.session.completed → Journal 자동 생성 확인`() { ... }

    @Test
    @Order(6)
    fun `STOMP 알림 수신 (Journal 생성 완료)`() { ... }
}
```

### 7.2 E2E 실패 대응

| 단계 실패 | 먼저 확인 | 참조 |
| --- | --- | --- |
| Auth 로그인 실패 | Gateway AuthFilter 로그 | 10번 § 4.1 |
| Bible 구절 조회 실패 | Bible Service 시드 확인 | 10번 § 7.1 |
| AI SSE 미수신 | Gateway buffering 우회 | 10번 § 3.4 |
| 묵상 DRAFT 미생성 | Bible Service Kafka consumer lag | 10번 § 6.1 |
| STOMP 알림 미수신 | BFF STOMP 로그 | 10번 § 3.5 |

---

## 8. CI 통합 게이트

### 8.1 PR 머지 차단 조건

```yaml
# .github/workflows/ci.yml
jobs:
  unit-test:
    steps:
      - run: ./gradlew test
      # 실패 시 PR 머지 차단

  spectral-lint:
    steps:
      - run: npx @stoplight/spectral-cli lint apis/*/openapi.yaml --ruleset .spectral.yaml
      # 실패 시 PR 머지 차단

  flutter-test:
    steps:
      - run: fvm flutter test --coverage
      # 실패 시 PR 머지 차단

  contract-test:
    needs: [unit-test]
    steps:
      - run: ./gradlew :gateway:test -Ptest.tags="contract"
      # 실패 시 PR 머지 차단
```

### 8.2 nightly E2E (W3 이후)

```yaml
on:
  schedule:
    - cron: '0 15 * * *'  # 매일 KST 00:00

jobs:
  e2e:
    runs-on: ubuntu-latest
    steps:
      - name: Start Minikube
        run: minikube start --memory=8192 --cpus=4
      - name: Deploy all services
        run: helm install qtai ./helm/qtai -n qtai
      - name: Wait for pods
        run: kubectl wait --for=condition=ready pod --all -n qtai --timeout=300s
      - name: Run E2E
        run: ./gradlew :e2e:test
      - name: Run AI eval
        run: python3 tests/eval/run_eval.py  # golden 100건 회귀
```

> **비용 주의:** nightly E2E는 DeepSeek API 실제 호출 가능. 09번 § 11.4 비용 한도(USD 2.0/실행) 설정 필수.
