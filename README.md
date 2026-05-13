# 📖 QT-AI — 큐티 AI 앱 (2차 팀 프로젝트)

> Flutter 모바일 + Spring Boot MSA + AI 코칭형 묵상 도우미

## 🎯 프로젝트 한 줄 정의

성경 구절 클릭 한 번으로 **한/영 본문 + 주석을 동시에 보여주고**, 큐티 A~D형(관찰·해석·적용·결단) 패턴을 따라 **소크라테스식 꼬리 질문으로 코칭하는 AI 묵상 앱** (SSE 스트리밍).

## 🧱 기술 스택

| 영역 | 스택 |
| --- | --- |
| 모바일 | Flutter (Sliver 기반 Sync Scroll, RiverPod, DIO) |
| API Gateway | Spring Cloud Gateway (JWT 검증, SSE 패스스루) |
| 백엔드 (MSA) | Spring Boot 3.3 / Java 21 (Gateway·BFF·Bible·AI — Auth·Journal 독립 서비스 제거) |
| 메시징 | Kafka (이벤트 소싱 + Saga 보상 트랜잭션) |
| AI/RAG | Spring Boot 3.3 + DeepSeek API(OpenAI 호환, RestClient, SSE) + ChromaDB |
| 데이터 | MySQL · Redis |
| 인프라 | Kubernetes (Minikube) + Helm |
| 관측성 | Loki · Prometheus · Jaeger |
| CI/CD | GitHub Actions → GHCR → Helm Upgrade |

## 📅 일정 (총 25 영업일, 5/12 화 ~ 6/17 수)

| 주차 | 기간 | 일수 | 목적 |
| --- | --- | --- | --- |
| **W0** | 5/8 금~5/11 월 | 4 | 킥오프 + 문서 폭주 + 학습 워크숍 |
| **W1** | 5/12 화~5/22 금 | 5 | 🔒 **Foundation Lock-in** 5항목 |
| **W2** | 5/26 화~5/29 금 | 4 | 서비스별 핵심 도메인 병렬 (5/25 부처님오신날 휴) |
| **W3** | 6/1 월~6/5 금 | 4 | Kafka 통합 + E2E 1차 (6/3 지방선거 휴) |
| **W4** | 6/8 월~6/12 금 | 5 | 마감·통합·시연 환경·부하 테스트 |
| **W5** | 6/15 월~6/17 수 | 3 | 6/15 PPT, 6/16 리허설×2, **6/17 발표** |

평일 09:00~18:00 (점심 13~14, 9~11 강사 수업, 코어 작업 6h/일).

## 👥 팀 구성 (6명, MSA Service-Owner 모델)

| 담당자 | 역할 | 담당 |
| --- | --- | --- |
| **강태오** | Lead + DevOps 총괄 | BFF Aggregator + 공유 레이어 + Gateway + K8s/Helm/CI |
| **이지윤** | Bible Owner | Bible Service (성경·주석·QT·묵상일지 통합) |
| **김태혁** | AI Owner | AI Service (큐티 A~D 프롬프트, RAG 보조) |
| **강상민** | AI/RAG Owner (팀 내 기술적 깊이 최고) | AI/RAG Service — DeepSeek·RAG·SSE·프롬프트 인젝션 방어·신학 가드레일 |
| **이승욱** | Bible + Kafka Owner | Bible Service 묵상일지 통합 (이벤트 소싱, 컨슈머 멱등성) |
| **김지민** | Flutter Owner | Flutter App (Sliver Sync Scroll, AI 대화, 알림) |

> 2026-05-12 기준: Auth Service와 Journal Service는 독립 서비스로 두지 않는다. 묵상 기록 API는 Bible Service에서 담당한다.

## 🔒 W1 Foundation Lock-in (기능보다 우선)

5/22(금) 18:00 시점에 5/5 모두 ✅ 가 아니면 W2 진입 금지. 기능 0줄이어도 5가지가 끝나면 W1 성공.

1. 서비스 경계 확정 (강태오)
2. API 계약 OpenAPI 동결 (전원)
3. Kafka 토픽·이벤트 스키마 확정 (강태오 + 이승욱)
4. K8s 스켈레톤 배포 (강태오 + 전원)
5. 관측성 기본기 — Loki·Prometheus·Jaeger (강태오 + 전원)

## 📚 문서 인덱스

