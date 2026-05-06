# 📖 QT-AI — 큐티 AI 앱 (2차 팀 프로젝트)

> Flutter 모바일 + Spring Boot MSA + AI 코칭형 묵상 도우미

## 🎯 프로젝트 한 줄 정의

성경 구절 클릭 한 번으로 **한/영 본문 + 주석을 동시에 보여주고**, 큐티 A~D형(관찰·해석·적용·결단) 패턴을 따라 **소크라테스식 꼬리 질문으로 코칭하는 AI 묵상 앱**.

## 🧱 기술 스택

| 영역 | 스택 |
| --- | --- |
| 모바일 | Flutter (Android/iOS) |
| API Gateway | Spring Cloud Gateway |
| 백엔드 (MSA) | Spring Boot · BFF Aggregator · Auth · Bible · AI · Journal |
| 메시징 | Kafka (이벤트 소싱 + Saga) |
| AI/RAG | Anthropic Claude API + ChromaDB |
| 데이터 | MySQL · Redis |
| 인프라 | Kubernetes (Minikube) + Helm |
| 관측성 | Loki · Prometheus · Jaeger |
| CI/CD | GitHub Actions → Docker Hub → Helm Upgrade |

## 📅 일정

- **5/6 (화)** 주제 선정 ✅
- **5/7~5/10** W0 킥오프 + 문서 폭주 (01~10 v1)
- **5/11~5/29** W1~W3 개발 (3주)
  - **W1**: 🔒 Foundation Lock-in 5항목 강제
  - **W2**: 서비스별 도메인 병렬 구현
  - **W3**: Kafka 이벤트 통합 + E2E + 부하 테스트
- **6/1~6/5** W4 발표·시연 준비

## 👥 팀 구성

6명 + 전원 AI 에이전트(Claude Code / Cursor) 활용. 각자 1 service end-to-end 책임.

| 담당자 | 서비스 |
| --- | --- |
| Lead | BFF Aggregator + 공유 레이어 + Gateway |
| Dev A | Auth/User Service |
| Dev B | Bible Service |
| Dev C | AI/RAG Service |
| Dev D | Journal Service |
| Dev E | Flutter App |
| DevOps/QA | K8s · Kafka · Helm · CI/CD · Observability |

> 인원 배분(A안/B안)은 W0 킥오프(5/7 수)에서 확정 — 자세한 내용은 [01_프로젝트_계획서.md § 6](./01_프로젝트_계획서.md#6-인력-배치표-resource-plan) 참조.

## 📚 문서 인덱스

| # | 문서 | 상태 |
| --- | --- | --- |
| 01 | [프로젝트_계획서](./01_프로젝트_계획서.md) | ✅ v1.0 |
| 02 | ERD 문서 | ⏳ 작성 예정 |
| 03 | 아키텍처 정의서 | ⏳ 작성 예정 |
| 04 | API 명세서 | ⏳ 작성 예정 |
| 05~21 | … | ⏳ 작성 예정 |

> **0~3번 문서를 두껍게**: MSA 풀스코프 특성상 W1 Foundation Lock-in을 강제하기 위해 브리프·아키텍처·서비스 경계·API 계약 문서를 우선·중점 작성.

## 🔗 관련 저장소

- **1차 프로젝트 (HMS)**: https://github.com/Tae0072/hms
- **템플릿 시스템 (v2)**: https://github.com/Tae0072/team-project-templates

---

🤖 작성: Claude (Anthropic) + Lead
