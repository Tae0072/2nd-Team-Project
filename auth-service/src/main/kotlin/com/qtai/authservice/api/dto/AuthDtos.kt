package com.qtai.authservice.api.dto

import jakarta.validation.constraints.Email
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size

data class RegisterRequest(
    @field:Email(message = "이메일 형식이 올바르지 않습니다.")
    @field:NotBlank
    val email: String,

    @field:NotBlank
    @field:Size(min = 8, message = "비밀번호는 8자 이상이어야 합니다.")
    val password: String,

    @field:NotBlank
    @field:Size(max = 50, message = "닉네임은 50자 이하여야 합니다.")
    val nickname: String
)

data class LoginRequest(
    @field:NotBlank val email: String,
    @field:NotBlank val password: String
)

data class RegisterResponse(
    val userId: Long,
    val email: String,
    val nickname: String
)

data class LoginResponse(
    val accessToken: String,
    val refreshToken: String,
    val tokenType: String = "Bearer",
    val expiresIn: Int = 900
)

data class MeResponse(
    val userId: Long,
    val email: String,
    val nickname: String,
    val provider: String
)
