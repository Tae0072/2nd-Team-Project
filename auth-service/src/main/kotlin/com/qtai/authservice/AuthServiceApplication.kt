package com.qtai.authservice

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.runApplication
import org.springframework.context.annotation.Bean
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder

@SpringBootApplication
class AuthServiceApplication {
    @Bean
    fun passwordEncoder() = BCryptPasswordEncoder(12)
}

fun main(args: Array<String>) {
    runApplication<AuthServiceApplication>(*args)
}
