# QT-AI 개인 공식 일정표 - 김태혁

> 이 파일 하나만 읽고도 본인 작업을 시작할 수 있도록 최신 결정, 작업 범위, 일정, 검증 명령을 모두 포함한다.
> 기준일: 2026-05-13 / 기준 결정: 2026-05-13 오전 회의 + 4서비스 재정렬

## 1. 내 역할

- 담당자: 김태혁
- 역할: AI/RAG Service - Prompt/RAG 보조 Owner
- 개인 작업 폴더: `workspaces/DevB_김태혁/`
- 기본 브랜치 흐름: feature/{name}-{task} -> dev PR -> 리뷰 -> squash merge

## 2. 반드시 지킬 최신 결정

- 백엔드는 gateway, bff-aggregator, bible-service, ai-service 4개 서비스만 사용한다.
- 인증은 Gateway Auth 모듈에서 처리한다. 독립 Auth Service를 만들지 않는다.
- 묵상일지 Journal은 Bible Service 내부 도메인이다. 독립 Journal Service를 만들지 않는다.
- LLM은 DeepSeek API(OpenAI 호환) 기준이다. 구 Anthropic SDK나 Claude 고정 코드는 만들지 않는다.
- Java 21, Spring Boot 3.3.x, Gradle Kotlin DSL, MySQL 8.0, Kafka KRaft, Jaeger를 고정한다.
- Kafka envelope는 data 필드만 사용한다. payload 키는 사용하지 않는다.
- 에러 응답은 RFC 7807 ProblemDetail(application/problem+json)로 통일한다.
- 성경 데이터는 KJV, 개역한글, Matthew Henry 주석만 허용 범위로 다룬다. 개역개정, ESV, NIV는 금지다.
- 오늘 QT는 MVP에서 하루 1구절이며 `verseStart == verseEnd`로 전달한다.
- AI 질문과 묵상 기록은 오늘 QT 본문에서만 가능하다. 일반 성경 화면은 읽기 전용이다.
- Journal은 `POST /api/v1/journals/today`로 오늘 DRAFT를 만들거나 조회한다. 자유 본문 `POST /api/v1/journals`는 만들지 않는다.
- Journal 4필드(`felt`, `memorableVerse`, `application`, `prayer`)는 별도 저장 버튼 없이 자동 저장한다. 사용자에게 글자 수 제한을 노출하지 않는다.
- AI 완료 이벤트는 새 Journal 생성이 아니라 오늘 Journal에 AI 요약과 `aiSessionId`를 첨부한다.
- 찬양은 AI 추천곡 저장/제거만 MVP에 포함한다. 직접 YouTube URL 입력, 가사/음원/스트리밍 제공은 제외한다.
- 교회 인증은 MVP 기본 제외다. 인증 버튼 자리는 둘 수 있지만, 인증 여부로 앱 사용을 막지 않는다.

## 3. 내가 주로 만지는 경로

- services/ai-service/src/main/java/com/qtai/ai/infrastructure/rag/
- services/ai-service/src/main/java/com/qtai/ai/prompt/
- services/ai-service/src/test/
- 09_AI_프롬프트_운영_가이드.md

## 4. 담당 범위

- QT A/B/C/D 유형과 OBSERVATION/INTERPRETATION/FEELING/APPLICATION 단계 분리 유지
- ChromaDB RAG source metadata, seed corpus, rag_sources SSE payload 지원
- 오늘 QT 본문·저장 설명 source를 AI 답변의 기본 근거로 연결
- PromptTemplate 모델과 injection/golden 평가 세트 관리
- DeepSeek 호출부는 DevC와 인터페이스를 맞추고 공급자 교체를 시도하지 않음
- RAG 출처 없는 신학 단정 답변을 차단하는 검증 규칙 보조
- 참고 QT 앱 화면 흐름 캡처/공유와 찬양 추천 후보 조사 보조

## 5. API와 이벤트 계약 요약

- ChromaDB collection: qtai_corpus
- SSE rag_sources event: source title, passage/ref, snippet, score 포함
- AI prompt는 09번 가이드의 오늘 QT 1회성 질문 MVP와 23번 도메인 용어사전을 따른다.
- AI turn 저장 전 검증 실패 시 완료 turn으로 저장하지 않는다.

## 6. W1 상세 일정 - Foundation Lock-in

