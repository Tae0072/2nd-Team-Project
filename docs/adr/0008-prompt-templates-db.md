# ADR-0008: AI system prompt는 DB(PROMPT_TEMPLATES)에 보관

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
1차 HMS는 prompt를 코드에 하드코딩 → 변경 시 재배포 필요. AI 도메인은 prompt 튜닝이 곧 품질 — 자주 변경되는데 매번 배포는 부담. 또한 신학 가드레일이라는 도메인 특수성 때문에 검토 절차가 필요 (강상민 owner — 09번 작성 예정).

## Decision
**PROMPT_TEMPLATES 테이블에 system prompt 저장** (02번 § 10):

\\\sql
CREATE TABLE PROMPT_TEMPLATES (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  step CHAR(1) NOT NULL,                  -- A, B, C, D
  version INT NOT NULL,
  system_prompt TEXT NOT NULL,
  is_active TINYINT(1) NOT NULL DEFAULT 0,
  rag_retrieval_strategy VARCHAR(50),
  created_at DATETIME(6) NOT NULL,
  created_by_user_id BIGINT NOT NULL,
  approved_at DATETIME(6),
  approved_by_user_id BIGINT
);
\\\

- AI Service 시작 시 \is_active=1\ 행을 메모리에 캐시 (TTL 5min)
- 새 prompt는 \is_active=0\으로 INSERT → 검토 후 \is_active=1\ UPDATE
- 동일 step에 \is_active=1\ 행은 1개만 (UNIQUE partial index 또는 application 검증)

## Alternatives
- **코드 하드코딩**: 1차 패턴 그대로
- **외부 prompt 관리 SaaS (예: PromptLayer, LangSmith)**: 외부 의존성·비용·시연 6주 무리
- **K8s ConfigMap에 prompt**: 변경 시 Pod 재시작 필요

## Consequences
**긍정:**
- prompt 변경에 재배포 불필요 (운영자가 DB 직접 변경 또는 v1.1 admin endpoint)
- 검토 절차 (created_by + approved_by) → 신학 가드레일
- 버전 history 보존 (롤백 가능)

**부정:**
- 캐시 stale 위험 (TTL 5min — 한 번에 모든 Pod 동기화 X)
- DB read 의존도 ↑ (시작 시 + TTL 갱신)
- 관리자 endpoint·UI 작성 부담 (v1.1 검토)

## 검증 방법
W1 통합 테스트: 새 prompt INSERT → AI Service TTL 만료 후 새 prompt 적용 확인