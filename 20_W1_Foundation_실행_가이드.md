# QT-AI (큐티 AI 앱) — W1 Foundation 실행 가이드 v1.1

> **문서 버전:** v1.1
> **작성일:** 2026-05-08
> **연관 문서:** [11_개발_환경_셋업_가이드 v1.1](./11_개발_환경_셋업_가이드.md) / [15_서비스별_구현_체크리스트 v1.0](./15_서비스별_구현_체크리스트.md) / [14_팀_협업_규칙_Git_브랜치_전략 v1.0](./14_팀_협업_규칙_Git_브랜치_전략.md)
> **owner:** 강태오 (Lead)
> **목적:** W1 첫날(5/12 화)부터 W1 종료(5/22 금)까지 6명이 겹치지 않고 Foundation을 쌓는 구체적 행동 순서. "오늘 뭐 해요?"를 없애기 위한 step-by-step.

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-08 | 강태오 (Lead) | 초기 작성 |
| v1.1 | 2026-05-13 | Codex | 2026-05-12 결정 반영 — 4모듈 기준, Gateway Auth, Bible Service Journal 통합, DeepSeek 기준으로 W1 작업 지시 정리 |

---

## 목차

1. [W1 시작 전 확인사항 (5/12 오전 9시)](#1-w1-시작-전-확인사항-512-오전-9시)
2. [Day 1 — 5/12 화 (킥오프 + 환경 통일)](#2-day-1--512-화-킥오프--환경-통일)
3. [Day 2~3 — 5/13~5/14 (서비스 골격 구축)](#3-day-23--513514-서비스-골격-구축)
4. [Day 4~5 — 5/15~5/16 (핵심 도메인 구현)](#4-day-45--515516-핵심-도메인-구현)
5. [Day 6~7 — 5/19~5/20 (통합 연결)](#5-day-67--519520-통합-연결)
6. [Day 8~9 — 5/21~5/22 (Lock-in 검증)](#6-day-89--521522-lock-in-검증)
7. [W1 종료 기준 체크리스트](#7-w1-종료-기준-체크리스트)

---

## 1. W1 시작 전 확인사항 (5/12 오전 9시)

### 1.1 환경 사전 확인 (5/12 오전 오기 전에)

각자 11번 문서의 셋업 체크리스트 완료 여부 확인:

```
□ git clone 완료
□ java -version → 21
□ minikube status → Running
□ docker --version → 4.x
□ (김지민) fvm flutter --version → 3.24.5
□ (강상민) ai-service `./gradlew build -x test` → BUILD SUCCESSFUL
```

미완료 시 5/12 오전 중 강태오와 즉시 페어로 해결.

### 1.2 W1 킥오프 (5/12 화 10:00 — 30분)

| 순서 | 내용 | 진행 |
| --- | --- | --- |
| 1 (5분) | W1 목표 공유 (Foundation Lock-in) | 강태오 |
| 2 (10분) | 역할 최종 확인 + 페어 합의 사항 전달 | 강태오 |
| 3 (10분) | 질문 + 막힌 것 즉시 해소 | 전원 |
| 4 (5분) | Slack 스탠드업 채널 + 일일 보고 형식 시연 | 강태오 |

**킥오프 후 각자 자리에서 즉시 시작.**

---

## 2. Day 1 — 5/12 화 (킥오프 + 환경 통일)

### 강태오 (Lead, Gateway, DevOps)

```
10:30  Gradle root settings.gradle.kts + 4 module build.gradle.kts 초기화
12:00  ./gradlew build -x test → BUILD SUCCESSFUL (빈 모듈 4개)
13:00  GitHub master/dev 브랜치 기준 Gradle wrapper commit + push
14:00  K8s namespace qtai + Helm infra (MySQL·Redis·Kafka) 기동
16:00  Gateway Spring Cloud Gateway 라우팅 4개 서비스 영역 설정
17:30  .github/workflows/ci.yml Gradle build job 초기 구성
```

### 이지윤 (Bible Service)

```
10:30  git pull → Gradle wrapper 확인
11:00  bible-service/ 성경·주석 패키지 구조 생성 (12번 § Bible 기준)
13:00  Flyway V1__create_bible_tables.sql (BOOKS·KR_BIBLE·EN_BIBLE) 작성
15:00  Book·Verse 도메인 엔티티 구현
17:00  Bible 조회 UseCase 골격 + 단위 테스트 시작
```

### 강상민 (AI Service)

```
10:30  git pull + ai-service `gradle wrapper --gradle-version=8.10` (첫 1회만)
11:00  `./gradlew build -x test` → BUILD SUCCESSFUL + DEEPSEEK_API_KEY 환경변수 확인
12:00  ChromaDB K8s 배포 + collection qtai_corpus 생성
14:00  임베딩 모델 다운로드 확인 (paraphrase-multilingual-mpnet-base-v2)
15:00  RAG 시드 5개 문서 큐레이션 + Spring/CLI 시드 실행
17:00  시스템 프롬프트 4종 초안 작성 (step_a ~ step_d)
```

### 이승욱 (Bible Service · Journal/Kafka)

```
10:30  git pull → Gradle wrapper 확인
11:00  bible-service/ journal 패키지 구조 생성
13:00  Flyway V1 migration (JOURNALS·JOURNAL_EVENTS)
15:00  Journal·JournalEvent 도메인 엔티티 구현
17:00  Kafka consumer 설정 + CreateJournalUseCase 골격
```

### 김태혁 (Bible Service)

```
10:30  git pull → Gradle wrapper 확인
11:00  ai-service/ RAG 보조 패키지 구조 확인
13:00  PromptTemplate·RagSource 모델 검토
15:00  KJV·Matthew Henry·팀 작성 더미 자료 seed 범위 확인
17:00  DeepSeek 프롬프트 템플릿 리뷰 보조
```

### 김지민 (Flutter)

```
10:30  git pull → flutter-app/ 디렉토리 확인
11:00  fvm flutter create qtai_app (flutter-app/ 디렉토리)
12:00  pubspec.yaml 의존성 설치 (08번 § 2.3)
13:00  .fvmrc 버전 고정 + commit
14:00  build_runner build → 0 error 확인
15:00  go_router 5 화면 라우팅 골격
17:00  flutter analyze → 0 issue 확인
```

---

## 3. Day 2~3 — 5/13~5/14 (서비스 골격 구축)

### 공통

```
매일 오전 9시  Slack #daily-standup 스탠드업 작성
막혔을 때      30분 초과 시 강태오 ping
```

### 강태오

```
5/13 오전  AuthFilter (JWT 검증 → X-User-Id 헤더) 구현
5/13 오후  Gateway → Gateway Auth/Bible 라우팅 curl 검증
5/14 오전  NetworkPolicy default-deny + 서비스 허용 정책
5/14 오후  K8s Secret 4종 등록 (deepseek, mysql, jwt-keys, google-oauth)
```

### 이지윤

```
5/13 오전  Book/Verse 조회 UseCase 구현 완료 + 단위 테스트 통과
5/13 오후  KR/EN 본문 조회 API DTO 정리
5/14 오전  Commentary 조회 + Redis cache 키 정책 구현
5/14 오후  Bible Service 통합 테스트 골격
```

### 강상민

```
5/13 오전  DeepSeekStreamService + 4분 timeout + semaphore 10
5/13 오후  AiSession·Turn 도메인 엔티티 + Flyway V1 migration
5/14 오전  강태오 신학 검수 30분 페어 (시스템 프롬프트 4종)
5/14 오후  ProcessTurnUseCase 골격 (인젝션 방어 계층 1 구현)
```

### 이승욱

```
5/13 오전  CreateJournalUseCase @Transactional + 단위 테스트
5/13 오후  Kafka consumer 설정 (manual ack + at-least-once)
5/14 오전  ai.session.completed consume → AutoCreateFromSessionUseCase
5/14 오후  UNIQUE 제약 (session_id) 확인 + 멱등성 테스트
```

### 김태혁

```
5/13 오전  KR_BIBLE 시드 로드 (BibleDataLoader 구현)
5/13 오후  /bible/books GET + /bible/books/{code}/chapters/{ch}/verses/{v} GET
5/14 오전  verse_exists API 구현 (강상민 AI 환각 검증용)
5/14 오후  인덱스 idx_kr_bible_bcv 생성 + Redis 캐시 설정
```

### 김지민

```
5/13 오전  Riverpod AuthState + dioProvider + tokenStorage 구현
5/13 오후  AuthInterceptor (401 → Refresh → retry)
5/14 오전  flutter_secure_storage Refresh Token 저장/읽기/삭제
5/14 오후  로그인 화면 UI + 폼 유효성 검증
```

---

## 4. Day 4~5 — 5/15~5/16 (핵심 도메인 구현)

### 강태오

```
5/15 오전  BFF Aggregator 기본 집계 (/me/dashboard 병렬 호출)
5/15 오후  Kafka 토픽 8종 자동 생성 스크립트 검증
5/16 오전  Prometheus scrape 설정 + Grafana 기본 대시보드
5/16 오후  CI yml 전체 구성 (build + Spectral + flutter analyze)
```

### 이지윤

```
5/15 오전  /auth/login POST endpoint + RestAssured integration test
5/15 오후  /auth/refresh POST endpoint + integration test
5/16 오전  /auth/me GET endpoint
5/16 오후  ProblemDetail ErrorCode 매핑 (INVALID_CREDENTIALS 등)
```

### 강상민

```
5/15 오전  SSE 4 이벤트 발행 구현 (token·turn_completed·error·end)
5/15 오후  검증 2종 (인젝션 누출·환각 구절 — verse_exists API 호출)
5/16 오전  golden-set 10건 + injection-set 10건 작성
5/16 오후  tests/eval/run_eval.py 실행 가능 상태
```

### 이승욱

```
5/15 오전  UpdateJournalUseCase + 낙관적 락
5/15 오후  ListJournalsUseCase (페이지네이션 + 삭제 필터)
5/16 오전  notification.requested Kafka 발행
5/16 오후  journal.creation.failed 보상 발행
```

### 김태혁

```
5/15 오전  성경 데이터 전체 로드 확인 (31,102절 count 검증)
5/15 오후  /bible/books/{code}/chapters/{ch} GET
5/16 오전  오늘의 구절 API 구현
5/16 오후  통합 테스트 (verse_exists 30건 정합성)
```

### 김지민

```
5/15 오전  대시보드 화면 UI + BFF mock API 연동
5/15 오후  go_router 인증 가드 (isAuthenticated → redirect)
5/16 오전  flutter test 1건 이상 통과 확인
5/16 오후  flutter analyze 0 issue + build_runner clean
```

---

## 5. Day 6~7 — 5/19~5/20 (통합 연결)

> **5/17~5/18 주말 — 휴식.**

### 5/19 월 — 서비스 간 첫 연결

**전원 목표:** Gateway를 통해 Auth·Bible 서비스에 실제 요청 성공.

```bash
# 오전 11:00 강태오가 공개 테스트
TOKEN=$(curl -s http://$(minikube ip):30080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"tester@qtai.dev","password":"Demo1234!"}' \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['accessToken'])")

curl http://$(minikube ip):30080/api/v1/bible/books/GEN/chapters/1/verses/1 \
  -H "Authorization: Bearer $TOKEN"
# 성공 시 전원에게 알림
```

### 5/20 화 — AI Service 1턴 E2E

**강상민 + 강태오 페어:**
```bash
# AI 세션 생성
SESSION=$(curl -s -X POST http://$(minikube ip):30080/api/v1/ai/sessions \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"bookCode":"GEN","chapter":1,"verse":1}' | python3 -c "...")

# 1턴 SSE 수신 확인 (curl --no-buffer)
curl -N http://$(minikube ip):30080/api/v1/ai/sessions/$SESSION/turns \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"step":"A","content":"이 구절에서 누가 등장하나요?"}'
# event: token → event: turn_completed → event: end 확인
```

### 각 역할 5/19~5/20 병렬 작업

| 역할 | 5/19 | 5/20 |
| --- | --- | --- |
| 강태오 | Gateway AuthFilter 통합 검증 | AI SSE buffering 우회 filter |
| 이지윤 | Google OAuth 구현 시작 | Auth ↔ Gateway X-User-Id 통합 |
| 강상민 | DeepSeek mock → 실제 API 전환 | 1턴 E2E 완성 |
| 이승욱 | Kafka consumer 통합 테스트 | notification.requested E2E |
| 김태혁 | Bible ↔ AI Service verse_exists 연결 | 캐시 히트율 확인 |
| 김지민 | Flutter ↔ Auth API 실제 연동 | STOMP client 골격 |

---

## 6. Day 8~9 — 5/21~5/22 (Lock-in 검증)

### 5/21 수 — 최종 구현 마무리

각자 자신의 W1 체크리스트 (15번) 완료 목표. 미완성 항목 오전 중 Slack 공유.

### 5/22 금 — W1 Lock-in 전체 검증 (종일)

| 시간 | 내용 | 진행 |
| --- | --- | --- |
| 10:00~12:00 | CI 전체 통과 확인 (Gradle build + Spectral + Flutter test) | 강태오 |
| 13:00~14:30 | 통합 E2E 1회 (Gateway → AI → Kafka → Journal → STOMP) | 강태오 + 강상민 |
| 14:30~15:00 | 강태오 신학 검수 (시스템 프롬프트 4종) | 강태오 ↔ 강상민 |
| 15:00~16:00 | 각자 W1 체크리스트 최종 점검 | 전원 (개별) |
| 16:00~17:00 | W1 회고 (15분) + W2 목표 공유 (15분) | 강태오 진행 |

---

## 7. W1 종료 기준 체크리스트

**5/22 금 17:00까지 모두 ✅:**

**인프라:**
- [ ] `./gradlew build -x test` → BUILD SUCCESSFUL (4 modules)
- [ ] Minikube 전체 pod Running (MySQL·Redis·Kafka·ChromaDB·4 services)
- [ ] Gateway → 4 서비스 영역 라우팅 curl 검증 통과
- [ ] CI yml → Gradle build + Spectral lint green

**Auth:**
- [ ] `/auth/login` → 200 + JWT (RestAssured integration test)
- [ ] `/auth/refresh` → 200 + Rotation (새 pair 발급)

**Bible:**
- [ ] KR_BIBLE 31,102절 시드 완료
- [ ] `/bible/books/GEN/chapters/1/verses/1` → 창세기 1:1 본문 응답

**AI:**
- [ ] SSE 1턴 E2E (token → turn_completed → end 이벤트 수신)
- [ ] 강태오 신학 검수 완료

**Kafka:**
- [ ] `ai.session.completed` → Bible Service Journal DRAFT 자동 생성 E2E

**Flutter:**
- [ ] `flutter analyze` 0 issue
- [ ] `flutter test` ALL PASSED
- [ ] 로그인 → 대시보드 진입 (Prism mock 또는 실제 Auth)

**전반:**
- [ ] develop 브랜치 CI green
- [ ] 각자 Slack 스탠드업 5일치 기록

> **80%+ 달성 → W2 진입. 60~79% → 강태오 페어 1회 추가. 60% 미만 → 범위 조정 회의 (cut 항목 결정).**
