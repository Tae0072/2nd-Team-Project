# QT-AI 개인 공식 일정표 - 김태혁

> 이 파일 하나만 읽고도 본인 작업을 시작할 수 있도록 최신 결정, 작업 범위, 일정, 검증 명령을 모두 포함한다.
> **기준일: 2026-05-14 / 기준 결정: 2026-05-14 오전 회의 (Modular Monolith 전환 + 시뮬레이터 단독)**
>
> **2026-05-14 v2.0 변경 요지:**
> - 백엔드는 단일 `qtai-server`. RAG/ChromaDB 폐기. 기존 AI/RAG Prompt 보조 범위는 강상민 단독 주도로 이관.
> - **본인 새 역할: 시뮬레이터 단독 담당** (스프라이트 기반 검토). 데이터 모델·저장소·생성 이미지 라이선스는 본인 일임.
> - 시뮬레이터 명세는 22_기능_명세서·DECISIONS §10 보류 항목 참조.

## 1. 내 역할

- 담당자: 김태혁
- GitHub: [@xogurrh012](https://github.com/xogurrh012)
- **새 역할 (2026-05-14): 시뮬레이터 단독 담당 (`com.qtai.simulator` 도메인)**
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
- qtai-server/src/main/java/com/qtai/simulator/
- qtai-server/src/main/resources/db/migration/simulator/
- 22_기능_명세서.md FS-12 (시뮬레이터 명세)

## 4. 담당 범위 (2026-05-14 v2.0 — 시뮬레이터 단독)

- `com.qtai.simulator` 도메인 패키지 단독 담당 (Modular Monolith, ADR-0001)
- 본문 좌표(book·chapter·verse) → 장면 시각화. 스프라이트 기반 검토 중 (Flame · pixi.js · Lottie · 자체 sprite sheet 후보 비교)
- `simulator_scenes` 테이블 스키마·저장소(권장 Docker volume `qtai-simulator-assets`)·생성 이미지 라이선스 정의 = **본인 일임**
- 생성 이미지 라이선스 3가지 확인: (1) 학습 데이터 출처 (2) 결과물 상업/재배포 권리 (3) 종교 인물(예수·하나님 등) 묘사 정책
- 5년 단위 본문 갱신 시 폐기/재생성 (회의록 §3-3)
- 회의록 §6 "가장 난이도 높음 — 일정 양보 허용". 시연 못 들어가면 정적 일러스트 폴백 5~10개 준비

## 5. API와 도메인 경계

- API: `GET /api/v1/simulator/scenes/{bookCode}/{chapter}/{verse}` (lazy 생성·캐시·재사용)
- 도메인 Facade: `com.qtai.simulator.api.SimulatorFacade` Interface — 다른 도메인은 이 Facade만 통해 호출 (ADR-0015)
- 입력: 본문 좌표만. **Bible 도메인 Repository 직접 import 금지** (ADR-0001)
- 출력: `SceneResponse {bookCode, chapter, verse, assetType, assetUrl, generatedAt}`

## 6. W1 상세 일정 - Foundation Lock-in v2 (2026-05-14)

- 5/13: `com.qtai.simulator` 패키지 골격 + Spring Modulith `@ApplicationModule` 선언 + 22_기능_명세서 FS-12 본문 1차
- 5/14: 후보 라이브러리 비교 (Flame / pixi.js / Lottie / 자체 sprite) + 본문 좌표 1개 prototype 시각화
- 5/15: `simulator_scenes` Flyway V1 작성 + Scene 도메인 Entity
- 5/19: **라이선스 3가지 확인 완료** → DECISIONS §10 보류 해소 + workspaces/DevB_김태혁/docs/simulator-license-report.md 박제
- 5/20: SimulatorFacade 구현 + AssetStorage(Docker volume) + lazy 생성
- 5/21: API endpoint + apis OpenAPI 추가 + BFF/Flutter 협업 합의
- 5/22: 시연 본문 좌표 1~2개 E2E 검증 + 단위 테스트 + Spring Modulith 통과

### W1 PR 머지 조건 (필수)

- [ ] 단위 테스트 작성 완료 및 `./gradlew :qtai-server:test` 로컬 통과
- [ ] Spring Modulith `QtaiModulesTest.verifyModuleBoundaries()` 통과 (다른 도메인 import 0건)
- [ ] ArchUnit 5 룰 통과 (Controller→Repository 등 금지 룰)

## 7. W2-W5 일정 (2026-05-14 v2.0)

### W2 - 시뮬레이터 명세 + 데이터 모델 + 라이선스 확정 (5/26~5/29)
- 22_기능_명세서 FS-12 본문 채우기 (입출력·저장 정책·완료 기준)
- `simulator_scenes` 테이블 + 생성 방식 결정 (AI 이미지 vs PD 일러스트 vs 자체 sprite)
- **라이선스 3가지 확인 완료** → simulator-license-report.md 박제
- UI 토글 "성경 인물 묘사" on/off 정책 결정

### W3 - 시뮬레이터 생성 파이프라인 1차 (6/1~6/5)
- 본문 좌표 → 장면 lazy 생성 + DB 캐시
- API endpoint + apis OpenAPI 추가
- Docker volume `qtai-simulator-assets` 캐시·재사용 검증

#### W3 PR 머지 조건 (필수)
- [ ] simulator 패키지 단위 테스트 + Spring Modulith 통과
- [ ] 다른 도메인 import 0건 (ADR-0001 절대 규칙)
- [ ] 시연 본문 좌표 1~2개 시각화 성공

### W4 - 시연 본문 시각화 + 정적 일러스트 폴백 (6/8~6/12)
- 2026-06-17 발표 본문 좌표 1~3개 시각화
- **정적 일러스트 폴백 5~10개 준비** (시뮬레이터 실패 시 즉시 대체)
- 강태오 ADR-0016 결과 확인 — 시뮬레이터는 v2 분리 대상 아님(Modular Monolith 잔류)

### W5 - 발표와 리허설 (6/15~6/17)
- 시뮬레이터 시연 또는 정적 일러스트 폴백 시연
- 발표 자료 "시뮬레이터" 절 (생성 방식·라이선스·5년 폐기 정책)
- Q&A: 생성 이미지 권리·종교 인물 묘사 정책 답변 준비

## 8. 매일 작업 순서

- 작업 시작 전 git pull 방식으로 최신 dev 동기화
- 개인 workspaces/DevB_김태혁/workflows/{date}-{task}.md에 오늘 작업과 DoD 작성
- 계약 파일 이름과 경로를 먼저 확인하고 코드 생성
- 작업 후 `./gradlew :qtai-server:test`와 금지 패턴 검색
- 개인 reports/{date}-{task}.md에 결과, 막힌 점, 다음 작업 작성
- PR에는 변경 범위, 검증 명령, 남은 리스크를 짧게 적는다

## 9. 검증 명령

```powershell
cd C:\workspace\QT-AI-2nd-Team-Project-master
.\gradlew.bat :qtai-server:test --no-daemon

# Spring Modulith 경계 검증 (ADR-0015)
.\gradlew.bat :qtai-server:test --tests "QtaiModulesTest" --no-daemon

# 금지 패턴 검색 (0건이어야 함 — ChromaDB·RAG·v1 Kafka 코드 금지)
rg -n "ChromaDB|rag_sources|chromadb" qtai-server\src\main\java\com\qtai\simulator
rg -n "import com\.qtai\.(bible|ai|journal|gatewayauth|bff)\." qtai-server\src\main\java\com\qtai\simulator
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
