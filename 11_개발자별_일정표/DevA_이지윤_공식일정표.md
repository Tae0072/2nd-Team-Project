# 📋 QT-AI — Dev A (이지윤) 상세 일정표

문서 버전: v1.0
작성일: 2026-05-08
담당자: 이지윤
역할: Auth Service Owner
담당 서비스: Auth/User Service — JWT RS256·OAuth·회원·Refresh Rotation
개발 기간: W1(5/12) ~ W5(6/17)
연관 문서: 00_개발_일정_총괄표 / 02_ERD_문서 v1.3 / 04_API_명세서 v1.5 / 05_보안_명세서 v1.0

---

## 0. 역할 핵심 선언

> **"인증이 흔들리면 전체 시스템이 흔들린다."**
> Auth Service가 W1에 안정화되어야 Gateway AuthFilter가 JWT를 검증할 수 있고,
> 나머지 4개 서비스가 `X-User-Id` 헤더를 전제로 개발을 시작할 수 있다.
> JWT 키쌍·Refresh Rotation 정책은 한번 확정되면 변경 시 전원 공지 필수.

### 공통 PR 완료 조건

> 모든 코드 PR은 테스트 코드 작성 후 단위 테스트와 통합 테스트가 모두 통과해야 완료로 인정한다.

- [ ] 변경 범위 테스트 코드 작성 완료 (문서-only PR은 사유 명시)
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] PR 본문에 테스트 명령과 통과 결과 첨부
- [ ] 미충족 시 Draft 유지, 머지 금지

---

## 1. 소유권 선언

```
auth-service/
  └── src/main/kotlin/com/qtai/authservice/
      ├── domain/
      │   ├── user/entity/User.java           ← 전담 소유
      │   ├── user/entity/RefreshToken.java
      │   ├── user/entity/OAuthLink.java
      │   └── user/repository/
      ├── usecase/
      │   ├── LoginUseCase.java               ← 전담 소유
      │   ├── RegisterUseCase.java
      │   ├── RefreshTokenUseCase.java
      │   └── OAuthUseCase.java
      ├── infrastructure/
      │   ├── jwt/JwtProvider.java            ← 강태오와 공동 설계, 이지윤 구현
      │   └── redis/RefreshTokenRepository.java
      └── api/
          └── AuthController.java
  └── src/main/resources/
      ├── db/migration/V1__create_auth_tables.sql
      └── application.yml

Gateway AuthFilter에 제공하는 공개 인터페이스:
  - RS256 공개키 (K8s Secret으로 Gateway에 공유)
  - 토큰 형식: Authorization: Bearer {JWT}
  - X-User-Id 헤더: userId (BIGINT) — Gateway가 주입
```

---

## 2. Auth Service 핵심 기술 요구사항

| 요구사항 | 구현 방식 | 완료 목표 | 왜 중요한가 |
|---------|-----------|-----------|-------------|
| JWT RS256 발급 | `java.security.KeyPairGenerator` RSA-2048 | W1 화 | 공개키로 Gateway 검증 |
| Refresh Token Rotation | 재발급 시 기존 토큰 Redis blacklist 등록 | W1 수 | 탈취 방지 |
| bcrypt 해싱 | `BCryptPasswordEncoder(strength=12)` | W1 화 | 평문 저장 방지 (HMS 실패 재발 금지) |
| Google OAuth | Spring Security OAuth2 Client + JWK | W2 수 | 03번 ADR-0002 |
| 이메일 재가입 마스킹 | 탈퇴 후 `u***@***.com` soft delete | W2 목 | ADR-0010 |
| Flyway 마이그레이션 | `V1__create_auth_tables.sql` | W1 월 | DB 스키마 버전 관리 |

---

## 3. 일별 상세 일정

### 🟩 W1 — Auth Service 골격 구축 (5/12~5/22)

| 일자 | 오전 | 오후 코어 | 저녁 |
|------|------|-----------|------|
| 5/12 화 | 킥오프 참석. git pull. 환경 확인 | `auth-service/` 패키지 구조 생성. Flyway V1 SQL (USERS·REFRESH_TOKENS·OAUTH_LINKS) | User 엔티티 기본 필드 |
| 5/13 화 | Stand-up | `LoginUseCase` 골격 + bcrypt 비밀번호 인코딩 구현 | JWT RS256 키쌍 생성 (`JwtProvider.java`) |
| 5/14 수 | Stand-up | `RegisterUseCase` + 이메일 중복 검증 | `RefreshTokenUseCase` — Rotation 정책 구현 |
| 5/15 목 | Stand-up | `AuthController` — `/auth/login`, `/auth/register`, `/auth/refresh` | Redis blacklist 연동 (`RefreshTokenRepository`) |
| 5/16 금 | Stand-up | 단위 테스트 — `LoginUseCase`, `RegisterUseCase` (Mockito) | 1차 `/auth/login` → JWT 발급 curl 테스트 |
| 5/19 월 | Stand-up | `/auth/logout` POST 구현 + Redis blacklist 등록 | `/auth/me` GET 구현 |
| 5/20 화 | Stand-up | `AuthController` 전체 엔드포인트 통합 테스트 (@SpringBootTest) | Gateway AuthFilter 연동 테스트 (강태오 협력) |
| 5/21 수 | Stand-up | POST `/auth/me/deactivate` soft delete + 이메일 마스킹 | Repository 테스트 (@DataJpaTest) |
| 5/22 목 | Stand-up | W1 체크리스트 최종 확인. PR 정리. | **W1 Lock-in 게이트 참석 (18:00)** |

**W1 완료 기준**
- [ ] `/auth/login` → JWT Access + Refresh 토큰 발급
- [ ] `/auth/refresh` → Rotation (기존 블랙리스트 등록 확인)
- [ ] `/auth/me` → X-User-Id 헤더로 사용자 조회
- [ ] Flyway V1 마이그레이션 성공
- [ ] LoginUseCase 단위 테스트 통과

---

### 🟨 W2 — Google OAuth + 완성도 (5/26~5/29)

| 일자 | 주요 작업 |
|------|-----------|
| 5/26 화 | 페이스 점검 (11:30). Google OAuth redirect 엔드포인트 구현 |
| 5/27 수 | OAuth callback — JWK 직접 검증 + JWT 발급 |
| 5/28 목 | `OAuthLink` 엔티티 + 기존 계정 연결 로직. 탈퇴 마스킹 완성 |
| 5/29 금 | Service 커버리지 60%+ 확인. W2 PR 정리 |

---

### 🟧 W3 (6/1~6/5) + 🟥 W4 (6/8~6/12)

| 주차 | 주요 작업 |
|------|-----------|
| W3 | 통합 테스트 — Gateway AuthFilter ↔ Auth Service E2E. 감사 로그 Logback 마스킹 확인 |
| W4 | 회귀 테스트. 시연 시나리오 인증 흐름 dry-run 지원. 커버리지 70%+ |

---

## 4. AI 에이전트 활용 가이드

| 단계 | Claude 활용처 | 주의사항 |
|------|--------------|----------|
| W1 | Flyway SQL 초안, JWT 코드 골격 생성 | RS256 키 생성 로직은 직접 검증 필수 |
| W2 | OAuth2 Spring Security 설정 코드 | JWK endpoint URL 직접 확인 |
| W3 | 단위 테스트 케이스 생성 | 실패 케이스 1개 이상 포함 강제 |
| 전체 | 보안 관련 코드는 Claude 생성 후 05번 보안 명세서와 대조 | JWT 시크릿 Claude에 입력 금지 |
