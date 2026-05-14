# 📖 QT-AI — 큐티 AI 앱 (2차 팀 프로젝트)

> Flutter 모바일 + Spring Boot **Modular Monolith** + AI 코칭형 묵상 도우미 (2026-05-14 v2.0)

## 🎯 프로젝트 한 줄 정의

성경 구절 클릭 한 번으로 **한/영 본문 + 해설을 동시에 보여주고**, 큐티 A~D형(관찰·해석·적용·결단) 패턴을 따라 **AI가 자체 생성한 해설로 묵상을 돕는 앱** (SSE 스트리밍).

## 🧱 기술 스택 (v2.0 — 2026-05-14)

| 영역 | v1 (시연 6/17) | v2 (분리 시 도입, ADR-0016) |
| --- | --- | --- |
| 모바일 | Flutter (Sliver Sync Scroll, RiverPod, DIO) | 동일 |
| 백엔드 | **단일 `qtai-server` (Modular Monolith)** Spring Boot 3.3 / Java 21 — 도메인 패키지 6개(`gatewayauth`·`bff`·`bible`·`ai`·`journal`·`simulator`) | AI 도메인 우선 분리 → `qtai-ai-service` |
| 도메인 간 통신 | **Spring `ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)`** | Kafka KRaft + Schema Registry |
| AI | DeepSeek API (OpenAI 호환, RestClient, SSE) — RAG·ChromaDB·벡터 DB 제외 (ADR-0013) | 동일 (AI 도메인이 별도 컨테이너로) |
| AI 출처 컨텍스트 | 사전 적재 `bible_explanations` row 참조 (RAG 폐기) | 동일 |
| 데이터 | MySQL (단일 DB `qtai_db`, 도메인별 테이블 prefix) · Redis | DB per Service로 schema 분리 |
| 인프라 | **Docker Compose** | Kubernetes (Minikube) + Helm |
| 관측성 | Loki · Prometheus · Jaeger | 동일 (분산 트레이싱 강화) |
| CI/CD | GitHub Actions + Spring Modulith + ArchUnit (ADR-0015) | + GHCR + Helm Upgrade |
| QT 본문 소싱 | 성서 유니온 19:00 cron 스크래핑 (ADR-0014, 좌표 메타데이터만) | 동일 |

## 📅 일정 (총 25 영업일, 5/12 화 ~ 6/17 수)

| 주차 | 기간 | 일수 | 목적 |
| --- | --- | --- | --- |
| **W0** | 5/8 금~5/11 월 | 4 | 킥오프 + 문서 폭주 + 학습 워크숍 |
| **W1** | 5/12 화~5/22 금 | 5 | 🔒 **Foundation Lock-in v2** 5항목 (단일 빌드 / 도메인 경계 / OpenAPI / 단일 DB / 관측성) |
| **W2** | 5/26 화~5/29 금 | 4 | 도메인 핵심 구현 + **강사 면담(ADR-0016 트리거)** (5/25 부처님오신날 휴) |
| **W3** | 6/1 월~6/5 금 | 4 | 통합 테스트 + Flutter 합류 (6/3 지방선거 휴) |
| **W4** | 6/8 월~6/12 금 | 5 | (분기) v2 AI 도메인 분리 OR v1 안정화 + 발표 자료 |
| **W5** | 6/15 월~6/17 수 | 3 | 6/15 PPT, 6/16 리허설×2, **6/17 발표** |

평일 09:00~18:00 (점심 13~14, 9~11 강사 수업, 코어 작업 6h/일).

## 👥 팀 구성 (6명, Bible팀 3인 + AI/Simulator/Lead) — 2026-05-14 재배치

