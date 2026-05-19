# Git 규칙 — QT-AI v3.1 기준

> **문서 버전:** v3.1
> **작성일:** 2026-05-08 / **최종 갱신:** 2026-05-18
> **기준 문서:** [07_요구사항_정의서 v3.1](./07_요구사항_정의서.md), [00_문서_역할_분리표](./00_문서_역할_분리표.md), [02_ERD_문서](./02_ERD_문서.md), [03_아키텍처_정의서](./03_아키텍처_정의서.md), [04_API_명세서](./04_API_명세서.md), [05_시퀀스_다이어그램](./05_시퀀스_다이어그램.md), [06_화면_기능_정의서](./06_화면_기능_정의서.md), [18_코드_품질_게이트](./18_코드_품질_게이트.md), [22_구현_저장소_반영_체크리스트](./22_구현_저장소_반영_체크리스트.md), [23_도메인_용어사전](./23_도메인_용어사전.md), [25_기능_명세서](./25_기능_명세서.md)
> **문서 역할:** 문서 기준 저장소와 구현 저장소의 Git 브랜치, 커밋, PR, 리뷰 운영 기준 관리
> **owner:** 강태오 (Lead — 규칙 정의 + 강제)
> **목적:** 6명이 6주 동안 충돌 없이 협업한다. Git 충돌, 빌드 깨짐, 리뷰 없는 머지, 요구사항 역주행을 PR 단계에서 차단한다.

---

## 협업 기준

아래 기준은 이 문서 전체에 우선한다. 기능·비기능·화면 요구사항이 충돌하면 `07_요구사항_정의서.md` v3.1을 따른다. 문서 역할과 충돌 처리 방식은 `00_문서_역할_분리표.md`를 따른다.

- 백엔드는 단일 `qtai-server` Modular Monolith로 운영한다.
- 도메인 간 Entity/Service/Repository 직접 import를 금지하고 DTO/Interface로만 통신한다.
- `note`, `sharing`, `praise`는 별도 도메인으로 두며 독립 서비스로 분리하지 않는다.
- 외부 공개 API는 `/api/v1/**` HTTP API이고, 내부 도메인 인터페이스는 Java Interface다.
- RAG, ChromaDB, 벡터 DB, Elasticsearch는 v1에서 사용하지 않는다.
- Kafka, Kubernetes, Helm은 v1에서 도입하지 않는다. v1은 Spring `ApplicationEventPublisher`와 Docker Compose 기준이다.
- AI 자유 챗봇, 다중 턴 대화, SSE, `/ai/sessions/**` 엔드포인트는 만들지 않는다.
- 해설·시뮬레이터 생성은 04:00 KST 배치 또는 관리자 트리거에서만 실행하고, F-15 사실 기반 Q&A는 단발·검증 흐름으로만 실행한다.
- QT 본문은 성서 유니온 00:00 KST 공개, 우리 시스템 04:00 KST 수집 배치 기준으로 처리한다.
- 오늘 QT 100%는 본문, 해설 진입점, 묵상 진입점, 시뮬레이터 상태값이 정상 응답한다는 뜻이다. 모든 본문에 실제 시뮬레이터 클립이 있다는 뜻이 아니다.
- 성경 데이터는 Repo URL, 라이선스, 번역본명, 출처 표기, 재배포 가능 여부를 확인한 GitHub 공개 JSON만 적재한다.
- 개역개정, ESV, NIV는 저장·시드·응답에 포함하지 않는다.
- 찬양은 운영자 큐레이션 메타데이터만 제공한다. AI 추천, 가사/음원 저장, 직접 URL 입력은 제외한다.
- 교회 인증은 MVP에서 완전히 제외한다. 회원가입 화면에 버튼도 두지 않는다.

---