- 5/13: PromptTemplate, RagSource, QtStage/JournalType 매핑 초안
- 5/14: KJV/Matthew Henry/더미 한글 주석 seed 범위 정의
- 5/15: 오늘 QT 1회성 질문 시스템 프롬프트 초안과 금지 응답 규칙
- 5/19: golden-set 10건, injection-set 10건 작성
- 5/20: ChromaDB metadata schema와 today QT/explanation source rag_sources 예시 고정
- 5/21: DevC SSE payload와 PromptTemplate 저장 구조 맞춤
- 5/22: eval 실행 방법과 통과 기준 리포트

### W1 PR 머지 조건 (필수)

- [ ] 단위 테스트(Unit Test) 작성 완료 및 `./gradlew :ai-service:test` 로컬 통과
- [ ] 테스트 미작성 항목은 PR 본문에 사유 명시 (단위 테스트 누락 시 REQUEST_CHANGES)

## 7. W2-W5 일정

### W2 - 핵심 도메인 구현
- RAG 검색 client와 prompt assembly 연동
- 출처 기반 응답 검증기 1차 구현
- AI 서비스 테스트 데이터 확장
- 찬양 추천 후보 데이터 구조 초안 공유

### W3 - Kafka/E2E 통합
- Bible verse_exists 또는 본문 조회와 RAG 검증 연동
- 프롬프트 인젝션 회귀 테스트 CI 후보 작성
- 응답 품질 로그 샘플 수집

#### W3 PR 머지 조건 (필수)

- [ ] 통합 테스트(Integration Test) 작성 완료 및 `./gradlew :ai-service:integrationTest` 통과
- [ ] 테스트 커버리지 70% 이상 유지

### W4 - 안정화와 시연 환경
- golden/injection/theology set 확장
- RAG seed 재현 스크립트 정리
- 시연용 안정 응답 샘플 준비

### W5 - 발표와 리허설
- 오늘 QT AI 답변 품질 Q&A 대응
- RAG 출처와 저작권 설명 준비
- 시연 중 DeepSeek 장애 fallback 문구 지원

## 8. 매일 작업 순서

- 작업 시작 전 git pull 방식으로 최신 dev 동기화
- 개인 workspaces/.../workflows/{date}-{task}.md에 오늘 작업과 DoD 작성
- 계약 파일 이름과 경로를 먼저 확인하고 코드 생성
- 작업 후 본인 서비스 build/test와 금지 패턴 검색
- 개인 reports/{date}-{task}.md에 결과, 막힌 점, 다음 작업 작성
- PR에는 변경 범위, 검증 명령, 남은 리스크를 짧게 적는다

## 9. 검증 명령

```powershell
cd C:\workspace\QT-AI-2nd-Team-Project-master
.\gradlew.bat -p services\ai-service build --no-daemon
.\gradlew.bat -p services\ai-service test --no-daemon
rg -n "rag_sources|PromptTemplate|QtStage|JournalType" services\ai-service
```

## 10. 금지 패턴

- PostgreSQL, ZooKeeper, Tempo 설정 추가 금지
- application.yml이나 코드에 API key, DB password, private key 평문 작성 금지
- 트랜잭션 안에서 KafkaTemplate.send 직접 호출 금지. AFTER_COMMIT 패턴 사용
- 서비스 간 DB 직접 JOIN 또는 Repository 공유 금지
- JOURNAL_EVENTS 수정/삭제 금지. append-only 이벤트 로그로 유지
- AI SSE 경로에 /messages 사용 금지. /ai/sessions/{id}/turns만 사용
- OpenAPI 계약과 다른 DTO, 경로, 에러 포맷 임의 생성 금지

## 11. 산출물

- PromptTemplate/QtStage 모델 PR
- RAG seed와 source metadata 문서
- golden/injection 평가 세트
- 프롬프트 가드레일 체크리스트

## 12. PR 전에 확인

- 내 담당 경로 밖 변경이 섞이지 않았는가
- OpenAPI, event schema, DECISIONS.md와 충돌하지 않는가
- ProblemDetail, Kafka data envelope, DeepSeek, 4서비스 기준을 지켰는가
- 로컬 build/test 결과를 PR 본문에 적었는가
- 막힌 점은 추측으로 넘기지 않고 Lead에게 질문으로 남겼는가
