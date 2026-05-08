package com.qtai.authservice.api

import org.springframework.http.HttpStatus
import org.springframework.http.ProblemDetail
import org.springframework.validation.FieldError
import org.springframework.web.bind.MethodArgumentNotValidException
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice
import java.net.URI

@RestControllerAdvice
class GlobalExceptionHandler {

    @ExceptionHandler(IllegalArgumentException::class)
    fun handleIllegalArgument(ex: IllegalArgumentException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, ex.message ?: "BAD_REQUEST")
            .also { it.type = URI.create("https://api.qtai.app/errors/bad-request") }

    @ExceptionHandler(NoSuchElementException::class)
    fun handleNotFound(ex: NoSuchElementException): ProblemDetail =
        ProblemDetail.forStatusAndDetail(HttpStatus.NOT_FOUND, ex.message ?: "NOT_FOUND")
            .also { it.type = URI.create("https://api.qtai.app/errors/not-found") }

    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun handleValidation(ex: MethodArgumentNotValidException): ProblemDetail {
        val fields = ex.bindingResult.allErrors
            .filterIsInstance<FieldError>()
            .associate { it.field to it.defaultMessage }
        return ProblemDetail.forStatusAndDetail(HttpStatus.UNPROCESSABLE_ENTITY, "VALIDATION_FAILED")
            .also {
                it.type = URI.create("https://api.qtai.app/errors/validation-failed")
                it.setProperty("fields", fields)
            }
    }
}
