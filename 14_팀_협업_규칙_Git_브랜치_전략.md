# 📖 QT-AI (큐티 AI 앱) — 팀 협업 규칙·Git 브랜치 전략 v1.0

> **문서 버전:** v1.0
> **작성일:** 2026-05-08
> **연관 문서:** [01_프로젝트_계획서 v1.3](./01_프로젝트_계획서.md) / [11_개발_환경_셋업_가이드 v1.0](./11_개발_환경_셋업_가이드.md)
> **owner:** 강태오 (Lead — 규칙 정의 + 강제)
> **목적:** 6명이 6주 동안 충돌 없이 협업. Git 충돌·빌드 깨짐·리뷰 없는 머지로 인한 시간 낭비 원천 방지.

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-08 | 강태오 (Lead) | 초기 작성 — Git 전략·PR 룰·커밋 메시지·코드 리뷰·회의 규칙 |

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
main          ← 최종 배포 브랜치 (항상 배포 가능 상태 유지)
  └── develop ← 통합 브랜치 (PR 대상, CI 통과 필수)
        ├── feature/auth-login        ← 기능 개발
        ├── feature/ai-sse-stream
        ├── fix/jwt-refresh-race      ← 버그 수정
        ├── docs/update-api-spec      ← 문서 수정
        └── chore/setup-gradle        ← 빌드·설정 변경
```

### 1.2 브랜치 명명 규칙

```
{type}/{short-description}

type:
  feature   기능 개발
  fix       버그 수정
  docs      문서
  chore     빌드·의존성·CI 설정
  refactor  리팩토링 (기능 변경 없음)
  test      테스트 추가·수정

short-description:
  영소문자 + 하이픈(-)
  25자 이내
  issue 번호 포함 권장: feature/auth-login-#12
```

**예시:**
```bash
git checkout develop
git checkout -b feature/auth-google-oauth
git checkout -b fix/refresh-token-race-condition
git checkout -b docs/update-ai-service-api
```

### 1.3 브랜치 운영 규칙

| 규칙 | 내용 |
| --- | --- |
| main 직접 push 금지 | PR + 강태오 승인 필수 |
| develop 직접 push 금지 | 모든 작업은 feature/fix 브랜치 경유 |
| 브랜치 수명 | 최대 3일 (장기 작업은 매일 develop rebase) |
| 완료 브랜치 삭제 | PR 머지 후 원격 브랜치 즉시 삭제 |
| WIP 브랜치 보호 | `WIP:` prefix 커밋은 PR 생성 금지 |

### 1.4 daily rebase 습관

```bash
# 매일 작업 시작 시 develop 최신화
git fetch origin
git checkout develop
git pull origin develop

# 작업 브랜치로 돌아와 rebase
git checkout feature/my-branch
git rebase develop

# 충돌 해결 후
git rebase --continue
```

> **⚠️ merge 대신 rebase 권장** (develop 히스토리 선형 유지). 단, 공유된 브랜치(PR 올린 후)는 rebase 금지 — force push로 팀원 혼란.

---

## 2. 커밋 메시지 규칙

### 2.1 Conventional Commits 형식

```
{type}({scope}): {subject}

{body}  ← 선택사항

{footer}  ← 선택사항 (issue 참조)
```

**type 목록:**
```
feat     새 기능
fix      버그 수정
docs     문서 수정
style    코드 포맷 (로직 변경 없음)
refactor 리팩토링
test     테스트 추가·수정
chore    빌드·의존성·CI
perf     성능 개선
```

**scope (서비스명 또는 모듈명):**
```
auth, bible, journal, ai, bff, gateway, flutter, common, docs, ci
```

### 2.2 커밋 메시지 예시

```bash
# 좋은 예
feat(auth): add Google OAuth login with JWK verification

Implements Google ID Token validation using JWK endpoint.
Adds GoogleJwkVerifier that fetches and caches JWK keys.

Closes #23

# 좋은 예 (짧은 커밋)
fix(ai): prevent infinite SSE retry on LLM_TIMEOUT

test(journal): add Kafka consumer idempotency test

docs(api): update /ai/sessions POST request schema

# 나쁜 예 (명확하지 않음)
git commit -m "fix bug"
git commit -m "update"
git commit -m "wip"
git commit -m "asdf"
```

### 2.3 한국어 vs 영어

- **커밋 메시지**: 영어 (국제 표준 + 1차 프로젝트에서 한국어 메시지가 터미널에서 깨진 경험)
- **PR 설명, 주석, 변수명**: 영어
- **팀 내 소통 (Slack, 구두)**: 한국어

### 2.4 커밋 단위 원칙

```
✅ 1 커밋 = 1 논리적 변경
✅ 테스트와 구현 같은 커밋 가능
✅ 리팩토링과 기능 변경 분리

