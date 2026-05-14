# apis/journal/openapi.yaml — DEPRECATED (2026-05-12, 2026-05-14 재확정)

본 디렉토리의 OpenAPI는 사용하지 않습니다.

- **2026-05-12 결정:** Journal Service 독립 서비스 제거. 묵상일지 기능 Bible Service로 통합.
- **2026-05-14 결정:** Modular Monolith 전환에 따라 Journal 기능은 `com.qtai.journal` 도메인 패키지로 통합. API 계약은 `apis/bible/openapi.yaml`에 포함 (`/api/v1/journals/...`, `/api/v1/shares/...`).

`apis/journal/openapi.yaml`은 v2 분리 시 재개될 가능성이 있으므로 본문은 보존하되, **코드 생성·테스트·CI 검증 대상에서 제외**합니다.

참조: DECISIONS.md §3, AGENTS.md 도메인 패키지 표, ADR-0001 Modular Monolith.