| # | 문서 | 상태 |
| --- | --- | --- |
| 01 | [프로젝트_계획서](./01_프로젝트_계획서.md) | ⚠️ v1.3, 구버전 항목 정리 중 |
| 02 | [ERD_문서](./02_ERD_문서.md) | ✅ v1.6 |
| 03 | [아키텍처_정의서](./03_아키텍처_정의서.md) | ✅ v1.6 |
| 04 | [API_명세서](./04_API_명세서.md) | ✅ v1.5 |
| 05 | [요구사항_정의서](./05_요구사항_정의서.md) | ✅ v1.4 |
| 05-A | [보안_명세서](./05_보안_명세서.md) | ✅ v1.0 |
| 06 | [DevOps_운영_매뉴얼](./06_DevOps_운영_매뉴얼.md) | ✅ v1.0 |
| 07 | [테스트_전략](./07_테스트_전략.md) | ⚠️ v1.0, 정합성 패치 중 |
| 08 | [프론트엔드_Flutter_가이드](./08_프론트엔드_Flutter_가이드.md) | ⚠️ v1.0, 정합성 패치 중 |
| 09 | [AI_프롬프트_운영_가이드](./09_AI_프롬프트_운영_가이드.md) | ✅ v1.1 |
| 10 | [트러블슈팅_FAQ](./10_트러블슈팅_FAQ.md) | ✅ v1.0 |
| 11 | [개발_환경_셋업_가이드](./11_개발_환경_셋업_가이드.md) | ✅ v1.1 |
| 12 | [서비스별_도메인_모델_상세](./12_서비스별_도메인_모델_상세.md) | ⚠️ v1.0, 정합성 패치 중 |
| 13 | [운영_시나리오_시연_가이드](./13_운영_시나리오_시연_가이드.md) | ✅ v1.0 |
| 14 | [팀_협업_규칙_Git_브랜치_전략](./14_팀_협업_규칙_Git_브랜치_전략.md) | ✅ v1.1 |
| 15 | [서비스별_구현_체크리스트](./15_서비스별_구현_체크리스트.md) | ⚠️ v1.0, 정합성 패치 중 |
| 16 | [API_통합_테스트_가이드](./16_API_통합_테스트_가이드.md) | ⚠️ v1.0, 정합성 패치 중 |
| 17 | [데이터_시드_마이그레이션_전략](./17_데이터_시드_마이그레이션_전략.md) | ✅ v1.0 |
| 18 | [코드_품질_게이트](./18_코드_품질_게이트.md) | ✅ v1.0 |
| 19 | [성능_테스트_가이드](./19_성능_테스트_가이드.md) | ✅ v1.0 |
| 20 | [W1_Foundation_실행_가이드](./20_W1_Foundation_실행_가이드.md) | ✅ v1.1 |
| 21 | [프로젝트_회고_템플릿](./21_프로젝트_회고_템플릿.md) | ✅ v1.0 |
| 22 | [기능_명세서](./22_기능_명세서.md) | ✅ v1.2 |
| 23 | [도메인_용어사전](./23_도메인_용어사전.md) | ✅ v1.0 |
| 24 | [회의결정_2026-05-13_오전](./24_회의결정_2026-05-13_오전.md) | ✅ v1.0 |
| — | [DECISIONS.md](./DECISIONS.md) — 단일 기준표 (포트·TTL·Route·Envelope·인프라) | ✅ |
| — | [AGENTS.md](./AGENTS.md) — AI 에이전트 협업 가이드 | ✅ |

> **0~3번 두껍게 정책**: MSA 풀스코프 특성상 W1 Foundation Lock-in을 강제하기 위해 브리프·아키텍처·서비스 경계·API 계약 문서를 우선·중점 작성.

## 📖 학습 자료

- 노션 「기술 블로그」 → **6. MSA** (Docker / Kubernetes / Kafka / WebSocket / SSE / Saga / UseCase) + **플러터** (Sliver / RiverPod / DIO / Clean Architecture / AI 코딩 도구)
- 1차 프로젝트 (HMS) 회고: 트랜잭션 누락 / 메서드 환각 / 평문 시크릿 → MSA 가드레일로 박제 ([01번 § 9.3](./01_프로젝트_계획서.md))

## 🔗 관련 저장소

- **1차 프로젝트 (HMS)**: https://github.com/Tae0072/hms
- **템플릿 시스템 (v2)**: https://github.com/Tae0072/team-project-templates

---

🤖 작성: AI 도구 + 강태오 (Lead)
