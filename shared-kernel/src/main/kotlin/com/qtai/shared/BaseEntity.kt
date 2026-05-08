package com.qtai.shared.domain

import java.time.LocalDateTime

/**
 * 공통 감사 필드 — JPA 어노테이션은 각 서비스 모듈에서 상속 시 적용.
 * shared-kernel은 JPA 의존성 없이 유지.
 */
abstract class BaseEntity {
    var createdAt: LocalDateTime = LocalDateTime.now()
    var updatedAt: LocalDateTime = LocalDateTime.now()
}