| 담당자 | 역할 | 담당 |
| --- | --- | --- |
| **강태오** | Lead · DevOps · 전체 조율 (단일 파트 고정 X) | Spring Modulith + ArchUnit PR 검증 / 인프라 / W2 강사 면담 / W4 분기 |
| **강상민** | AI 도메인 단독 주도 (`com.qtai.ai`) | DeepSeek SSE · 해설 생성 파이프라인 · 편집자 에이전트 · 검증 메커니즘 정의 |
| **김태혁** ([@xogurrh012](https://github.com/xogurrh012)) | 시뮬레이터 단독 (`com.qtai.simulator`) | 본문 좌표 → 장면 시각화 (스프라이트 검토) · 데이터 모델·라이선스 일임 |
| **이지윤** | Bible팀 (3인 중 1) | Bible 도메인 → Flutter → 인증 → 관리자 페이지 / 편집자 에이전트 보조 큐레이션 / 새번역 라이선스 확인 |
| **이승욱** | Bible팀 (Journal 주도) · **Flutter 빌드 책임자(시연 6/17)** | Journal 도메인 (이벤트 소싱) → Flutter 빌드 → 인증 → 관리자 페이지 |
| **김지민** | Bible팀 (3인 중 1) | Bible 도메인 → Flutter UI → 인증 → 관리자 페이지 |

> 2026-05-14 회의 재배치 (DECISIONS.md §0): AI 서버 팀장 강태오 → **강상민**으로 이관. 김지민 Flutter 단독 → Bible팀 합류. 김태혁 AI/RAG 보조 → 시뮬레이터 단독. Bible팀 3인이 Bible 프로토타입 → Flutter → 인증 → 관리자 페이지 일괄 진행.

## 🔒 W1 Foundation Lock-in v2 (기능보다 우선)

5/22(금) 18:00 시점에 5/5 모두 ✅ 가 아니면 W2 진입 금지.

1. **모놀리식 빌드 통과** — `./gradlew :qtai-server:build` 성공, `/actuator/health` UP (강태오)
2. **도메인 패키지 import 검증** — Spring Modulith `verifyModuleBoundaries()` 통과, 다른 도메인 import 0건 (강태오 + 전원)
3. **OpenAPI 3종 동결** — `apis/{ai,bff,bible}/openapi.yaml` Spectral lint 통과 + Prism mock 가동. `apis/auth`·`apis/journal`은 폐기 (전원)
4. **단일 DB Flyway 적용** — `qtai_db`에 도메인별 prefix 테이블 모두 적용. `bible_today_qt_schedule`에 cron 19:00 1회 수집 성공 (Bible팀)
5. **관측성** — Loki(로그) + Prometheus(메트릭) + Jaeger(트레이스) 단일 프로세스 기준 작동 (강태오 + 전원)

## 📚 문서 인덱스 (v2.0 — 2026-05-14)

| # | 문서 | 상태 |
| --- | --- | --- |
| — | [DECISIONS.md](./DECISIONS.md) — 단일 기준표 (포트·TTL·Route·Envelope·인프라·저작권·팀 배치) | ✅ v2.0 |
| — | [AGENTS.md](./AGENTS.md) — AI 에이전트 협업 가이드 | ✅ v2.0 |
| 00 | [개발_일정_총괄표](./00_개발_일정_총괄표.md) | ⚠️ 본문 v1, 상단 v2.0 banner |
| 01 | [프로젝트_계획서](./01_프로젝트_계획서.md) | ⚠️ 본문 v1, 상단 v2.0 banner |
| 02 | [ERD_문서](./02_ERD_문서.md) | ✅ v2.0 |
| 03 | [아키텍처_정의서](./03_아키텍처_정의서.md) | ✅ v2.0 |
| 04 | [API_명세서](./04_API_명세서.md) | ✅ v2.0 (sources / explanations/commentary) |
| 05 | [요구사항_정의서](./05_요구사항_정의서.md) | ⚠️ 본문 v1, 상단 v2.0 banner |
| 05-A | [보안_명세서](./05_보안_명세서.md) | ⚠️ 본문 v1, 상단 v2.0 banner |
| 06 | [DevOps_운영_매뉴얼](./06_DevOps_운영_매뉴얼.md) | ✅ v2.0 |
| 09 | [AI_프롬프트_운영_가이드](./09_AI_프롬프트_운영_가이드.md) | ✅ v2.0 |
| 11 | [개발_환경_셋업_가이드](./11_개발_환경_셋업_가이드.md) | ✅ v2.0 |
| 14 | [팀_협업_규칙_Git_브랜치_전략](./14_팀_협업_규칙_Git_브랜치_전략.md) | ⚠️ 본문 v1, 상단 v2.0 banner |
| 15 | [서비스별_구현_체크리스트](./15_서비스별_구현_체크리스트.md) | ⚠️ 본문 v1, 상단 v2.0 banner |
| 17 | [데이터_시드_마이그레이션_전략](./17_데이터_시드_마이그레이션_전략.md) | ✅ v2.0 (RAG 폐기, 본문 텍스트 적재 흐름) |
| 18 | [코드_품질_게이트](./18_코드_품질_게이트.md) | ✅ v2.0 (§1.5 Spring Modulith + ArchUnit) |
| 20 | [W1_Foundation_실행_가이드](./20_W1_Foundation_실행_가이드.md) | ✅ v2.0 |
| 22 | [기능_명세서](./22_기능_명세서.md) | ✅ v2.0 (FS-12 시뮬레이터 + 해설 리네이밍) |
| docs/adr/0001 | MSA → **Modular Monolith** | ✅ 갈아엎음 |
| docs/adr/0003 | DB per Service → **단일 DB + 도메인 prefix** | ✅ 갈아엎음 |
| docs/adr/0004 | 이벤트 소싱 — v1 in-process / v2 Kafka | ✅ 갱신 |
| docs/adr/0007 | 멱등성 UNIQUE — v1 in-process / v2 Kafka | ✅ 갱신 |
| docs/adr/0013 | **RAG / 벡터 DB / 엘라스틱서치 제외** (신설) | ✅ 신설 |
| docs/adr/0014 | **QT 본문 일일 스크래핑 (성서 유니온 19:00)** (신설) | ✅ 신설 |
| docs/adr/0015 | **PR 검증 = Spring Modulith + ArchUnit** (신설) | ✅ 신설 |
| docs/adr/0016 | **v2 MSA Migration Plan** (신설) | ✅ 신설 |

> **충돌 시 우선순위:** DECISIONS.md > ADR > AGENTS.md > 도메인별 문서. `apis/auth`·`apis/journal`은 폐기 (각 디렉토리의 `DEPRECATED.md` 참조).

## 📖 학습 자료

- 노션 「기술 블로그」 → **Modular Monolith / Spring Modulith / Domain Boundary** + **플러터** (Sliver / RiverPod / DIO / Clean Architecture)
- 1차 프로젝트 (HMS) 회고: 트랜잭션 누락 / 메서드 환각 / 평문 시크릿 → v2.0 가드레일로 박제 (Spring Modulith + ArchUnit + PR 자동 차단, ADR-0015)

## 🔗 관련 저장소

- **1차 프로젝트 (HMS)**: https://github.com/Tae0072/hms
- **템플릿 시스템 (v2)**: https://github.com/Tae0072/team-project-templates
- **이 레포 (문서)**: https://github.com/Tae0072/2nd-Team-Project
- **실제 구현 레포**: https://github.com/Tae0072/QT-AI-2nd-Team-Project

---

🤖 작성: AI 도구 + 강태오 (Lead) · 2026-05-14 v2.0
