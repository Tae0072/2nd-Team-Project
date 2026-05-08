package com.qtai.authservice.usecase

import com.qtai.authservice.domain.user.entity.User
import com.qtai.authservice.domain.user.repository.UserRepository
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional

@Service
class GetMeUseCase(private val userRepository: UserRepository) {

    @Transactional(readOnly = true)
    fun getMe(userId: Long): User =
        userRepository.findById(userId)
            .filter { it.isActive }
            .orElseThrow { NoSuchElementException("USER_NOT_FOUND") }
}
