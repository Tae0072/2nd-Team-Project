package com.qtai.authservice.usecase

import com.qtai.authservice.domain.user.entity.User
import com.qtai.authservice.domain.user.repository.UserRepository
import org.junit.jupiter.api.Assertions.*
import org.junit.jupiter.api.Test
import org.mockito.kotlin.*
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder

class RegisterUseCaseTest {

    private val repo: UserRepository = mock()
    private val encoder = BCryptPasswordEncoder(4)   // strength 4 = 테스트 속도 최적화
    private val useCase = RegisterUseCase(repo, encoder)

    @Test
    fun `정상 회원가입 시 저장 호출`() {
        whenever(repo.existsByEmail("test@qtai.app")).thenReturn(false)
        whenever(repo.save(any())).thenAnswer { it.arguments[0] as User }

        val result = useCase.register("test@qtai.app", "password123", "테스터")

        verify(repo).save(any())
        assertEquals("test@qtai.app", result.email)
        assertEquals("테스터", result.nickname)
        // 비밀번호는 해싱되어 저장 — 평문이 아닌지 확인
        assertNotEquals("password123", result.password)
        assertTrue(encoder.matches("password123", result.password))
    }

    @Test
    fun `중복 이메일이면 IllegalArgumentException`() {
        whenever(repo.existsByEmail("dup@qtai.app")).thenReturn(true)

        val ex = assertThrows(IllegalArgumentException::class.java) {
            useCase.register("dup@qtai.app", "password123", "중복")
        }
        assertEquals("EMAIL_ALREADY_EXISTS", ex.message)
    }
}
