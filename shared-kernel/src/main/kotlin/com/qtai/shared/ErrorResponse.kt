package com.qtai.shared.dto

data class ErrorResponse(
    val code: String,
    val message: String,
    val traceId: String? = null,
    val details: List<FieldError>? = null
) {
    data class FieldError(
        val field: String,
        val message: String
    )
}