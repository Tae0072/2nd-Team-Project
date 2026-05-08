package com.qtai.authservice.usecase

import com.qtai.authservice.domain.user.entity.User
import com.qtai.authservice.domain.user.repository.UserRepository
import com.qtai.authservice.infrastructure.jwt.JwtProvider
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.kotlin.*
import org.springframework.data.redis.core.StringRedisTemplate
import org.springframework.data.redis.core.ValueOperations
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import java.util.Optional

class LoginUseCaseTest {

    private val repo: UserRepository = mock()
    private val encoder = BCryptPasswordEncoder(4)
    private val jwtProvider: JwtProvider = mock()
    private val redisOps: ValueOperations<String, String> = mock()
    private val redis: StringRedisTemplate = mock {
        on { opsForValue() } doReturn redisOps
    }
    private val useCase = LoginUseCase(repo, encoder, jwtProvider, redis)

    private fun savedUser(rawPw: String = "password123") = User(
        userId   = 1L,
        email    = "user@qtai.app",
        password = encoder.encode(rawPw),
        nickname = "테스터"
    )

    @Test
    fun `올바른 자격증명이면 토큰 쌍 반환`() {
        val user = savedUser()
        whenever(repo.findByEmail("user@qtai.app")).thenReturn(Optional.of(user))
        whenever(jwtProvider.issueAccessToken(1L)).thenReturn("ACCESS")
        whenever(jwtProvider.issueRefreshToken(1L)).thenReturn("REFRESH")

        val result = useCase.login("user@qtai.app", "password123")

        assertEquals("ACCESS", result.accessToken)
        assertEquals("REFRESH", result.refreshToken)
        verify(redisOps).set(eq("refresh:1"), eq("REFRESH"), any(), any())
    }

    @Test
    fun `존재하지 않는 이메일이면 INVALID_CREDENTIALS`() {
        whenever(repo.findByEmail(any())).thenReturn(Optional.empty())

        val ex = assertThrows(IllegalArgumentException::class.java) {
            useCase.login("nobody@qtai.app", "pw")
        }
        assertEquals("INVALID_CREDENTIALS", ex.message)
    }

    @Test
    fun `비밀번호 불일치이면 INVALID_CREDENTIALS`() {
        whenever(repo.findByEmail("user@qtai.app")).thenReturn(Optional.of(savedUser()))

        val ex = assertThrows(IllegalArgumentException::class.java) {
            useCase.login("user@qtai.app", "wrongpassword")
        }
        assertEquals("INVALID_CREDENTIALS", ex.message)
    }

    @Test
    fun `탈퇴 계정이면 ACCOUNT_DEACTIVATED`() {
        val user = savedUser().also { it.deactivate() }
        whenever(repo.findByEmail("user@qtai.app")).thenReturn(Optional.of(user))

        val ex = assertThrows(IllegalArgumentException::class.java) {
            useCase.login("user@qtai.app", "password123")
        }
        assertEquals("ACCOUNT_DEACTIVATED", ex.message)
    }
}
