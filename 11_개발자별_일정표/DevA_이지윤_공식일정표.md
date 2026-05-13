# QT-AI 개인 공식 일정표 - 이지윤

> 이 파일 하나만 읽고도 본인 작업을 시작할 수 있도록 최신 결정, 작업 범위, 일정, 검증 명령을 모두 포함한다.
> 기준일: 2026-05-13 / 기준 결정: 2026-05-12 4서비스 재정렬

## 1. 내 역할

- 담당자: 이지윤
- 역할: Bible Service - 성경/QT/주석 Core
- 개인 작업 폴더: `workspaces/DevA_이지윤/`
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

## 3. 내가 주로 만지는 경로

- services/bible-service/src/main/java/com/qtai/bible/
- services/bible-service/src/main/resources/db/migration/
- apis/bible/openapi.yaml

## 4. 담당 범위

- BOOKS, KR_BIBLE, EN_BIBLE, COMMENTARIES, EXPLANATIONS 조회 도메인
- 오늘의 QT 본문과 쉬운 설명 제공을 위한 Bible read API
- Redis-Cache 적용 대상과 TTL 정리
- Bible Service 안에서 Journal 도메인과 충돌하지 않는 패키지 경계 유지
- 개역개정/ESV/NIV 등 저작권 위험 데이터 유입 차단

## 5. API와 이벤트 계약 요약

- GET /bible/books
- GET /bible/kr/{bookCode}/{ch}/{v}
- GET /bible/en/{bookCode}/{ch}/{v}
- GET /api/v1/explanations/{bookCode}/{ch}/{v}
- GET /api/v1/commentary/{bookCode}/{ch}/{v}
- 묵상일지 API는 같은 Bible Service지만 DevD와 패키지를 나누어 작업한다.

## 6. W1 상세 일정 - Foundation Lock-in

- 5/13: Book/Verse Entity, Repository, Flyway V1 BOOKS/KR_BIBLE/EN_BIBLE 초안
- 5/14: /bible/books, /bible/kr, /bible/en 조회 UseCase와 DTO
- 5/15: COMMENTARIES/EXPLANATIONS 스키마와 조회 API 골격
- 5/19: Redis cache key/TTL 표준과 cache miss 처리
- 5/20: ProblemDetail, X-User-Id 선택 처리, NotFound 에러 매핑
- 5/21: DevD Journal 테이블 migration과 충돌 여부 점검
- 5/22: Bible core API smoke test와 seed 데이터 검증

## 7. W2-W5 일정

### W2 - 핵심 도메인 구현
- 성경/주석/쉬운 설명 API 완성
- Redis 캐시 적용 및 테스트
- BFF 본문 화면 연동 대응

### W3 - Kafka/E2E 통합
- BFF 통합 테스트와 실제 모바일 조회 흐름 연결
- 데이터 누락/저작권 금지 데이터 스캔
- 성능 p95 개선

### W4 - 안정화와 시연 환경
- seed/migration 재현성 점검
- 문서와 API 예시 업데이트
- 시연 본문 데이터 고정

### W5 - 발표와 리허설
- 성경 조회와 주석 화면 시연 지원
- 장애 시 캐시/DB 점검 담당
- 발표 Q&A: 데이터 출처와 저작권 설명

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
.\gradlew.bat -p services\bible-service build --no-daemon
.\gradlew.bat -p services\bible-service test --no-daemon
rg -n "개역개정|ESV|NIV" services\bible-service
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

- Bible core Flyway migration
- 성경/주석 조회 UseCase와 Controller
- Redis cache 설정과 테스트
- 저작권 허용 데이터 seed 리포트

## 12. PR 전에 확인

- 내 담당 경로 밖 변경이 섞이지 않았는가
- OpenAPI, event schema, DECISIONS.md와 충돌하지 않는가
- ProblemDetail, Kafka data envelope, DeepSeek, 4서비스 기준을 지켰는가
- 로컬 build/test 결과를 PR 본문에 적었는가
- 막힌 점은 추측으로 넘기지 않고 Lead에게 질문으로 남겼는가
