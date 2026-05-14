# 구현 저장소 기본 구조 기준 — QT-AI v2.3

> **문서 버전:** v0.1
> **작성일:** 2026-05-15
> **기준 문서:** `07_요구사항_정의서.md` v2.3
> **문서 역할:** 구현 저장소 최상위 디렉터리와 각 영역의 책임을 고정한다.

---

## 1. 목적

이 문서는 QT-AI 구현 저장소의 기본 디렉터리 구조를 정의한다.

상세 요구사항은 `07_요구사항_정의서.md`, 아키텍처는 `03_아키텍처_정의서.md`, API 계약은 `04_API_명세서.md`, 품질 게이트는 `18_코드_품질_게이트.md`를 따른다.

---

## 2. 기준 구조

```text
repo-root/
    .github/
        pull_request_template.md
        workflows/
            qt-ai-ci.yml
    apis/
        README.md
        bff/
            README.md
            openapi.yaml
    data/
        README.md
        bible-sources/
            README.md
    db/
        README.md
    infra/
        README.md
    qtai-server/
        README.md
        src/main/java/com/qtai/
            gatewayauth/
            bff/
            bible/
                journal/
                songs/
            ai/
            simulator/
    flutter-app/
        README.md
```

---

## 3. 디렉터리 책임

| 경로 | 책임 | 주의 |
| --- | --- | --- |
| `.github/` | PR 템플릿과 GitHub Actions | 금지 패턴 설명 파일은 Guard 오탐 예외 필요 |
| `apis/` | 외부 공개 OpenAPI 산출물 | 내부 Java Interface는 포함하지 않음 |
| `apis/bff/` | Flutter/Admin이 호출하는 `/api/v1/**` 계약 | 사용자 AI Q&A/SSE API 작성 금지 |
| `data/` | 데이터 출처 검토표, seed 기준 | 성경 본문 원문 무단 저장 금지 |
| `data/bible-sources/` | 성경 JSON 출처·라이선스·재배포 가능 여부 검토 | 개역개정, ESV, NIV 사용 금지 |
| `db/` | 마이그레이션, seed, ERD 반영 파일 | 금지 번역본 fixture 금지 |
| `infra/` | Docker Compose, 로컬 인프라 설정 | Kubernetes/Helm v1 도입 금지 |
| `qtai-server/` | 단일 Spring Boot 백엔드 | 독립 서비스 분리 금지 |
| `flutter-app/` | 사용자 앱과 필요 시 관리자 UI | 교회 인증, AI 질문 화면 금지 |

---

## 4. 백엔드 패키지 기준

백엔드는 단일 `qtai-server` 안에서 도메인을 분리한다.

| 패키지 | 책임 |
| --- | --- |
| `com.qtai.gatewayauth` | JWT, Google OAuth, 인증·인가 공통 처리 |
| `com.qtai.bff` | 화면 단위 응답 조립, 외부 공개 API Controller |
| `com.qtai.bible` | 성경 본문, QT 범위, 해설 C, 묵상·찬양 하위 모듈 |
| `com.qtai.bible.journal` | 묵상 노트, 묵상 달력 |
| `com.qtai.bible.songs` | 찬양 큐레이션, 사용자 찬양 참조 저장 |
| `com.qtai.ai` | DeepSeek 배치, 해설 생성, 편집자 검증, 실행 로그 |
| `com.qtai.simulator` | 시뮬레이터 상태와 클립 메타데이터 |

다른 도메인은 `api/` 하위 Port/DTO만 import할 수 있다. Entity, Service, Repository 직접 import는 금지한다.

---

## 5. 완료 기준

| 항목 | 완료 기준 |
| --- | --- |
| CI | `.github/workflows/qt-ai-ci.yml` 존재 |
| PR | `.github/pull_request_template.md` 존재 |
| API | `apis/bff/openapi.yaml` 위치 확정 |
| 데이터 | `data/bible-sources/README.md` 위치 확정 |
| 백엔드 | `qtai-server` 단일 백엔드 기준 유지 |
| 앱 | `flutter-app` 위치 확정 |

---

## 6. 현재 상태

| 항목 | 상태 |
| --- | --- |
| PR 템플릿 | `.github/pull_request_template.md` 작성 완료 |
| 기본 CI | `.github/workflows/qt-ai-ci.yml` 작성 완료 |
| 기본 구조 기준 | 이 문서에서 v0.1로 신규 작성 |
| 다음 권장 작업 | 실제 Spring Boot/Flutter 프로젝트 골격 생성 |
