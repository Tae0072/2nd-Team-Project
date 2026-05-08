# QT-AI -- DevA (이지윤) Auth Service 상세 일정표 v2.0

> 이 문서 목적: Auth Service를 처음부터 끝까지 만드는 단계별 가이드.
> "어디서 뭘 왜 어떻게"를 명령어와 코드 수준으로 설명한다.

문서 버전: v2.0 | 작성일: 2026-05-08 | 담당자: 이지윤
연관 문서: 02_ERD_문서 v1.2 / 04_API_명세서 v1.2 / 05_보안_명세서 v1.0

---

## 0. Auth Service가 하는 일

Auth Service는 "이 사람이 누구인지 증명하는" 서비스다.

```
사용자 로그인 --> JWT 토큰(신분증) 발급
다른 서비스에 요청할 때 --> Gateway가 토큰 검증 --> X-User-Id 헤더 추가
사용자 로그아웃 --> 토큰 무효화 (Redis blacklist 등록)
```

**이지윤이 만들어야 하는 API**
```
POST /auth/register           회원가입
POST /auth/login              로그인 --> JWT Access + Refresh 토큰 발급
POST /auth/logout             로그아웃 --> Refresh 토큰 무효화
POST /auth/refresh            Access Token 갱신
GET  /auth/me                 내 정보 조회
POST /auth/me/deactivate      회원 탈퇴
GET  /auth/oauth/google       Google 로그인 시작
GET  /auth/oauth/google/callback  Google 로그인 완료
```

**Auth Service가 W1에 완성되어야 하는 이유**
Gateway AuthFilter는 Auth Service에서 발급한 JWT를 검증한다.
Auth Service가 없으면 Gateway도, 다른 4개 서비스도 인증이 동작하지 않는다.

---

## 1. 환경 세팅 (5/12 아침, 30분)

### 레포 최신화

```bash
cd C:\workspace\2nd-Team-Project
git pull origin main

# auth-service 빌드 확인
.\gradlew.bat :auth-service:build -x test --no-daemon
# "BUILD SUCCESSFUL" 이 나와야 한다
# 실패하면 에러 메시지를 Slack #dev 에 공유
```

### IntelliJ에서 프로젝트 열기

```
1. IntelliJ 실행
2. File --> Open --> C:\workspace\2nd-Team-Project 선택
3. Gradle 프로젝트로 인식될 때까지 기다리기 (우하단 진행바 완료까지)
4. 왼쪽 프로젝트 트리에 auth-service 모듈이 보이면 성공
```

---

## 2. Day1 -- 5/12(화): 패키지 구조 + Flyway SQL

### 패키지 구조 만들기

IntelliJ 왼쪽 트리에서 `auth-service/src/main/kotlin` 폴더를 찾아
아래 폴더들을 순서대로 만든다.

**폴더 만드는 법**: 폴더 우클릭 --> New --> Package --> 패키지명 입력

```
com.qtai.authservice
├── domain/
│   └── user/
│       ├── entity/          User.kt 파일이 들어갈 곳
│       └── repository/      UserRepository.kt 파일이 들어갈 곳
├── usecase/                 RegisterUseCase.kt, LoginUseCase.kt 등
├── api/                     AuthController.kt 파일이 들어갈 곳
└── infrastructure/
    └── jwt/                 JwtProvider.kt 파일이 들어갈 곳
```

### Flyway SQL 파일 생성

**Flyway란?**
DB 테이블 생성 SQL을 버전으로 관리해주는 도구다.
파일에 CREATE TABLE 을 적어두면 서비스 시작 시 자동으로 실행된다.
팀원마다 DB 구조가 달라지는 문제를 막아준다.

**파일 위치**: `auth-service/src/main/resources/db/migration/V1__create_auth_tables.sql`

> 파일명 규칙이 매우 중요하다:
> V + 숫자 + __(언더바 두 개) + 설명 + .sql
> V1_create.sql (언더바 1개) 처럼 쓰면 Flyway가 인식을 못 한다.

