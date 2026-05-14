# ADR-0003: 단일 DB `qtai_db` + 도메인별 테이블 prefix

## 상태
Accepted (2026-05-14 — Modular Monolith 결정과 연계해 기존 "Database per Service"를 본 ADR로 갈아엎음)

## 날짜
2026-05-14

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
2026-05-13까지 본 ADR은 "4 schema(auth_db, bible_db, ai_db, journal_db) — 단일 MySQL instance에 schema 단위 격리"였다. ADR-0001에서 v1 배포 단위가 Modular Monolith 하나로 결정되면서 DB도 단일 schema로 통합한다. 1차 HMS의 실패 원인이 schema 공유 자체가 아니라 도메인 경계가 코드에서 깨졌기 때문이었음을 인정한다. 경계는 코드(패키지 import 금지)와 테이블 prefix로 유지한다.

## Decision
**단일 MySQL DB `qtai_db` + 도메인별 테이블 prefix.**

| 도메인 | 테이블 prefix | 주요 테이블 |
| --- | --- | --- |
| Gateway Auth | `auth_` | `auth_users`, `auth_refresh_tokens`, `auth_oauth_links` |
| Bible | `bible_` | `bible_books`, `bible_kr_verses`, `bible_en_verses`, `bible_explanations`(구 commentaries) |
| AI | `ai_` | `ai_sessions`, `ai_turns`, `ai_prompt_templates` |
| Journal | `journal_` | `journal_journals`, `journal_events`, `journal_inbox_keys`, `journal_shares`, `journal_share_likes`, `journal_share_comments`, `journal_share_reports` |

### 규칙

1. **다른 도메인 prefix 테이블 직접 JOIN 금지.** Repository는 자기 도메인 prefix만 다룬다.
2. **다른 도메인 데이터가 필요하면 도메인 Interface 호출 또는 in-process 이벤트로 받는다** (ADR-0001 도메인 경계 절대 규칙 2·3).
3. **Flyway migration은 도메인별 하위 디렉토리로 격리.** `src/main/resources/db/migration/{auth,bible,ai,journal}/V1__init.sql`.
4. **단일 application DB user.** schema 단위 GRANT는 v2 분리 시 도입.

## Alternatives
- **4 schema 분리 (이전 결정)**: Modular Monolith와 정합 안 맞음. v2 분리 시 다시 사용.
- **물리적 다중 instance**: 운영 부담 과도. v2까지 보류.
- **NoSQL 혼합**: 학습 곡선·일정 부담. 통일성 우선.

## Consequences
**긍정:**
- 단일 SpringBootTest 컨텍스트 + 단일 Testcontainers MySQL로 통합 테스트 단순화.
- 백업·복구 단위가 하나라 운영 부담 감소.
- v2 분리 시 prefix별 테이블을 그대로 schema로 이전 가능.

**부정:**
- 도메인 경계가 코드 검증 스크립트에 의존 (DB가 강제하지 못함).
- 테이블 수가 한 schema에 누적되어 권한·통계 관리 복잡도 증가.
- 02_ERD 문서의 schema 분리 다이어그램·예제 SQL 동시 갱신 필요.

## 검증 방법
W1 Lock-in 5/22까지:
1. Flyway migration이 `qtai_db` 단일 schema에 모두 적용.
2. 도메인별 Repository가 자기 prefix 외 테이블을 참조하지 않음 (검증 스크립트로 SELECT 대상 prefix 추적).
3. 다른 도메인 JOIN을 시도한 PR은 ADR-0001 검증 스크립트에서 reject.

## 슈퍼시드 이력
- 2026-05-13 v1: "Database per Service — 4 schema 격리" (Accepted)
- **2026-05-14 v2: 단일 DB `qtai_db` + 도메인 prefix로 본문 갈아엎음 (현재)**
