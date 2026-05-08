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
    @Transactional
    fun register(email: String, rawPassword: String, nickname: String): User {
        if (userRepository.existsByEmail(email)) {
            throw IllegalArgumentException("EMAIL_ALREADY_EXISTS")
        }
        return userRepository.save(
            User(
                email    = email,
                password = passwordEncoder.encode(rawPassword),
                nickname = nickname
            )
        )
    }
}
