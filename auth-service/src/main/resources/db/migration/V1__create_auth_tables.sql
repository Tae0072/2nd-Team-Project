-- V1__create_auth_tables.sql
-- H2 (MODE=MySQL) + MySQL 8 양쪽 호환
-- ON UPDATE 제거 (H2 미지원) -> JPA @PreUpdate 로 처리
CREATE TABLE IF NOT EXISTS users (
    user_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    email      VARCHAR(255) NOT NULL,
    password   VARCHAR(255),
    nickname   VARCHAR(50)  NOT NULL,
    provider   VARCHAR(10)  NOT NULL DEFAULT 'LOCAL',
    is_active  BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT uq_users_email UNIQUE (email)
);

CREATE TABLE IF NOT EXISTS refresh_tokens (
    token_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id    BIGINT NOT NULL,
    token      VARCHAR(512) NOT NULL,
    expires_at DATETIME(6) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT uq_refresh_token UNIQUE (token),
    CONSTRAINT fk_refresh_user FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);