```sql
-- V1__create_auth_tables.sql
-- 이 파일에 적힌 SQL은 서비스 시작 시 자동으로 실행된다.

-- 회원 테이블
CREATE TABLE IF NOT EXISTS users (
    user_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    email      VARCHAR(255) NOT NULL UNIQUE,     -- UNIQUE: 같은 이메일 중복 가입 불가
    password   VARCHAR(255),                      -- Google 로그인은 비밀번호 없음 --> NULL 허용
    nickname   VARCHAR(50)  NOT NULL,
    provider   ENUM('LOCAL','GOOGLE') NOT NULL DEFAULT 'LOCAL',
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,    -- FALSE = 탈퇴한 계정
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6)
               ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Refresh Token 테이블
CREATE TABLE IF NOT EXISTS refresh_tokens (
    token_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT NOT NULL,
    token      VARCHAR(512) NOT NULL UNIQUE,
    expires_at DATETIME(6) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Google OAuth 연동 테이블
CREATE TABLE IF NOT EXISTS oauth_links (
    oauth_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id     BIGINT NOT NULL,
    provider    ENUM('GOOGLE') NOT NULL,
    provider_id VARCHAR(255) NOT NULL,
    UNIQUE KEY uq_provider_id (provider, provider_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```

---

## 3. Day2 -- 5/13(수): User Entity + JwtProvider

### User.kt -- JPA Entity

**JPA Entity란?**
DB 테이블과 1:1로 연결되는 Kotlin 클래스다.
`users` 테이블의 각 컬럼이 클래스의 필드가 된다.
`@Entity`를 붙이면 Spring이 DB와 자동으로 연결해준다.

```kotlin
// auth-service/src/main/kotlin/com/qtai/authservice/domain/user/entity/User.kt
package com.qtai.authservice.domain.user.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity                          // "이 클래스가 DB 테이블과 연결된다"고 Spring에 알림
@Table(name = "users")           // 연결할 테이블 이름
class User(
    @Column(nullable = false, unique = true)
    var email: String,

    @Column                      // null 허용 (Google 로그인은 비밀번호 없음)
    var password: String? = null,

    @Column(nullable = false)
    var nickname: String,

    @Enumerated(EnumType.STRING) // DB에 "LOCAL" 또는 "GOOGLE" 문자열로 저장
    @Column(nullable = false)
    val provider: Provider = Provider.LOCAL,

    @Column(nullable = false)
    var isActive: Boolean = true,     // false = 탈퇴한 계정

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)  // AUTO_INCREMENT
    val userId: Long = 0,

    @Column(nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    enum class Provider { LOCAL, GOOGLE }

    // 소프트 삭제: 실제로 DB에서 지우지 않고 isActive 만 false로 바꿈
    // "왜 실제 삭제를 안 하는가?" --> 데이터 복구 가능, 감사 로그 유지
    fun deactivate() {
        this.isActive = false
        this.updatedAt = LocalDateTime.now()
    }
}
```

### UserRepository.kt

```kotlin
// auth-service/.../domain/user/repository/UserRepository.kt
package com.qtai.authservice.domain.user.repository

import com.qtai.authservice.domain.user.entity.User
import org.springframework.data.jpa.repository.JpaRepository
import java.util.Optional

// JpaRepository 를 상속하면 save(), findById(), findAll() 등을 자동으로 쓸 수 있다
interface UserRepository : JpaRepository<User, Long> {

    // 메서드 이름만 보고 Spring Data JPA 가 SQL을 자동으로 만들어준다
    // findByEmail --> SELECT * FROM users WHERE email = ?
    fun findByEmail(email: String): Optional<User>

    // existsByEmail --> SELECT COUNT(*) > 0 FROM users WHERE email = ?
    fun existsByEmail(email: String): Boolean
}
```

### JwtProvider.kt -- JWT 토큰 발급/검증

**JWT (JSON Web Token) 이란?**
로그인 성공 시 서버가 발급하는 암호화된 신분증이다.

```
eyJhbGciOiJSUzI1NiJ9  .  eyJ1c2VySWQiOjEwMDF9  .  서명값
      (헤더)                    (페이로드)              (서명)
```

페이로드에는 userId, 만료시간이 담긴다.
RS256 서명은 서버만 가진 개인키로 만들어지므로 위조가 불가능하다.

