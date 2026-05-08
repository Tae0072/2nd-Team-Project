package com.qtai.authservice.usecase

import com.qtai.authservice.domain.user.repository.UserRepository
import com.qtai.authservice.infrastructure.jwt.JwtProvider
import org.springframework.data.redis.core.StringRedisTemplate
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder
import org.springframework.stereotype.Service
import java.util.concurrent.TimeUnit

data class TokenPair(val accessToken: String, val refreshToken: String)

@Service
class LoginUseCase(
    private val userRepository: UserRepository,
    private val passwordEncoder: BCryptPasswordEncoder,
    private val jwtProvider: JwtProvider,
    private val redisTemplate: StringRedisTemplate
) {
    fun login(email: String, rawPassword: String): TokenPair {
        val user = userRepository.findByEmail(email)
            .orElseThrow { IllegalArgumentException("INVALID_CREDENTIALS") }

        if (!user.isActive)
            throw IllegalArgumentException("ACCOUNT_DEACTIVATED")

        if (!passwordEncoder.matches(rawPassword, user.password))
            throw IllegalArgumentException("INVALID_CREDENTIALS")

        val accessToken  = jwtProvider.issueAccessToken(user.userId)
        val refreshToken = jwtProvider.issueRefreshToken(user.userId)

        // Refresh Token Redis 저장 (7일 TTL)
        redisTemplate.opsForValue()
            .set("refresh:${user.userId}", refreshToken, 7, TimeUnit.DAYS)

        return TokenPair(accessToken, refreshToken)
    }
}
