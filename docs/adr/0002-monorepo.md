# ADR-0002: Monorepo + Gradle multi-module

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
MSA에서 service당 별도 git repo (polyrepo)로 가는 표준이 있지만 6명 6주 시연에는 cross-cutting 변경 (예: BaseEntity·event schema·ADR) 동기화 비용이 큼. 1차 HMS는 단일 repo였고 그게 협업에 도움됐음.

## Decision
**Monorepo + Gradle multi-module** (03번 § 5):

\\\
2nd-Team-Project/
├── settings.gradle.kts (include "gateway", "bff-aggregator", ...)
├── build.gradle.kts (root: BOM 픽스 + Spotless + ArchUnit)
├── gateway/
├── bff-aggregator/
├── auth-service/
├── bible-service/
├── ai-service/
├── journal-service/
├── apis/{service}/openapi.yaml      # 계약 1곳 관리
├── events/schema/*.json             # 이벤트 schema 1곳
├── docs/                            # 문서·ADR 1곳
└── helm/                            # Chart 1곳
\\\
"@ 
  @"
- **Polyrepo (service당 1 repo)**: 6 repo 동기화 비용 ↑. cross-cutting 변경(BaseEntity 갱신·event schema 추가)이 6 PR로 분산 → 머지 누락 위험
- **단일 module (모놀리스)**: ADR-0001 부정
- **monorepo + 단일 module**: service 간 타이트 커플링 → ADR-0001 무력화

## Alternatives
**긍정:**
- cross-cutting 변경 1 PR로 끝
- BaseEntity·이벤트 schema·ADR 1곳 관리 (단일 진실의 출처)
- 6명이 같은 git history 공유 → 학습 곡선 ↓

**부정:**
- 빌드 시간 ↑ (CI에서 변경된 모듈만 build하는 incremental build 필요 — Gradle build cache로 해결)
- module 간 의존성 우발적 발생 위험 (ArchUnit 룰로 차단 — 07번 § 11)

## Consequences
ArchUnit 룰: \com.qtai.journal..\ 가 \com.qtai.auth..\·\com.qtai.bible..\·\com.qtai.ai..\ 패키지에 의존 X (Database per Service 강제 — 07번 § 11)

## 검증 방법