```kotlin
// auth-service/.../infrastructure/jwt/JwtProvider.kt
package com.qtai.authservice.infrastructure.jwt

import io.jsonwebtoken.Jwts
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.Resource
import org.springframework.stereotype.Component
import java.security.KeyFactory
import java.security.interfaces.RSAPrivateKey
import java.security.interfaces.RSAPublicKey
import java.security.spec.PKCS8EncodedKeySpec
import java.security.spec.X509EncodedKeySpec
import java.util.Base64
import java.util.Date

@Component
class JwtProvider(
    @Value("\${jwt.private-key-path}") private val privateKeyRes: Resource,
    @Value("\${jwt.public-key-path}")  private val publicKeyRes: Resource
) {
    private val ACCESS_EXPIRY  = 15 * 60 * 1000L           // 15분
    private val REFRESH_EXPIRY = 7 * 24 * 60 * 60 * 1000L  // 7일

    // lazy: 처음 쓸 때 한 번만 파일에서 읽는다 (매 요청마다 파일 읽지 않음)
    private val privateKey: RSAPrivateKey by lazy { loadPrivateKey() }
    private val publicKey: RSAPublicKey   by lazy { loadPublicKey() }

    // Access Token 발급 (15분 유효)
    fun issueAccessToken(userId: Long): String = Jwts.builder()
        .claim("userId", userId)                    // 페이로드에 userId 저장
        .issuedAt(Date())
        .expiration(Date(System.currentTimeMillis() + ACCESS_EXPIRY))
        .signWith(privateKey, Jwts.SIG.RS256)       // RS256 개인키로 서명
        .compact()

    // Refresh Token 발급 (7일 유효)
    fun issueRefreshToken(userId: Long): String = Jwts.builder()
        .claim("userId", userId)
        .issuedAt(Date())
        .expiration(Date(System.currentTimeMillis() + REFRESH_EXPIRY))
        .signWith(privateKey, Jwts.SIG.RS256)
        .compact()

    // 토큰에서 userId 추출 (서명 검증도 함께 수행)
    fun getUserId(token: String): Long {
        val claims = Jwts.parser()
            .verifyWith(publicKey)   // 공개키로 서명 검증 (위조된 토큰은 여기서 예외 발생)
            .build()
            .parseSignedClaims(token)
        return (claims.payload["userId"] as Int).toLong()
    }

    private fun loadPrivateKey(): RSAPrivateKey {
        val pem = privateKeyRes.inputStream.bufferedReader().use { it.readText() }
            .replace("-----BEGIN PRIVATE KEY-----", "")
            .replace("-----END PRIVATE KEY-----", "")
            .replace("\n", "").trim()
        return KeyFactory.getInstance("RSA")
            .generatePrivate(PKCS8EncodedKeySpec(Base64.getDecoder().decode(pem))) as RSAPrivateKey
    }

    private fun loadPublicKey(): RSAPublicKey {
        val pem = publicKeyRes.inputStream.bufferedReader().use { it.readText() }
            .replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace("\n", "").trim()
        return KeyFactory.getInstance("RSA")
            .generatePublic(X509EncodedKeySpec(Base64.getDecoder().decode(pem))) as RSAPublicKey
    }
}
```

**application.yml 에 추가** (auth-service/src/main/resources/application.yml):
```yaml
jwt:
  private-key-path: ${JWT_PRIVATE_KEY_PATH:/run/secrets/jwt_private.pem}
  public-key-path: ${JWT_PUBLIC_KEY_PATH:/run/secrets/jwt_public.pem}
```

---

## 4. Day3~4 -- 5/14~5/15: UseCase 구현

### RegisterUseCase.kt

```kotlin
// auth-service/.../usecase/RegisterUseCase.kt
package com.qtai.authservice.usecase

import com.qtai.authservice.domain.user.entity.User
import com.qtai.authservice.domain.user.repository.UserRepository
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class RegisterUseCase(
    private val userRepository: UserRepository,
    private val passwordEncoder: BCryptPasswordEncoder
) {
    // @Transactional: 이 메서드 안에서 DB 작업이 실패하면 전부 롤백
    @Transactional
    fun register(email: String, password: String, nickname: String): User {
        // 이메일 중복 체크
        if (userRepository.existsByEmail(email)) {
            throw IllegalArgumentException("이미 사용 중인 이메일입니다.")
        }

        // bcrypt 해싱
        // "왜 해싱하는가?" --> DB가 해킹당해도 원래 비밀번호를 알 수 없게 하기 위해
        // bcrypt는 같은 비밀번호도 매번 다른 해시값을 만든다 (rainbow table 공격 방지)
        val hashedPassword = passwordEncoder.encode(password)

        return userRepository.save(
            User(email = email, password = hashedPassword, nickname = nickname)
        )
    }
}
```

### LoginUseCase.kt

