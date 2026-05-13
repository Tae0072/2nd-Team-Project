# QT-AI (큐티 AI 앱) — 팀 협업 규칙·Git 브랜치 전략 v1.2

> **문서 버전:** v1.1
> **작성일:** 2026-05-08
> **수정일:** 2026-05-12
> **연관 문서:** [01_프로젝트_계획서 v1.4](./01_프로젝트_계획서.md) / [11_개발_환경_셋업_가이드 v1.0](./11_개발_환경_셋업_가이드.md)
> **owner:** 강태오 (Lead — 규칙 정의 + 강제)
> **목적:** 6명이 6주 동안 충돌 없이 협업. Git 충돌·빌드 깨짐·리뷰 없는 머지로 인한 시간 낭비 원천 방지.

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-08 | 강태오 (Lead) | 초기 작성 — Git 전략·PR 룰·커밋 메시지·코드 리뷰·회의 규칙 |
| v1.1 | 2026-05-12 | 강태오 (Lead) | `develop` → `dev` 브랜치 변경 / Claude 자동 리뷰·자동 머지 시스템 반영 |
| v1.2 | 2026-05-13 | 강태오 (Lead) | PR 테스트 필수 조건 강화 (단위/통합 테스트 미작성 시 REQUEST_CHANGES) / PR 템플릿 dev 브랜치 실제본 동기화 / Claude 리뷰 기준 8가지로 확장 |

---

## 목차

