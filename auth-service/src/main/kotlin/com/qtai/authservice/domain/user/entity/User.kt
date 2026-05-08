package com.qtai.authservice.domain.user.entity

import jakarta.persistence.*
import java.time.LocalDateTime

@Entity
@Table(
    name = "users",
    uniqueConstraints = [UniqueConstraint(columnNames = ["email"])]
)
class User(
    @Column(nullable = false, length = 255)
    var email: String,

    @Column(length = 255)
    var password: String? = null,

    @Column(nullable = false, length = 50)
    var nickname: String,

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, length = 10)
    val provider: Provider = Provider.LOCAL,

    @Column(nullable = false)
    var isActive: Boolean = true,

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    val userId: Long = 0,

    @Column(nullable = false, updatable = false)
    val createdAt: LocalDateTime = LocalDateTime.now(),

    @Column(nullable = false)
    var updatedAt: LocalDateTime = LocalDateTime.now()
) {
    enum class Provider { LOCAL, GOOGLE }

    // ON UPDATE 트리거 대신 JPA 레벨에서 처리
    @PreUpdate
    fun onUpdate() { updatedAt = LocalDateTime.now() }

    fun deactivate() {
        isActive = false
        updatedAt = LocalDateTime.now()
    }
}