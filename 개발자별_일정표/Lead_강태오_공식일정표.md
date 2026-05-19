# QT-AI 개인 공식 일정표 - 강태오

> **문서 버전:** v3.1-align.1
> **작성일:** 2026-05-15
> **기준 문서:** `00_개발_일정_총괄표.md` v0.1, `07_요구사항_정의서.md` v3.1
> **적용 범위:** 강태오 Lead 일정표이면서, 다른 팀원 개인 일정표 작성 시 복제 가능한 공통 기준
> **연관 문서:** `09_Git_규칙.md`, `18_코드_품질_게이트.md`, `23_도메인_용어사전.md`, `24_템플릿_문서_매핑표.md`, `개발자별_일정표/00_공통_브랜치_PR_워크플로우_규칙.md`

---

## 1. 역할

| 항목 | 내용 |
| --- | --- |
| 담당자 | 강태오 |
| 주 역할 | Lead / platform / member / qt / admin / DevOps / 전체 조율 |
| 구현 기준 | 단일 `qtai-server` Modular Monolith |
| 협업 기준 | 인증·Today QT·외부 API 계약은 Lead 단독 소유가 아니라 Bible·Flutter 담당자와 API 계약을 맞춰 구현한다. |
| 산출물 기준 | 구현 PR, 검증 로그, 회고 메모, 문서 정합성 수정 내역을 남긴다. |

---

## 2. 흔들리면 안 되는 기준

| 구분 | 고정 기준 |
| --- | --- |
| 백엔드 구조 | 단일 `qtai-server` 안에 `domain.member`, `domain.bible`, `domain.qt`, `domain.study`, `domain.note`, `domain.sharing`, `domain.report`, `domain.notification`, `domain.praise`, `domain.mission`, `domain.ai`, `domain.admin`, `domain.audit` 패키지를 둔다. |
| 배포 기준 | v1은 Docker Compose 기준이다. Kubernetes와 Helm은 MVP 작업 목표에 넣지 않는다. |
| 이벤트 | v1은 Spring `ApplicationEventPublisher`를 사용한다. Kafka는 v2 이후 검토 대상이다. |
| AI | AI 자유 챗봇, 다중 턴 대화, SSE, `/ai/sessions/**` 사용자 경로는 만들지 않는다. F-15 사실 기반 Q&A는 단발·검증 흐름으로 둔다. |
| Today QT | 공개 시각은 00:00 KST, 수집 배치 시각은 04:00 KST로 통일한다. |
| Today QT 100% | 본문·해설·묵상 진입점·시뮬레이터 상태값까지 정상 응답하는 것을 의미한다. 모든 시뮬레이터 클립이 반드시 존재한다는 뜻이 아니다. |
| 시뮬레이터 | `READY`일 때만 보기 버튼을 활성화한다. `MISSING`, `FAILED`, `DISABLED`는 보기 버튼을 비활성화한다. |
| 성경 데이터 | Repo URL, 라이선스, 번역본명, 출처 표기 방식, 재배포 가능 여부가 확인된 GitHub 공개 JSON만 적재한다. 개역개정, ESV, NIV는 금지한다. |
| 검색/AI 저장소 | RDB 인덱스만 사용한다. RAG, ChromaDB, vector DB, Elasticsearch는 사용하지 않는다. |
| 찬양 | AI 추천이 아니라 운영자가 선별한 큐레이션 목록을 제공한다. |
| 교회 인증 | MVP 기본 제외다. 화면, 버튼, API를 작업 목표에 넣지 않는다. |

---

## 3. W1 Foundation Lock-in 상세 일정

W1은 2026-05-18부터 2026-05-22까지 진행한다. 이 기간의 목표는 기능을 많이 만드는 것이 아니라, W2부터 기능 구현이 흔들리지 않도록 기준을 고정하는 것이다.

| 날짜 | 목표 | 작업 범위 | 완료 기준 |
| --- | --- | --- | --- |
| 2026-05-18 | 구현 저장소 골격 고정 | `qtai-server`, Flutter 앱, OpenAPI 위치, 브랜치/PR 흐름 확인 | `dev` 기준 PR 흐름과 기본 빌드 위치가 문서와 맞다. |
| 2026-05-19 | 도메인 패키지 경계 준비 | `domain.member`, `domain.bible`, `domain.qt`, `domain.study`, `domain.note`, `domain.sharing`, `domain.report`, `domain.notification`, `domain.praise`, `domain.mission`, `domain.ai`, `domain.admin`, `domain.audit` 패키지 구조와 import 금지 기준 정리 | 도메인 간 Entity/Service/Repository 직접 import 금지 기준을 검증할 수 있다. |
| 2026-05-20 | DB/API 계약 정리 | 외부 공개 API `/api/v1/**`와 내부 도메인 Java Interface를 분리해 표기 | ERD 주요 테이블과 API 초안이 서로 충돌하지 않는다. |
| 2026-05-21 | 품질 게이트 자동화 | 금지 기술, 금지 API, 금지 데이터, 문서 용어 검사 기준 준비 | Kafka/K8s/Helm/SSE/RAG/금지 번역본이 PR에서 검출 가능하다. |
| 2026-05-22 | Foundation 5/5 판정 | 저장소 운영, 백엔드 골격, 도메인 경계, DB/API 계약, 품질 게이트 최종 확인 | `Foundation 5/5`가 모두 통과해야 W2로 넘어간다. |

### W1 완료 체크리스트