1. [Git 브랜치 전략](#1-git-브랜치-전략)
2. [커밋 메시지 규칙](#2-커밋-메시지-규칙)
3. [PR (Pull Request) 규칙](#3-pr-pull-request-규칙)
4. [코드 리뷰 기준](#4-코드-리뷰-기준)
5. [회의 규칙·스탠드업](#5-회의-규칙스탠드업)
6. [Slack 채널 운영](#6-slack-채널-운영)
7. [긴급 상황 대응](#7-긴급-상황-대응)

---

## 1. Git 브랜치 전략

### 1.1 브랜치 구조

```
master        ← 최종 배포 브랜치 (Lead 강태오 수동 머지만)
  └── dev     ← 통합 브랜치 (팀원 PR 대상 — Claude 자동 리뷰 + 자동 머지)
        ├── feature/auth-oauth-google  ← 기능 개발
        ├── feature/bible-today-api
        ├── bugfix/ai-sse-timeout      ← 버그 수정
        ├── docs/update-api-spec       ← 문서 수정
        └── refactor/gateway-filter    ← 리팩토링
```

> **브랜치 역할 요약**
> - `dev`: 팀원 PR 자동 머지 대상. Claude 리뷰 통과 + CI 통과 시 squash merge 자동 진행.
> - `master`: Lead가 dev → master PR을 직접 검토 후 수동 머지 (배포 단위).

### 1.2 브랜치 명명 규칙

```
{type}/{서비스}-{짧은-설명}
```

**서비스 scope (담당 디렉토리):**

| scope | 담당자 | 디렉토리 |
| --- | --- | --- |
| `gateway` | 강태오 | `services/gateway/` |
| `bff` | 강태오 | `services/bff-aggregator/` |
| `auth` | 이지윤 | `services/auth-service/` |
| `bible` | 김태혁 | `services/bible-service/` |
| `ai` | 강상민 | `services/ai-service/` |
| `journal` | 이승욱 | `services/journal-service/` |
| `mobile` | 김지민 | `apps/mobile/` |

**예시:**
```bash
git checkout dev
git checkout -b feature/auth-google-oauth
git checkout -b bugfix/ai-sse-turn-completed
git checkout -b feature/bible-today-passage-api
```

### 1.3 브랜치 운영 규칙

| 규칙 | 내용 |
| --- | --- |
| master 직접 push 금지 | Lead 전용 — dev→master PR 수동 검토 |
| dev 직접 push 금지 | 모든 작업은 feature/bugfix 브랜치 경유 |
| 타 팀원 모듈 수정 금지 | CODEOWNERS 자동 감지 — Claude가 REQUEST_CHANGES |
| 브랜치 수명 | 최대 3일 (장기 작업은 매일 dev rebase) |
| 완료 브랜치 삭제 | PR 머지 후 원격 브랜치 즉시 삭제 |

### 1.4 daily rebase 습관

```bash
# 매일 작업 시작 시 dev 최신화
git checkout dev
git pull origin dev

# 작업 브랜치로 돌아와 rebase
git checkout feature/my-branch
git rebase dev

# 충돌 해결 후
git rebase --continue
git push --force-with-lease  # 자신의 feature 브랜치에만
```

> **⚠️ merge 대신 rebase 권장** (dev 히스토리 선형 유지). 단, PR 올린 후에는 force push 금지.

---

## 2. 커밋 메시지 규칙

### 2.1 Conventional Commits 형식

```
{type}({scope}): {subject}
```

**type 목록:**
```
feat     새 기능
fix      버그 수정
docs     문서 수정
refactor 리팩토링
test     테스트 추가·수정
chore    빌드·의존성·CI
```

### 2.2 커밋 메시지 예시

```bash
# ✅ 좋은 예
feat(auth): add Google OAuth login with JWK verification
fix(ai): prevent infinite SSE retry on LLM_TIMEOUT
feat(journal): add @TransactionalEventListener AFTER_COMMIT
feat(mobile): implement QT home screen UI

# ❌ 나쁜 예 (Claude가 REQUEST_CHANGES 냄)
git commit -m "수정"
git commit -m "fix bug"
git commit -m "작업중"
```

### 2.3 커밋 단위 원칙

```
✅ 1 커밋 = 1 논리적 변경
✅ 테스트와 구현 같은 커밋 가능
❌ 여러 기능을 1 커밋에 묶기
❌ 빌드 깨지는 커밋 push (feature 브랜치라도)
```

---

## 3. PR (Pull Request) 규칙

### 3.1 PR 자동화 시스템

PR을 `dev`에 올리면 **자동으로** 아래가 실행됩니다:

```
PR 오픈 (base: dev)
  ├── 🔨 QT-AI CI 실행
  │     ├── Spring Boot Build & Test × 6개 서비스
  │     ├── Flutter Test
  │     └── Decisions Guard (PostgreSQL/ZooKeeper/Python/.env 금지 검사)
  │
  └── 🤖 Claude 자동 코드 리뷰 (구독 OAuth)
        ├── APPROVE → CI 완료 대기 → 전체 통과 → squash merge → dev ✅
        └── REQUEST_CHANGES → PR에 리뷰 코멘트 등록, 머지 안 됨 ❌
```

**팀원이 해야 할 것:**
- PR 템플릿 성실하게 작성
- REQUEST_CHANGES 받으면 → 코멘트 확인 → 수정 후 push → 자동 재리뷰

**팀원이 하지 않아도 되는 것:**
- 수동 머지 버튼 클릭 ❌
- 리뷰어 지정 ❌ (CODEOWNERS 자동 처리)

### 3.2 PR 생성 기준

| 항목 | 기준 |
| --- | --- |
| PR 대상 브랜치 | 항상 `dev` (master로 직접 PR 금지) |
| PR 크기 | 변경 파일 10개 이하, 500줄 이하 권장 |
| 자동 CI | GitHub Actions 자동 실행 (실패 시 머지 차단) |
| 자동 리뷰 | Claude 자동 코드 리뷰 |
| 머지 방식 | Squash Merge (자동) |

### 3.3 PR 템플릿 (자동 채워짐)

> 실제 PR 생성 시 [QT-AI-2nd-Team-Project/.github/pull_request_template.md](https://github.com/Tae0072/QT-AI-2nd-Team-Project/blob/dev/.github/pull_request_template.md) 가 자동으로 채워집니다. 아래는 동기화된 사본입니다.

```markdown
## 구현 내용
<!-- 이 PR에서 해결하거나 추가하는 변경 사항을 간략하게 설명하세요. -->

## 관련 이슈 / 타스크
<!-- Closes #000 / Fixes #000 -->

## 변경 유형
- [ ] 기능 추가 (feat)
- [ ] 버그 수정 (fix)
- [ ] 리팩토링 (refactor)
- [ ] 테스트 (test)
- [ ] 문서 (docs)
- [ ] 인프라 / CI (chore)

## 코드 체크리스트
- [ ] `DECISIONS.md` 값과 충돌이 없음
- [ ] PostgreSQL / ZooKeeper / Tempo 코드 없음
- [ ] `application.yml` 또는 코드에 평문 Secret 없음
- [ ] Kafka envelope에 `payload` 키 대신 `data` 사용
- [ ] AI SSE 경로 `/turns` 사용 (`/messages` 아님)
- [ ] 성경 데이터: 개역개정/ESV/NIV 코드 없음
- [ ] `@Transactional` 없는 DB 변경 메서드 없음
- [ ] Kafka 이벤트 발행은 `@TransactionalEventListener(AFTER_COMMIT)`

## 테스트 체크리스트
<!-- feat / fix / refactor 타입은 아래 항목 필수 — 미충족 시 Claude가 REQUEST_CHANGES -->
- [ ] 단위 테스트(Unit Test) 작성 완료 및 `./gradlew test` 로컬 통과
- [ ] 통합 테스트(Integration Test) 작성 완료
      또는 미작성 사유: <!-- 예: 외부 의존성(Google OAuth) 특성상 Mock 처리 -->
- [ ] docs / chore 타입은 해당 없음 (위 항목 무시)

## 테스트 방법
<!-- 어떻게 테스트했는지 설명 (Unit / Integration / 수동) -->
```

### 3.4 PR 라이프사이클

```
① dev 최신화
   git checkout dev && git pull origin dev

② feature 브랜치 생성 (dev 기준)
   git checkout -b feature/auth-google-oauth

③ 코드 작성 + 커밋
   git commit -m "feat(auth): ..."

④ push
   git push -u origin feature/auth-google-oauth

⑤ GitHub에서 PR 오픈 (base: dev 확인 필수!)

⑥ 🤖 Claude 자동 리뷰 + CI (gradle build·test) 병렬 실행 (1~3분)
   - Claude APPROVE + CI (build + `./gradlew test`) 모두 통과 → 자동 squash merge → dev ✅
   - Claude REQUEST_CHANGES → 리뷰 코멘트 확인 → 수정 후 push → 자동 재리뷰 🔄
   - CI 실패 (단위/통합 테스트 실패 포함) → 자동 머지 차단 + PR에 ⛔ 코멘트

⑦ 완료: dev에 자동 머지됨, feature 브랜치 삭제
```

### 3.5 Claude REQUEST_CHANGES 주요 원인

**즉시 반려 (Critical):**
```
❌ 타 팀원 모듈 디렉토리 파일 수정
❌ 하드코딩된 API Key / 비밀번호 발견
❌ ai-service에 Python 파일 (.py) 존재
❌ PostgreSQL JDBC URL (MySQL만 허용)
❌ ZooKeeper 설정 (KRaft만 허용)
```

**경고 후 반려 (수정 필요):**
```
⚠️ DB 쓰기 메서드에 @Transactional 누락
⚠️ 빈 catch 블록 — catch (Exception e) {} 금지
⚠️ javax.* 사용 (Spring Boot 3.x → jakarta.*)
⚠️ Kafka envelope에 payload 키 사용 (data 써야 함)
⚠️ SSE 경로 /messages 사용 (/turns 써야 함)
⚠️ 성경 데이터에 개역개정/ESV/NIV 포함
⚠️ 새 기능(feat) PR에 단위 테스트(Unit Test) 코드 없음
⚠️ 핵심 로직(Service, UseCase) 변경인데 테스트 없음
⚠️ "다음 PR에서 테스트 추가 예정" 사유만 제시 → APPROVE 불가
⚠️ 통합 테스트 미작성인데 PR 본문에 사유 없음
```

### 3.6 긴급 hotfix 절차

```bash
git checkout master
git checkout -b hotfix/critical-bug

git commit -m "hotfix(auth): prevent JWT verification bypass"

# master에 PR → Lead 즉시 수동 검토
# 이후 dev에도 cherry-pick
git checkout dev
git cherry-pick <commit-hash>
git push origin dev
```

---

## 4. 코드 리뷰 기준

### 4.1 Claude 자동 리뷰 기준 (8가지)

| # | 기준 | 주요 체크 |
| --- | --- | --- |
| 1 | 코드 품질 | 가독성, 네이밍, 중복 코드 |
| 2 | 버그 가능성 | NPE, 인덱스 오류, 예외 처리 누락 |
| 3 | 보안 | 하드코딩된 시크릿, SQL Injection, 권한 검증 |
| 4 | Spring Boot 3.x 호환성 | deprecated API 사용 여부 |
| 5 | 트랜잭션 | @Transactional 누락, 범위 오류 |
| 6 | MSA | Kafka 이벤트 페어, API 타임아웃, 서비스 의존성 |
| 7 | 도메인 로직 | 성경 묵상 세션 흐름, AI 코칭 턴, 묵상 노트 생성 |
| 8 | 테스트 코드 | 단위 테스트 존재, 핵심 로직(Service/UseCase) 커버, 통합 테스트 또는 미작성 사유 명시 |

### 4.2 팀원 리뷰 코멘트 레벨 (Claude 보완)

```
[BLOCK]   머지 전 반드시 수정
[SUGGEST] 개선 제안 (개발자 판단)
[NIT]     사소한 스타일 (무시 가능)
[PRAISE]  잘된 코드 칭찬
```

---

## 5. 회의 규칙·스탠드업

### 5.1 주간 페이스 점검 (화 11:30 — 강제)

매주 화요일 11:30, 강태오 진행, 10분 내.
각자 30초: 지난주 완료 / 이번주 목표 / 막힌 것.

**30분 이상 막힌 문제는 반드시 공유** — 혼자 씨름 금지.

### 5.2 일일 비동기 스탠드업 (Slack)

매일 오전 9~10시 `#daily-standup` 채널:

```
✅ 어제 한 것: auth JWT 발급 구현 (PR #12 자동 머지)
🔧 오늘 할 것: Refresh Token Blacklist Redis 구현
🚫 막힌 것: JWK 캐싱 TTL — 강태오 의견 요청
```

---

## 6. Slack 채널 운영

| 채널 | 용도 |
| --- | --- |
| `#general` | 팀 전체 공지·잡담 |
| `#daily-standup` | 매일 오전 비동기 스탠드업 |
| `#개발-리뷰` | PR 링크 공유 + 리뷰 요청 |
| `#decisions` | 설계·기술 결정 사항 기록 |
| `#bugs` | 버그 발견 즉시 공유 |
| `#claude알람채널` | 운영 alert 자동 발송 |

---

## 7. 긴급 상황 대응

### 7.1 긴급 연락 체계

| 상황 | 1차 연락 | 2차 연락 |
| --- | --- | --- |
| dev 빌드 깨짐 | 마지막 머지 작성자 | 강태오 |
| 보안 이슈 (시크릿 노출) | 강태오 즉시 | 전체 팀 |
| 시연 당일 장애 | 강태오 | 강상민 / 김지민 |

### 7.2 dev 빌드 깨짐 대응

```bash
# Slack #bugs 즉시 공유 후 revert
git checkout dev
git log --oneline -5
git revert <commit-hash>
git push origin dev
```

### 7.3 W4~W5 코드 프리즈 (6/12 금요일 이후)

```
- 새 기능 추가 금지
- 버그 수정만 허용 (강태오 승인)
- 모든 수정은 hotfix 브랜치 경유
- 시연 빌드: git tag v1.0.0-demo
```

---

> **협업 규칙의 핵심:** Claude 자동 리뷰가 있더라도 PR 템플릿을 성실하게 작성하는 것이 팀 전체 시간을 줄인다. 1차(HMS)에서 PR 없이 직접 push → 코드 충돌 → 3시간 날린 경험을 잊지 말자.