```kotlin
// auth-service/.../usecase/LoginUseCase.kt
package com.qtai.authservice.usecase

import com.qtai.authservice.domain.user.repository.UserRepository
import com.qtai.authservice.infrastructure.jwt.JwtProvider
import org.springframework.data.redis.core.RedisTemplate
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import org.springframework.stereotype.Service
import java.util.concurrent.TimeUnit

data class TokenPair(val accessToken: String, val refreshToken: String)

@Service
class LoginUseCase(
    private val userRepository: UserRepository,
    private val passwordEncoder: BCryptPasswordEncoder,
    private val jwtProvider: JwtProvider,
    private val redisTemplate: RedisTemplate<String, String>
) {
    fun login(email: String, password: String): TokenPair {
        // 1. 이메일로 사용자 찾기
        val user = userRepository.findByEmail(email)
            .orElseThrow { IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다.") }

        // 2. 탈퇴한 계정 확인
        if (!user.isActive) throw IllegalArgumentException("탈퇴한 계정입니다.")

        // 3. 비밀번호 검증
        // matches(입력한 비밀번호, DB에 저장된 해시값) --> true/false 반환
        if (!passwordEncoder.matches(password, user.password)) {
            throw IllegalArgumentException("이메일 또는 비밀번호가 올바르지 않습니다.")
        }

        // 4. JWT 발급
        val accessToken  = jwtProvider.issueAccessToken(user.userId)
        val refreshToken = jwtProvider.issueRefreshToken(user.userId)

        // 5. Refresh Token 을 Redis에 저장 (7일 후 자동 만료)
        // 키 형식: "refresh:{userId}"
        // "왜 Redis인가?" --> Redis는 TTL(자동 만료) 기능이 있어서 만료된 토큰을 자동 삭제
        redisTemplate.opsForValue()
            .set("refresh:${user.userId}", refreshToken, 7, TimeUnit.DAYS)

        return TokenPair(accessToken, refreshToken)
    }
}
```

### LogoutUseCase.kt

```kotlin
// auth-service/.../usecase/LogoutUseCase.kt
package com.qtai.authservice.usecase

import com.qtai.authservice.infrastructure.jwt.JwtProvider
import org.springframework.data.redis.core.RedisTemplate
import org.springframework.stereotype.Service
import java.util.concurrent.TimeUnit

@Service
class LogoutUseCase(
    private val jwtProvider: JwtProvider,
    private val redisTemplate: RedisTemplate<String, String>
) {
    fun logout(refreshToken: String) {
        try {
            val userId = jwtProvider.getUserId(refreshToken)

            // Redis 에서 Refresh Token 삭제
            redisTemplate.delete("refresh:$userId")

            // Blacklist 에 등록 (15분짜리 Access Token 도 즉시 무효화)
            // "왜 필요한가?" --> Access Token 이 탈취되어도 로그아웃하면 즉시 사용 불가
            redisTemplate.opsForValue()
                .set("blacklist:$refreshToken", "1", 7, TimeUnit.DAYS)
        } catch (e: Exception) {
            // 이미 만료된 토큰으로 로그아웃 시도해도 에러 없이 처리
        }
    }
}
```

---

## 5. Day5~9 -- 5/16~5/22: Controller + 테스트

### AuthController.kt

```kotlin
// auth-service/.../api/AuthController.kt
package com.qtai.authservice.api

import com.qtai.authservice.usecase.LoginUseCase
import com.qtai.authservice.usecase.LogoutUseCase
import com.qtai.authservice.usecase.RegisterUseCase
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/auth")    // 이 Controller의 모든 경로는 /auth 로 시작
class AuthController(
    private val registerUseCase: RegisterUseCase,
    private val loginUseCase: LoginUseCase,
    private val logoutUseCase: LogoutUseCase
) {
    // POST /auth/register --> 201 Created
    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    fun register(@RequestBody req: RegisterRequest): UserResponse {
        val user = registerUseCase.register(req.email, req.password, req.nickname)
        return UserResponse(user.userId, user.email, user.nickname)
    }

    // POST /auth/login --> 200 OK
    @PostMapping("/login")
    fun login(@RequestBody req: LoginRequest): TokenResponse {
        val tokens = loginUseCase.login(req.email, req.password)
        return TokenResponse(
            accessToken  = tokens.accessToken,
            refreshToken = tokens.refreshToken,
            tokenType    = "Bearer",
            expiresIn    = 900    // 15분 = 900초
        )
    }

    // POST /auth/logout --> 204 No Content
    @PostMapping("/logout")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    fun logout(@RequestBody req: LogoutRequest) {
        logoutUseCase.logout(req.refreshToken)
    }
}

// DTO (Data Transfer Object): API 요청/응답 데이터 구조 정의
data class RegisterRequest(val email: String, val password: String, val nickname: String)
data class LoginRequest(val email: String, val password: String)
data class LogoutRequest(val refreshToken: String)
data class UserResponse(val userId: Long, val email: String, val nickname: String)
data class TokenResponse(
    val accessToken: String,
    val refreshToken: String,
    val tokenType: String,
    val expiresIn: Int
)
```

### BCryptPasswordEncoder 빈 등록

