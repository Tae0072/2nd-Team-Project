package com.qtai.authservice.api

import com.fasterxml.jackson.databind.ObjectMapper
import com.qtai.authservice.api.dto.LoginRequest
import com.qtai.authservice.api.dto.RegisterRequest
import com.qtai.authservice.domain.user.repository.UserRepository
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.whenever
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.mock.mockito.MockBean
import org.springframework.data.redis.core.StringRedisTemplate
import org.springframework.data.redis.core.ValueOperations
import org.springframework.http.MediaType
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.get
import org.springframework.test.web.servlet.post

@SpringBootTest
@AutoConfigureMockMvc
class AuthControllerSliceTest {

    @Autowired lateinit var mockMvc: MockMvc
    @Autowired lateinit var objectMapper: ObjectMapper
    @Autowired lateinit var userRepository: UserRepository

    // @MockBean: Spring Boot 자동 구성된 Redis 빈을 완전히 대체
    @MockBean lateinit var redisTemplate: StringRedisTemplate

    @BeforeEach
    fun setup() {
        userRepository.deleteAll()

        // Redis ValueOperations mock 설정
        val ops: ValueOperations<String, String> = org.mockito.kotlin.mock()
        whenever(redisTemplate.opsForValue()).thenReturn(ops)
        whenever(ops.set(any(), any(), any<Long>(), any())).then { /* no-op */ }
    }

    @Test
    fun `POST auth-register 성공 시 201 반환`() {
        mockMvc.post("/auth/register") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(
                RegisterRequest("slice@qtai.app", "password123", "슬라이스")
            )
        }.andExpect {
            status { isCreated() }
            jsonPath("$.userId") { isNumber() }
            jsonPath("$.email") { value("slice@qtai.app") }
        }
    }

    @Test
    fun `POST auth-register 중복 이메일이면 400`() {
        val req = RegisterRequest("dup@qtai.app", "password123", "중복")
        // 첫 번째 성공
        mockMvc.post("/auth/register") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(req)
        }.andExpect { status { isCreated() } }

        // 두 번째 중복
        mockMvc.post("/auth/register") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(req)
        }.andExpect { status { isBadRequest() } }
    }

    @Test
    fun `POST auth-login 성공 시 accessToken 반환`() {
        // 먼저 회원가입
        mockMvc.post("/auth/register") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(
                RegisterRequest("login@qtai.app", "password123", "로그인테스터")
            )
        }.andExpect { status { isCreated() } }

        // 로그인
        mockMvc.post("/auth/login") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(
                LoginRequest("login@qtai.app", "password123")
            )
        }.andExpect {
            status { isOk() }
            jsonPath("$.accessToken") { isString() }
            jsonPath("$.tokenType") { value("Bearer") }
        }
    }

    @Test
    fun `POST auth-login 잘못된 비밀번호이면 400`() {
        mockMvc.post("/auth/register") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(
                RegisterRequest("bad@qtai.app", "password123", "틀린비번")
            )
        }
        mockMvc.post("/auth/login") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(
                LoginRequest("bad@qtai.app", "wrongpassword")
            )
        }.andExpect { status { isBadRequest() } }
    }

    @Test
    fun `GET auth-me X-User-Id 헤더로 사용자 조회`() {
        val result = mockMvc.post("/auth/register") {
            contentType = MediaType.APPLICATION_JSON
            content = objectMapper.writeValueAsString(
                RegisterRequest("me@qtai.app", "password123", "미테스터")
            )
        }.andReturn()

        val userId = objectMapper.readTree(result.response.contentAsString)["userId"].asLong()

        mockMvc.get("/auth/me") {
            header("X-User-Id", userId)
        }.andExpect {
            status { isOk() }
            jsonPath("$.email") { value("me@qtai.app") }
            jsonPath("$.nickname") { value("미테스터") }
        }
    }
}