## 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-08 | 강태오 (Lead) | 초기 작성 — Git 전략·PR 룰·커밋 메시지·코드 리뷰·회의 규칙 |
| v1.1 | 2026-05-12 | 강태오 (Lead) | `develop` → `dev` 브랜치 변경 / Claude 자동 리뷰·자동 머지 시스템 반영 |
| v1.2 | 2026-05-13 | 강태오 (Lead) | PR 테스트 필수 조건 강화 / PR 템플릿 dev 브랜치 실제본 동기화 / Claude 리뷰 기준 확장 |
| v2.x | 2026-05-14 | Codex + 강태오 | 이전 요구사항 기준으로 Modular Monolith, 배치 AI, API prefix, 금지 패턴, PR 체크리스트 정합화 |
| v2.4 | 2026-05-15 | Codex | 문서 역할 분리 이후 `00`, `03`, `04`, `18`, `23` 기준을 협업 규칙과 PR 템플릿에 연결 |
| v3.1 | 2026-05-18 | Codex | 02~08 최신 기준으로 Kakao 인증, `domain.*` 패키지, F-15 사실 기반 Q&A, 권한 기준 정합화 |

---

## 목차

1. [Git 브랜치 전략](#1-git-브랜치-전략)
2. [커밋 메시지 규칙](#2-커밋-메시지-규칙)
3. [PR 규칙](#3-pr-규칙)
4. [코드 리뷰 기준](#4-코드-리뷰-기준)
5. [문서 변경 규칙](#5-문서-변경-규칙)
6. [회의 규칙·스탠드업](#6-회의-규칙스탠드업)
7. [Slack 채널 운영](#7-slack-채널-운영)
8. [긴급 상황 대응](#8-긴급-상황-대응)
9. [현재 상태](#9-현재-상태)

---

## 1. Git 브랜치 전략

### 1.1 브랜치 구조

```text
master        ← 최종 배포 브랜치 (Lead 수동 머지)
  └── dev     ← 통합 브랜치 (팀원 PR 대상 — 자동 리뷰 + CI)
        ├── feature/member-kakao-oauth
        ├── feature/qt-today-response
        ├── feature/bible-qt-batch-collector
        ├── feature/ai-explanation-batch
        ├── feature/study-simulator-status-api
        ├── docs/requirements-v31-sync
        └── bugfix/study-simulator-fallback
```

**브랜치 역할 요약**

| 브랜치 | 역할 |
| --- | --- |
| `dev` | 팀원 PR 대상. 자동 리뷰와 CI 통과 후 squash merge |
| `master` | 배포 단위. Lead가 `dev` → `master` PR을 직접 검토 후 수동 머지 |
| `feature/*` | 기능 개발 |
| `bugfix/*` | 버그 수정 |
| `docs/*` | 문서 수정 |
| `refactor/*` | 구조 개선 |
| `chore/*` | 빌드·CI·설정 변경 |
| `hotfix/*` | 긴급 수정 |

### 1.2 브랜치 명명 규칙

```text
{type}/{scope}-{짧은-설명}
```

**scope 기준**

| scope | 담당/영역 | 기준 경로·책임 |
| --- | --- | --- |
| `member` | 강태오 | `qtai-server/src/main/java/com/qtai/domain/member/` — JWT, Kakao OAuth, 회원·프로필 |
| `qt` | 강태오·이지윤 | `qtai-server/src/main/java/com/qtai/domain/qt/` — Today QT, QT 범위 |
| `bible` | 이지윤 | `qtai-server/src/main/java/com/qtai/domain/bible/` — 성경 본문·출처 |
| `study` | 이지윤·김태혁 | `qtai-server/src/main/java/com/qtai/domain/study/` — 해설, 용어, 시뮬레이터 조회 |
| `note` | 이승욱 | `qtai-server/src/main/java/com/qtai/domain/note/` — 노트, 카테고리, 묵상 달력 |
| `sharing` | 이승욱 | `qtai-server/src/main/java/com/qtai/domain/sharing/` — 닉네임 나눔, 댓글, 좋아요 |
| `praise` | 김지민 | `qtai-server/src/main/java/com/qtai/domain/praise/` — 찬양 큐레이션, 내 찬양 |
| `ai` | 강상민 | `qtai-server/src/main/java/com/qtai/domain/ai/` — DeepSeek 생성·검증, F-15 사실 기반 Q&A |
| `mobile` | 김지민 중심 | Flutter 앱 |
| `admin` | domain별 관리자 API + Flutter Web | 관리자 화면/API |
| `infra` | 강태오 | Docker Compose, GitHub Actions, gitleaks, 품질 게이트 |
| `docs` | 전원 | 요구사항, 문서 역할 분리표, 아키텍처, API, 품질 게이트, 용어사전, 회의록, 일정표 |

**삭제·금지된 scope**

| 금지 scope | 이유 |
| --- | --- |
| `auth-service` | 독립 Auth Service 없음. `domain.member`에서 처리 |
| `note-service` | 독립 Note Service 없음. `domain.note`에서 처리 |
| `ai-chat` | 세션형 AI 자유 챗봇 없음. F-15 사실 기반 Q&A는 `domain.ai` 단발 흐름 |
| `rag` | RAG·벡터 DB 제외 |
| `kafka` | Kafka는 v1 보류 |
| `k8s`, `helm` | Kubernetes/Helm은 v1 보류 |

**예시**

```bash
git checkout dev
git checkout -b feature/member-kakao-oauth
git checkout -b feature/qt-today-response
git checkout -b feature/bible-qt-batch-collector
git checkout -b feature/note-meditation-calendar
git checkout -b feature/ai-explanation-batch
git checkout -b feature/study-simulator-status-api
git checkout -b docs/requirements-v31-sync
```

### 1.3 브랜치 운영 규칙

| 규칙 | 내용 |
| --- | --- |
| `master` 직접 push 금지 | Lead 전용. `dev` → `master` PR 수동 검토 |
| `dev` 직접 push 금지 | 모든 작업은 feature/bugfix/docs 브랜치 경유 |
| 담당 범위 밖 변경 금지 | 필요한 경우 PR 본문에 이유와 영향 범위를 명시 |
| unrelated 파일 stage 금지 | 빌드 산출물, `.gradle`, `build/reports` 등 의도치 않은 파일 제외 |
| 브랜치 수명 | 최대 3일 권장. 장기 작업은 작은 PR로 분리 |
| 완료 브랜치 삭제 | PR 머지 후 원격 브랜치 삭제 |

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

> PR을 올린 뒤 force push가 필요하면 PR 코멘트에 이유를 남긴다.

---

## 2. 커밋 메시지 규칙

### 2.1 Conventional Commits 형식

```text
{type}({scope}): {subject}
```

**type 목록**

```text
feat      새 기능
fix       버그 수정
docs      문서 수정
refactor  리팩토링
test      테스트 추가·수정
chore     빌드·의존성·CI
```

### 2.2 커밋 메시지 예시

```bash
# 좋은 예
feat(member): add Kakao OAuth login filter
feat(qt): add today QT response aggregator
feat(bible): add 04 KST QT passage collector
feat(ai): persist explanation batch run status
feat(simulator): return simulator availability status
docs(requirements): align v3.1 decisions

# 나쁜 예
git commit -m "수정"
git commit -m "fix bug"
git commit -m "작업중"
git commit -m "feat(ai): add user chat SSE"
git commit -m "feat(kafka): add event topics"
```

### 2.3 커밋 단위 원칙

```text
좋음: 1 커밋 = 1 논리적 변경
좋음: 구현과 해당 테스트를 같은 커밋에 포함
나쁨: 여러 도메인 기능을 한 커밋에 묶기
나쁨: 빌드가 깨지는 커밋 push
나쁨: 산출물/캐시 파일을 함께 커밋
```

---

## 3. PR 규칙

### 3.1 PR 자동화 시스템

PR을 `dev`에 올리면 아래 검증이 실행된다.

```text
PR 오픈 (base: dev)
  ├─ QT-AI CI
  │  ├─ 단일 qtai-server build/test
  │  ├─ Flutter test (앱 변경 시)
  │  ├─ Spring Modulith / ArchUnit 도메인 경계 검증
  │  ├─ Requirements Guard (금지 기술·금지 엔드포인트·금지 데이터 검사)
  │  ├─ Document/Terminology Guard (문서·용어 기준 검사)
  │  └─ gitleaks secret scan
  │
  └─ 자동 코드 리뷰
     ├─ APPROVE → CI 통과 확인 → squash merge
     └─ REQUEST_CHANGES → 수정 후 재리뷰
```

**팀원이 해야 할 것**

- PR 템플릿을 성실하게 작성한다.
- 요구사항 변경은 `07_요구사항_정의서.md` 근거를 링크하고 Lead 리뷰를 받는다.
- REQUEST_CHANGES를 받으면 코멘트 확인 후 수정한다.
- 담당 범위 밖 변경이 있으면 이유와 리뷰어를 명시한다.

**팀원이 하지 않아도 되는 것**

- `dev`에 직접 push하지 않는다.
- 수동 머지 버튼을 누르지 않는다.
- 금지 기술을 "나중에 지울 임시 코드"로 넣지 않는다.

### 3.2 PR 생성 기준

| 항목 | 기준 |
| --- | --- |
| PR 대상 브랜치 | 항상 `dev` (`master` 직접 PR 금지) |
| PR 크기 | 변경 파일 10개 이하, 500줄 이하 권장 |
| 자동 CI | GitHub Actions 자동 실행. 실패 시 머지 차단 |
| 자동 리뷰 | 코드 리뷰 통과 필요 |
| 머지 방식 | Squash Merge |
| 요구사항 근거 | 기능 PR은 `07_요구사항_정의서.md`의 F-ID 포함 |
| 설계/API 근거 | 아키텍처 변경은 `03`, API 변경은 `04`, 품질 게이트 변경은 `18`, 용어 변경은 `23` 링크 포함 |

### 3.3 PR 템플릿

```markdown
## 구현 내용
<!-- 이 PR에서 해결하거나 추가하는 변경 사항을 간략하게 설명하세요. -->

## 관련 요구사항 / 문서
<!-- 예: F-01-11, F-02-01, 03_아키텍처_정의서.md §5, 04_API_명세서.md §4, 18_코드_품질_게이트.md §3 -->

## 변경 유형
- [ ] 기능 추가 (feat)
- [ ] 버그 수정 (fix)
- [ ] 리팩토링 (refactor)
- [ ] 테스트 (test)
- [ ] 문서 (docs)
- [ ] 인프라 / CI (chore)

## v3.1 코드·문서 체크리스트
- [ ] `07_요구사항_정의서.md` v3.1과 충돌하지 않음
- [ ] `00_문서_역할_분리표.md`의 문서 책임과 충돌하지 않음
- [ ] 아키텍처 변경은 `03_아키텍처_정의서.md`, API 변경은 `04_API_명세서.md`, 품질 게이트 변경은 `18_코드_품질_게이트.md`, 용어 변경은 `23_도메인_용어사전.md`와 정합함
- [ ] 단일 `qtai-server` Modular Monolith 기준을 지킴
- [ ] `note`, `sharing`, `praise`는 별도 도메인으로 유지하고 독립 서비스로 분리하지 않음
- [ ] 다른 도메인의 Entity/Service/Repository 직접 import 없음
- [ ] 도메인 간 호출은 DTO/Interface로만 처리
- [ ] 외부 공개 API는 `/api/v1/**`, 내부 도메인 인터페이스는 Java Interface로 분리됨
- [ ] RAG, ChromaDB, 벡터 DB, Elasticsearch 코드/의존성 없음
- [ ] Kafka, Kubernetes, Helm v1 도입 없음
- [ ] AI 자유 챗봇, 다중 턴 대화, SSE, `/ai/sessions/**` 엔드포인트 없음
- [ ] 해설·시뮬레이터는 사용자 요청 경로에서 즉시 생성하지 않음
- [ ] F-15 사실 기반 Q&A는 단발·검증 흐름으로만 제공
- [ ] QT 본문은 00:00 KST 공개 / 04:00 KST 수집 배치 기준
- [ ] 오늘 QT 응답은 본문, 해설 진입점, 묵상 진입점, 시뮬레이터 상태값을 반환
- [ ] 성서 유니온·두란노 본문 텍스트 자체 저장 없음
- [ ] 성경 데이터는 Repo URL·라이선스·번역본명·출처 표기·재배포 가능 여부 확인 완료
- [ ] 개역개정, ESV, NIV 시드/응답/테스트 데이터 없음
- [ ] 찬양 가사·음원 저장 없음, AI 찬양 추천 없음
- [ ] 교회 인증 화면/버튼/API 없음
- [ ] 시뮬레이터는 `READY/MISSING/FAILED/DISABLED` 상태를 반환
- [ ] 관리자 API는 기능별 관리자 권한, 배치/AI 내부 작업은 `SYSTEM_BATCH` 권한 기준
- [ ] 인프로세스 이벤트 실패 시 `eventId` + error log 기록 및 재처리 가능
- [ ] `application.yml` 또는 코드에 평문 Secret 없음

## 테스트 체크리스트
- [ ] 단위 테스트(Unit Test) 작성 완료 및 `./gradlew -p qtai-server test` 로컬 통과
- [ ] 통합 테스트(Integration Test) 작성 완료
      또는 미작성 사유:
- [ ] docs / chore 타입은 해당 없음

## 테스트 방법
<!-- 어떻게 테스트했는지 설명 (Unit / Integration / 수동) -->
```

### 3.4 PR 라이프사이클

```text
1. dev 최신화
   git checkout dev && git pull origin dev

2. feature 브랜치 생성
   git checkout -b feature/qt-today-response

3. 코드 작성 + 커밋
   git commit -m "feat(qt): add today QT response aggregator"

4. push
   git push -u origin feature/qt-today-response

5. GitHub에서 PR 오픈 (base: dev)

6. 자동 리뷰 + CI 실행
   - 리뷰 APPROVE + CI 통과 → squash merge
   - REQUEST_CHANGES → 수정 후 push
   - CI 실패 → 머지 차단

7. 완료 후 feature 브랜치 삭제
```

### 3.5 REQUEST_CHANGES 주요 원인

**즉시 반려 (Critical)**

```text
타 팀원 담당 범위 파일을 사전 설명 없이 수정
하드코딩된 API Key / 비밀번호 / private key 발견
독립 서비스 디렉토리 생성 (auth-service, bible-service, ai-service 등)
RAG, ChromaDB, 벡터 DB, Elasticsearch 코드/의존성 추가
Kafka, Kubernetes, Helm v1 코드/설정 추가
사용자용 AI Q&A/SSE/API 경로 추가
성경 데이터에 개역개정, ESV, NIV 포함
성서 유니온·두란노 본문 텍스트 저장
찬양 가사·음원 저장 또는 AI 찬양 추천 구현
교회 인증 버튼/API 추가
```

**경고 후 반려 (수정 필요)**

```text
DB 쓰기 메서드에 @Transactional 누락
빈 catch 블록 — catch (Exception e) {} 금지
javax.* 사용 (Spring Boot 3.x → jakarta.*)
다른 도메인 Entity/Service/Repository 직접 import
외부 공개 API가 /api/v1 prefix를 따르지 않음
내부 Java Interface를 HTTP API나 OpenAPI 경로처럼 설계
시뮬레이터 미완성 상태인데 상태값 없이 null 반환
오늘 QT 응답에서 해설 진입점·묵상 진입점·시뮬레이터 상태값 누락
인프로세스 이벤트 핸들러 실패 로그/재처리 근거 없음
새 기능(feat) PR에 단위 테스트 코드 없음
핵심 로직(Service, UseCase) 변경인데 테스트 없음
"다음 PR에서 테스트 추가 예정"만 제시
통합 테스트 미작성인데 PR 본문에 사유 없음
```

### 3.6 긴급 hotfix 절차

```bash
git checkout master
git checkout -b hotfix/critical-bug

git commit -m "fix(member): prevent JWT verification bypass"

# master에 PR → Lead 즉시 수동 검토
# 이후 dev에도 cherry-pick
git checkout dev
git cherry-pick <commit-hash>
git push origin dev
```

---

## 4. 코드 리뷰 기준

### 4.1 자동 리뷰 기준

| # | 기준 | 주요 체크 |
| --- | --- | --- |
| 1 | 코드 품질 | 가독성, 네이밍, 중복 코드, 과도한 추상화 |
| 2 | 버그 가능성 | NPE, 인덱스 오류, 예외 처리 누락, fallback 누락 |
| 3 | 보안 | 하드코딩된 시크릿, SQL Injection, 권한 검증, 관리자/SYSTEM_BATCH 권한 |
| 4 | Spring Boot 3.x 호환성 | deprecated API, `javax.*` 사용 여부 |
| 5 | 트랜잭션·이벤트 | `@Transactional` 범위, 이벤트 실패 로그, 재처리 가능성 |
| 6 | Modular Monolith | 도메인 import 금지, DTO/Interface 통신, API timeout |
| 7 | 제품 요구사항 | 오늘 QT 00:00/04:00 기준, AI 배치 전용, 큐레이션 찬양, 시뮬레이터 상태 |
| 8 | 테스트 코드 | 단위 테스트, 핵심 UseCase 커버, 통합 테스트 또는 미작성 사유 |

### 4.2 팀원 리뷰 코멘트 레벨

```text
[BLOCK]   머지 전 반드시 수정
[SUGGEST] 개선 제안 (개발자 판단)
[NIT]     사소한 스타일
[PRAISE]  잘된 코드 칭찬
```

---

## 5. 문서 변경 규칙

이 저장소는 문서·명세 기준 틀이다. 구현 저장소는 이 기준을 따라 PR, CI, 리뷰 규칙을 구성한다.

### 5.1 문서별 변경 책임

| 문서 | 변경 가능 조건 | 필수 확인 |
| --- | --- | --- |
| `07_요구사항_정의서.md` | 기능·비기능·화면 요구사항 원본 변경 시 | Lead 리뷰, 영향 문서 동시 확인 |
| `03_아키텍처_정의서.md` | 구조, 도메인 경계, 이벤트 기준 변경 시 | `07`, `18`, `23`과 충돌 여부 |
| `04_API_명세서.md` | 외부 API, 내부 Java Interface 계약 변경 시 | `/api/v1`, 권한, DTO, OpenAPI 영향 |
| `18_코드_품질_게이트.md` | PR/CI 차단 기준 변경 시 | 구현 저장소 CI 반영 가능성 |
| `23_도메인_용어사전.md` | 용어, 상태값, 피해야 할 표현 변경 시 | 문서와 코드 상수명 영향 |
| `09_Git_규칙.md` | 브랜치, PR, 리뷰, 머지 규칙 변경 시 | `18` 품질 게이트와 정합성 |

### 5.2 충돌 처리 원칙

| 충돌 유형 | 우선 기준 |
| --- | --- |
| 기능 포함 여부 | `07_요구사항_정의서.md` |
| 비기능 목표 | `07_요구사항_정의서.md` |
| 화면 요구 | `07_요구사항_정의서.md` |
| 시스템 구조 | `03_아키텍처_정의서.md`, 단 `07` 위반 불가 |
| API 계약 | `04_API_명세서.md`, 단 `07` 위반 불가 |
| 품질 검증 방식 | `18_코드_품질_게이트.md`, 단 `07`를 검증 가능하게 유지 |
| 용어·표현 | `23_도메인_용어사전.md`, 단 `07` 의미 변경 불가 |

### 5.3 문서 PR 체크

문서 PR은 아래를 확인한다.

- 같은 내용을 여러 문서에 반복하지 않는다.
- `07_요구사항_정의서.md` 슬림화는 완료된 상태로 유지하고, 이후 요구사항 변경은 Lead 리뷰와 영향 문서 동시 확인을 거친다.
- `저작권 문제 없음`, `유실률 0% 보장`, `내부 API 경로`, `AI 찬양 추천` 같은 피해야 할 표현은 허용 문맥으로 쓰지 않는다.
- `note`, `sharing`, `praise`는 별도 도메인으로 표현한다.
- 기준 문서를 바꾸면 관련 문서의 현재 상태 표와 다음 권장 작업도 함께 확인한다.

---

## 6. 회의 규칙·스탠드업

### 6.1 주간 페이스 점검

매주 화요일 11:30, 강태오 진행, 10분 내.
각자 30초씩 지난주 완료 / 이번주 목표 / 막힌 것을 공유한다.

**30분 이상 막힌 문제는 반드시 공유한다.**

### 6.2 일일 비동기 스탠드업

매일 오전 9~10시 `#daily-standup` 채널:

```text
어제 한 것: qt 오늘 QT 응답 조립 PR 작성
오늘 할 것: 시뮬레이터 상태 fallback 테스트
막힌 것: 04:00 배치 실패 시 기존 캐시 유지 정책 확인 필요
```

---

## 7. Slack 채널 운영

| 채널 | 용도 |
| --- | --- |
| `#general` | 팀 전체 공지·잡담 |
| `#daily-standup` | 매일 오전 비동기 스탠드업 |
| `#개발-리뷰` | PR 링크 공유 + 리뷰 요청 |
| `#decisions` | 설계·기술 결정 사항 기록 |
| `#bugs` | 버그 발견 즉시 공유 |
| `#claude알람채널` | 자동 리뷰·CI 알림 |

---

## 8. 긴급 상황 대응

### 8.1 긴급 연락 체계

| 상황 | 1차 연락 | 2차 연락 |
| --- | --- | --- |
| `dev` 빌드 깨짐 | 마지막 머지 작성자 | 강태오 |
| 보안 이슈 (시크릿 노출) | 강태오 즉시 | 전체 팀 |
| 요구사항 충돌 발견 | 해당 PR 작성자 | 강태오 |
| 시연 당일 장애 | 강태오 | 강상민 / 김지민 |

### 8.2 `dev` 빌드 깨짐 대응

```bash
# Slack #bugs 즉시 공유 후 revert
git checkout dev
git log --oneline -5
git revert <commit-hash>
git push origin dev
```

### 8.3 W4~W5 코드 프리즈 (6/12 금요일 이후)

```text
새 기능 추가 금지
버그 수정만 허용 (강태오 승인)
모든 수정은 hotfix 브랜치 경유
시연 빌드: git tag v1.0.0-demo
```

---

## 9. 현재 상태

| 항목 | 상태 |
| --- | --- |
| 기준 요구사항 | `07_요구사항_정의서.md` v3.1 유지 |
| Git 규칙 문서 | 이 문서에서 v3.1로 재점검 완료 |
| 문서 역할 분리표 | `00_문서_역할_분리표.md` v0.1 반영 |
| ERD 문서 | `02_ERD_문서.md` v2.0 반영 |
| 구현 저장소 반영 체크리스트 | `22_구현_저장소_반영_체크리스트.md` v0.1 반영 |
| 기능 명세서 | `25_기능_명세서.md` v0.1 반영 |
| 화면 기능 정의서 | `06_화면_기능_정의서.md` v1.1 반영 |
| 시퀀스 다이어그램 | `05_시퀀스_다이어그램.md` v1.0 반영 |
| 아키텍처 정의서 | `03_아키텍처_정의서.md` v1.0 반영 |
| API 명세서 | `04_API_명세서.md` v1.3 반영 |
| 품질 게이트 | `18_코드_품질_게이트.md` v2.4 반영 |
| 도메인 용어사전 | `23_도메인_용어사전.md` v0.1 반영 |
| 전체 문서 정합성 최종 점검 | 진행 완료 |
| 다음 권장 작업 | 별도 구현 GitHub 1번 PR에서 PR 템플릿, CODEOWNERS, `workspaces/*/{workflows,reports}` 생성 |

---

> **Git 규칙의 핵심:** 자동 리뷰가 있더라도 PR 템플릿을 성실하게 작성해야 팀 전체 시간이 줄어든다. v3.1 요구사항과 충돌하는 구현은 "임시"라도 머지하지 않는다.