```kotlin
// auth-service/.../AuthServiceApplication.kt
package com.qtai.authservice

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder

@SpringBootApplication
class AuthServiceApplication {
    @Bean
    fun passwordEncoder() = BCryptPasswordEncoder(12)
    // 12 = 해싱 강도 (높을수록 안전하고 느림)
}

fun main(args: Array<String>) {
    runApplication<AuthServiceApplication>(*args)
}
```

### curl 로 직접 테스트

```bash
# 서비스 실행
.\gradlew.bat :auth-service:bootRun

# 회원가입
curl -X POST http://localhost:8081/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"password\":\"Test1234!\",\"nickname\":\"테스터\"}"
# 기대 응답: {"userId":1,"email":"test@test.com","nickname":"테스터"}

# 로그인
curl -X POST http://localhost:8081/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"password\":\"Test1234!\"}"
# 기대 응답: {"accessToken":"eyJ...","refreshToken":"eyJ...","tokenType":"Bearer","expiresIn":900}

# 잘못된 비밀번호 --> 에러 확인
curl -X POST http://localhost:8081/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@test.com\",\"password\":\"wrong\"}"
# 기대: 에러 메시지 응답
```

### 단위 테스트 작성

**왜 테스트를 작성하는가?**
내가 코드를 고쳤을 때 기존 기능이 망가졌는지 자동으로 확인해준다.

```kotlin
// auth-service/src/test/kotlin/.../usecase/RegisterUseCaseTest.kt
package com.qtai.authservice.usecase

import com.qtai.authservice.domain.user.repository.UserRepository
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.kotlin.*

class RegisterUseCaseTest {

    // Mock: 실제 DB 대신 가짜 객체 사용 --> 테스트에서 DB 연결 없이 동작
    private val userRepository: UserRepository = mock()
    private val passwordEncoder = org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder()
    private val useCase = RegisterUseCase(userRepository, passwordEncoder)

    @Test
    fun `정상 회원가입 성공`() {
        // Given: 이메일이 없는 상황 설정
        whenever(userRepository.existsByEmail("test@test.com")).thenReturn(false)
        whenever(userRepository.save(any())).thenAnswer { it.arguments[0] }

        // When: 회원가입 실행
        val result = useCase.register("test@test.com", "Test1234!", "테스터")

        // Then: 저장이 1번 호출됐는지, 이메일이 맞는지 확인
        verify(userRepository, times(1)).save(any())
        assertEquals("test@test.com", result.email)
    }

    @Test
    fun `중복 이메일은 예외 발생`() {
        // Given: 이미 이메일이 존재하는 상황
        whenever(userRepository.existsByEmail("test@test.com")).thenReturn(true)

        // When & Then: 예외가 발생하는지 확인
        val ex = assertThrows(IllegalArgumentException::class.java) {
            useCase.register("test@test.com", "Test1234!", "테스터")
        }
        assertEquals("이미 사용 중인 이메일입니다.", ex.message)
    }
}
```

```bash
# 테스트 실행
.\gradlew.bat :auth-service:test --no-daemon

# 결과 보기
# auth-service/build/reports/tests/test/index.html 을 브라우저로 열기
```

---

## 6. 자주 발생하는 오류

| 오류 메시지 | 원인 | 해결 방법 |
|------------|------|----------|
| `Failed to configure a DataSource` | application.yml 에 DB URL 없음 | `spring.datasource.url` 추가 확인 |
| `Could not autowire JwtProvider` | @Component 없음 | JwtProvider 클래스에 `@Component` 추가 |
| `Flyway migration failed` | SQL 파일명 형식 오류 | `V1__(언더바2개)xxx.sql` 형식인지 확인 |
| `Bad credentials` | 비밀번호 불일치 | `passwordEncoder.matches()` 사용했는지 확인 |
| `Cannot deserialize value` | JSON 필드명 불일치 | DTO 필드명과 요청 JSON 키 이름 대조 |
| `JwtException: JWT expired` | 토큰 만료 | `/auth/refresh` 로 새 토큰 발급 필요 |
| `@Bean definition overriding` | 같은 타입 Bean 이 두 개 | BCryptPasswordEncoder 등록 위치 확인 |

---

## 7. W2~W4 주간 요약

| 주차 | 이지윤 핵심 작업 |
|------|----------------|
| W2 (5/26~5/29) | Google OAuth 구현, /auth/me 완성, Refresh Rotation 완전 검증, 탈퇴 마스킹 |
| W3 (6/1~6/5) | Gateway AuthFilter 연동 E2E 테스트, 커버리지 80%+ |
| W4 (6/8~6/12) | 시연 dry-run 인증 흐름 지원, 커버리지 70%+ 최종 확인 |