| # | 체크 항목 | 상태 |
| --- | --- | --- |
| 1 | 저장소 운영 기준 정리 | TODO |
| 2 | 단일 `qtai-server` 골격 정리 | TODO |
| 3 | 도메인 경계 검증 준비 | TODO |
| 4 | 외부 API와 내부 인터페이스 분리 | TODO |
| 5 | 품질 게이트 기본 검사 준비 | TODO |

---

## 4. W2-W5 일정 요약

| 주차 | 기간 | Lead 집중 범위 | 완료 기준 |
| --- | --- | --- | --- |
| W2 | 2026-05-25 ~ 2026-05-29 | Today QT 집계, 인증·권한, 외부 API 응답 조립, PR 검증 | 핵심 API 데모가 가능하다. |
| W3 | 2026-06-01 ~ 2026-06-05 | 관리자·통합 조정, Feature Freeze, 경계 위반 차단 | 주요 MVP 기능이 통과한다. |
| W4 | 2026-06-08 ~ 2026-06-12 | E2E, 성능, 품질 게이트, Docker Compose 시연 후보 빌드 | 시연 후보 빌드를 확보한다. |
| W5 | 2026-06-15 ~ 2026-06-17 | 리허설, 백업 자료, 발표 직전 장애 대응 | 발표 흐름 2회 이상 성공한다. |

---

## 5. 매일 작업 순서

| 순서 | 작업 |
| --- | --- |
| 1 | `dev` 최신 상태를 확인한다. |
| 2 | 오늘 작업이 `00_개발_일정_총괄표.md`의 주차별 게이트 안에 있는지 확인한다. |
| 3 | 작업 전 API 계약, ERD, 화면 정의, 용어사전을 먼저 확인한다. |
| 4 | 구현 후 단위 테스트와 금지 패턴 검사를 실행한다. |
| 5 | PR 본문에 변경 범위, 검증 명령, 남은 리스크를 적는다. |
| 6 | 하루 종료 시 완료/미완료/내일 작업을 짧게 기록한다. |

---

## 6. 브랜치·PR·워크플로우 기록 규칙

| 항목 | Lead 기준 |
| --- | --- |
| 브랜치 생성 | `dev` 최신화 후 `feature/qt-*`, `feature/member-*`, `chore/infra-*`, `feature/admin-*` 형식으로 생성 |
| PR 대상 | 항상 `dev` |
| 자동 PR | 브랜치 push 후 GitHub PR을 생성하면 CI와 자동 리뷰가 실행된다. 자동 머지는 하지 않는다. |
| 작업 폴더 | 별도 구현 GitHub에서 `workspaces/Lead_강태오/workflows`, `workspaces/Lead_강태오/reports`를 사용 |
| 기록 순서 | 작업 전 workflow 작성 → 작업·검증 → report 작성 → PR 생성 |
| 기준 문서 | 상세 명령과 템플릿은 `개발자별_일정표/00_공통_브랜치_PR_워크플로우_규칙.md`를 따른다. |

---

## 7. PR 전 검증 명령

아래 명령은 구현 저장소 기준으로 실행한다.

```powershell
git checkout dev
git pull origin dev
./gradlew -p qtai-server test
rg -n "Kafka|Kubernetes|Helm|/ai/sessions|SSE|RAG|ChromaDB|Elasticsearch|개역개정|ESV|NIV" .
```

문서 저장소에서는 Markdown 표, 코드펜스, API JSON, 금지 기준 문구를 확인한다.

```powershell
git diff --check -- '*.md'
```

---

## 8. 산출물

| 시점 | 산출물 |
| --- | --- |
| W1 | Foundation 5/5 검증표, 도메인 경계 검증 결과, API/ERD 계약 확인 메모 |
| W2 | Today QT 핵심 API 데모, 인증·권한 검증 결과 |
| W3 | Feature Freeze 확인표, 관리자·통합 검증 결과 |
| W4 | E2E 결과, 성능 점검 결과, Docker Compose 시연 후보 빌드 |
| W5 | 발표 리허설 결과, 백업 영상/스크립트, 최종 회고 |

---

## 9. 다른 팀원 일정표로 복제할 때 바꿀 부분

| 항목 | 변경 방식 |
| --- | --- |
| 담당자 | 팀원 이름으로 변경 |
| 주 역할 | 해당 팀원의 도메인과 화면 책임으로 변경 |
| W1 상세 작업 | 공통 Foundation 5/5 안에서 개인 담당 영역만 바꾼다. |
| W2-W5 집중 범위 | `00_개발_일정_총괄표.md`의 주차별 게이트를 벗어나지 않는 선에서 바꾼다. |
| 브랜치·PR·작업 폴더 | 공통 규칙은 유지하고 담당자명, scope, `workspaces/{담당자}`만 바꾼다. |
| 금지 기준 | 삭제하거나 완화하지 않는다. |

---

## 10. 현재 상태

| 항목 | 상태 |
| --- | --- |
| 공식 일정표 | `00_개발_일정_총괄표.md` 기준으로 v3.1 정합화 완료 |
| 실행가이드 | `Lead_강태오_실행가이드.html`과 같은 기준으로 정합화 완료 |
| 브랜치·PR·작업 기록 | 공통 규칙 문서와 Lead 개인 `workspaces` 기준 반영 |
| 다음 권장 작업 | 1번 PR `chore(repo): initialize branch, pr rules and workspaces` 진행 후 2번 CI, 3번 서버 골격 PR로 이어감 |
