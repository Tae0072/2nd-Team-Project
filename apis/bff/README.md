# BFF OpenAPI 기준

이 디렉터리는 Flutter 앱과 관리자 화면이 호출하는 BFF 외부 공개 API 계약을 보관한다.

- 기준 파일: `openapi.yaml`
- 허용 범위: `/api/v1/**`
- 금지 범위: 사용자 AI Q&A, SSE, `/ai/sessions/**`, 교회 인증 API
- 내부 Java Interface는 이 디렉터리에 작성하지 않는다.
