package com.qtai.authservice.api

import com.qtai.authservice.api.dto.*
import com.qtai.authservice.usecase.GetMeUseCase
import com.qtai.authservice.usecase.LoginUseCase
import com.qtai.authservice.usecase.RegisterUseCase
import jakarta.validation.Valid
import org.springframework.http.HttpStatus
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/auth")
class AuthController(
    private val registerUseCase: RegisterUseCase,
    private val loginUseCase: LoginUseCase,
    private val getMeUseCase: GetMeUseCase
) {
    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    fun register(@Valid @RequestBody req: RegisterRequest): RegisterResponse {
        val user = registerUseCase.register(req.email, req.password, req.nickname)
        return RegisterResponse(user.userId, user.email, user.nickname)
    }

    @PostMapping("/login")
    fun login(@Valid @RequestBody req: LoginRequest): LoginResponse {
        val tokens = loginUseCase.login(req.email, req.password)
        return LoginResponse(tokens.accessToken, tokens.refreshToken)
    }

    // Gateway 가 X-User-Id 를 주입함 — 서비스는 헤더만 읽으면 됨
    @GetMapping("/me")
    fun getMe(@RequestHeader("X-User-Id") userId: Long): MeResponse {
        val user = getMeUseCase.getMe(userId)
        return MeResponse(user.userId, user.email, user.nickname, user.provider.name)
    }
}
