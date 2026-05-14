## 변경 요약

<!-- 이 PR이 무엇을 바꾸는지 한두 문장으로 설명. 자동 생성 PR이라면 어떤 트리거(스크립트/스케줄/일정표 갱신 등)로 만들어졌는지 함께 적기. -->

## 관련 이슈 / 회의

<!-- 예: Closes #00, Refs DECISIONS.md, 2026-05-13 오전 회의 결과 반영 -->

## 변경 유형

- [ ] 개발자별 일정표 (11_개발자별_일정표/*)
- [ ] 결정값 / DECISIONS.md
- [ ] 아키텍처 / ADR (docs/adr/*)
- [ ] OpenAPI 명세 (apis/*/openapi.yaml)
- [ ] ERD / 도메인 모델
- [ ] Kafka 이벤트 스키마 (events/schema/*)
- [ ] 운영 / DevOps 가이드
- [ ] 일반 문서 (README, 가이드 등)
- [ ] CI / 워크플로 (.github/workflows/*)

## 변경 대상

<!-- 수정한 주요 파일 경로 나열. 자동 PR인 경우 생성 스크립트가 채워도 됨. -->

- `path/to/file1`
- `path/to/file2`

## 문서 체크리스트

- [ ] `DECISIONS.md` 와 충돌하는 값이 없음 (포트/TTL/스택/금지 패턴)
- [ ] 금지 항목 미포함: PostgreSQL / ZooKeeper / Tempo / Anthropic SDK / Claude 고정 코드 / 개역개정 / ESV / NIV
- [ ] AI SSE 경로는 `/ai/sessions/{id}/turns` 사용 (`/messages` 아님)
- [ ] Kafka envelope는 `data` 키 사용 (`payload` 아님)
- [ ] 인증은 Gateway Auth, 묵상일지는 Bible Service 내부 도메인 — 독립 `auth-service` / `journal-service` 신설 문구 없음
- [ ] 오늘 QT MVP는 하루 1구절 (`verseStart == verseEnd`)
- [ ] Journal 생성은 `POST /api/v1/journals/today` (자유 본문 `POST /api/v1/journals` 미사용)
- [ ] 평문 Secret / API Key 노출 없음

## 일정표 PR 추가 체크

<!-- 11_개발자별_일정표 외 PR이면 삭제 -->

- [ ] 본인(또는 자동화 대상자) 파일만 수정 (다른 팀원 일정표 미수정)
- [ ] 기준일·기준 결정 라인 갱신
- [ ] 마일스톤(W0~발표 2026-06-17) 범위 이탈 없음
- [ ] HTML / MD 양쪽 파일이 동기화됨 (한쪽만 갱신되지 않았는지)

## 리뷰 요청

<!-- 영향받는 팀원 / 리뷰어 멘션. CODEOWNERS가 자동 지정해도 추가 컨텍스트가 필요하면 명시. -->

- 리뷰어: @Tae0072
- 영향 팀원:

## 비고 / 스크린샷 (선택)

<!-- 회의 캡처, 일정 다이어그램, 자동화 로그 등 필요한 경우 첨부. -->
