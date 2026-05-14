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

## 문서 체크리스트 (2026-05-14 v2.0)

- [ ] `DECISIONS.md` 와 충돌하는 값이 없음 (포트/TTL/스택/금지 패턴/팀 배치)
- [ ] 금지 항목 미포함: PostgreSQL / ZooKeeper / Tempo / Anthropic SDK / Claude 고정 코드 / 개역개정 / ESV / NIV
- [ ] **v1에 별도 서비스 모듈 신설 금지** (Modular Monolith, ADR-0001) — `auth-service`/`journal-service`/`ai-service`/`bible-service` 독립 모듈 신설 X. 모두 `qtai-server`의 도메인 패키지로
- [ ] **v1 Kafka 코드 생성 금지** (ADR-0001·0004·0007) — 도메인 간 통신은 Spring `ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)`
- [ ] **v1 ChromaDB / 벡터 DB / 엘라스틱서치 코드 생성 금지** (ADR-0013) — 출처는 사전 적재 `bible_explanations` row 참조
- [ ] **v1 K8s 매니페스트 / Helm chart 코드 생성 금지** (v2 분리 시 도입) — v1은 Docker Compose
- [ ] **Spring Modulith verifyModuleBoundaries() 통과 + ArchUnit 룰 통과** (ADR-0015) — 다른 도메인 패키지 직접 import 0건
- [ ] AI SSE 경로는 `/ai/sessions/{id}/turns` 사용 (`/messages` 아님)
- [ ] SSE 응답 필드는 `sources` 사용 (구 `rag_sources`, 2026-05-14 리네이밍)
- [ ] 해설 API 경로는 `/api/v1/explanations/commentary/*` (구 `/api/v1/commentary/*`)
- [ ] DB 테이블 `bible_explanations` (구 `COMMENTARIES`)
- [ ] 도메인 이벤트 envelope는 `data` 키 사용 (`payload` 아님)
- [ ] 오늘 QT MVP는 하루 1구절 (`verseStart == verseEnd`)
- [ ] Journal 생성은 `POST /api/v1/journals/today` (자유 본문 `POST /api/v1/journals` 미사용)
- [ ] 평문 Secret / API Key 노출 없음 (v1은 `.env` / OS env, v2 K8s Secret)
- [ ] 성경 데이터: KJV + 개역한글만. 새번역은 라이선스 확인 전까지 사용 금지 (pending)
- [ ] QT 본문 소싱: 좌표 메타데이터만 최소 수집 (본문 텍스트는 자체 DB)

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