❌ 여러 기능을 1 커밋에 묶기
❌ "WIP" 커밋 그대로 push
❌ 빌드 깨지는 커밋 push (feature 브랜치라도)
```

---

## 3. PR (Pull Request) 규칙

### 3.1 PR 생성 기준

| 항목 | 기준 |
| --- | --- |
| PR 대상 브랜치 | 항상 `develop` (main으로 직접 PR 금지) |
| PR 크기 | 변경 파일 10개 이하, 변경 줄 500줄 이하 권장 |
| CI 상태 | GitHub Actions 빌드 통과 필수 (머지 차단) |
| Reviewer | 최소 1명 (강태오 또는 도메인 관련자) |
| 머지 방식 | Squash Merge (feature 브랜치 히스토리 압축) |

### 3.2 PR 템플릿

```markdown
## 변경 내용
<!-- 무엇을 왜 변경했는지 -->

## 주요 변경 파일
- `auth-service/src/.../LoginUseCase.kt` — 로그인 비즈니스 로직 구현
- `auth-service/src/.../AuthController.kt` — 엔드포인트 추가

## 테스트
- [ ] 단위 테스트 추가/수정
- [ ] 통합 테스트 확인
- [ ] `./gradlew test` 로컬 통과

## 체크리스트
- [ ] @Transactional 누락 없음
- [ ] 시크릿이 코드에 없음 (grep 확인)
- [ ] ProblemDetail 에러 코드 사용
- [ ] ADR 작성 필요 여부 검토

## 관련 이슈
Closes #N
```

### 3.3 PR 라이프사이클

```
feature 브랜치 작업 완료
  → CI 통과 확인 (GitHub Actions)
  → PR 생성 + 템플릿 작성
  → Slack #개발-리뷰 채널 링크 공유
  → Reviewer 24시간 내 리뷰
  → 수정 요청 시 해당 브랜치에 추가 커밋
  → 승인 후 Squash Merge
  → feature 브랜치 삭제
  → develop에서 pull
```

### 3.4 긴급 hotfix 절차

```bash
# develop이 아닌 main에서 직접 분기 (W4·W5 시연 버그)
git checkout main
git checkout -b hotfix/critical-jwt-bug

# 수정 + 커밋
git commit -m "hotfix(auth): prevent JWT verification bypass"

# main에 PR (강태오 즉시 승인 가능)
# 승인 후 develop에도 cherry-pick
git checkout develop
git cherry-pick <commit-hash>
```

---

## 4. 코드 리뷰 기준

### 4.1 리뷰어 역할별 체크 포인트

| 리뷰 관점 | 체크 항목 |
| --- | --- |
| **정확성** | 비즈니스 로직이 스펙(01~04번)과 일치하는지 |
| **안전성** | @Transactional 누락 / 평문 시크릿 / 인증 우회 |
| **테스트** | 핵심 로직에 단위 테스트 있는지 |
| **1차 사고 패턴** | Controller에 비즈니스 로직 / 환경 변수 하드코딩 |
| **API 계약** | 04번 OpenAPI 스펙과 응답 구조 일치 |
| **성능** | N+1 쿼리 / 불필요한 DB 조회 / 캐시 미적용 |

### 4.2 리뷰 코멘트 레벨

```
[BLOCK]   머지 전 반드시 수정 (버그·보안·스펙 위반)
[SUGGEST] 개선 제안 (개발자 판단)
[NIT]     사소한 스타일 (무시 가능)
[PRAISE]  잘된 코드 칭찬 (팀 모티베이션)
```

**예시:**
```
[BLOCK] 이 메서드에 @Transactional이 없어서 부분 실패 시 롤백 안 됩니다.

[SUGGEST] refreshToken을 SHA-256으로 해시해서 저장하는 게 보안상 더 안전합니다.

[NIT] 변수명 `r`보다 `refreshToken`이 더 명확해 보입니다.

[PRAISE] QueuedInterceptor로 race condition 깔끔하게 처리했네요!
```

### 4.3 리뷰 응답 원칙

| 항목 | 규칙 |
| --- | --- |
| 리뷰 시간 | PR 생성 후 **24시간 내** 1차 리뷰 (늦으면 Slack ping) |
| 반박 가능 | [SUGGEST]에 반박 가능. 단, 이유를 댓글로 명확히 |
| [BLOCK] 처리 | 즉시 수정 후 re-request review |
| 칭찬 문화 | 좋은 코드에 [PRAISE] 적극적으로 달기 |

---

## 5. 회의 규칙·스탠드업

### 5.1 주간 페이스 점검 (화 11:30 — 강제)

| 항목 | 내용 |
| --- | --- |
| 시간 | 매주 화요일 11:30 (수업 끝나고 바로) |
| 장소 | 강의실 또는 빈 부스 |
| 진행 | 강태오 (10분 내) |
| 형식 | 각자 30초: 지난주 완료 / 이번주 목표 / 막힌 것 |

**30분 이상 막힌 문제는 반드시 공유** — 혼자 씨름 금지.

### 5.2 일일 비동기 스탠드업 (Slack)

매일 오전 9시~10시 사이 `#daily-standup` 채널에 텍스트로:

