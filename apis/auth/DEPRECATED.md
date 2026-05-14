# apis/auth/openapi.yaml — DEPRECATED (2026-05-12, 2026-05-14 재확정)

본 디렉토리의 OpenAPI는 사용하지 않습니다.

- **2026-05-12 결정:** Auth Service 독립 서비스 제거. JWT 발급·검증은 Gateway Auth 모듈에서 처리.
- **2026-05-14 결정:** Modular Monolith 전환에 따라 Auth 기능은 `com.qtai.gatewayauth` 도메인 패키지로 통합. API 계약은 `apis/bff/openapi.yaml` 또는 별도 분리 없이 단일 서비스에서 서빙.

`apis/auth/openapi.yaml`은 v2 분리 시 재개될 가능성이 있으므로 본문은 보존하되, **코드 생성·테스트·CI 검증 대상에서 제외**합니다.

참조: DECISIONS.md §0·§1, AGENTS.md 도메인 패키지 표, ADR-0001 Modular Monolith.