```
✅ 어제 한 것:
  - auth-service 로그인 UseCase 구현 완료 (#23 PR 생성)

🔧 오늘 할 것:
  - JWT RS256 발급 로직 + 테스트

🚫 막힌 것:
  - 없음
  (또는)
  - JWK 캐싱 TTL 설정에서 막힘 — 강태오 의견 요청
```

### 5.3 화상 회의 규칙 (필요 시)

```
- 15분 내 해결 안 되는 설계 논의 → 30분 화상 회의 소집
- Slack에서 화상 링크 공유
- 결정 사항은 반드시 Slack #decisions 채널 + docs/ 에 기록
- 회의 중 코드 짜기 금지 (이해와 결정만)
```

---

## 6. Slack 채널 운영

### 6.1 채널 목록

| 채널 | 용도 |
| --- | --- |
| `#general` | 팀 전체 공지·잡담 |
| `#daily-standup` | 매일 오전 비동기 스탠드업 |
| `#개발-리뷰` | PR 링크 공유 + 리뷰 요청 |
| `#decisions` | 설계·기술 결정 사항 기록 |
| `#bugs` | 버그 발견 즉시 공유 |
| `#claude알람채널` | 운영 alert (사용자 명시 요청 시 자동 발송) |

### 6.2 멘션 규칙

```
@강태오   설계 결정·긴급 이슈·PR 승인 요청
@강상민   AI Service·RAG·프롬프트 관련
@이승욱   Journal·Kafka 관련
@이지윤   Auth·보안 관련
@김태혁   Bible·데이터 관련
@김지민   Flutter·앱 UI 관련
@here     해당 채널 전체 (알림 O — 신중하게)
@channel  전체 (알림 모두 포함 — 긴급 시만)
```

### 6.3 코드 공유 형식

```
# Slack에서 코드 공유 시 항상 코드블록 사용
```kotlin
@Transactional
fun login(command: LoginCommand): TokenPair {
    // ...
}
```

# 에러 메시지 공유 시
```
FlywayException: Validate failed: Migration checksum mismatch
  for migration version 3
  -> Applied to database : 123456789
  -> Resolved locally    : 987654321
```
```

---

## 7. 긴급 상황 대응

### 7.1 긴급 연락 체계

| 상황 | 1차 연락 | 2차 연락 |
| --- | --- | --- |
| 빌드 깨짐 (develop) | 마지막 머지 작성자 | 강태오 |
| 보안 이슈 발견 (시크릿 노출 등) | 강태오 즉시 | 전체 팀 |
| 시연 당일 장애 | 강태오 | 강상민 (AI) / 김지민 (Flutter) |
| 시연 일주일 전 주요 기능 불가 | 강태오 (cut 결정) | — |

### 7.2 develop 빌드 깨짐 대응

```bash
# 즉시 Slack #bugs 공유
"🚨 develop 빌드 깨짐. 마지막 머지: PR #N (이름)
 에러: [에러 메시지]
 조사 중..."

# 빠른 revert 절차
git checkout develop
git log --oneline -5     # 문제 commit 확인
git revert <commit-hash> # revert commit 생성
git push origin develop

# revert 후 Slack 공지
"develop 빌드 복구. PR #N revert 완료. 원인 분석 중."
```

### 7.3 W4~W5 코드 프리즈

**W4 6/12 금요일 이후 코드 프리즈 원칙:**
```
- 새 기능 추가 금지
- 버그 수정만 허용 (강태오 승인)
- 모든 수정은 hotfix 브랜치 경유
- 시연 빌드는 태그로 고정: v1.0.0-demo
```

```bash
# 시연 빌드 태그
git tag -a v1.0.0-demo -m "시연 빌드 (6/17 발표용)"
git push origin v1.0.0-demo
```

---

> **협업 규칙의 핵심:** 규칙이 복잡해 보여도 지키면 **팀 전체 시간이 줄어든다.** 1차(HMS)에서 PR 없이 직접 push → 코드 충돌 → 3시간 날린 경험을 잊지 말자.
