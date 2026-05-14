# 📋 QT-AI — Dev B (김태혁) 상세 일정표

문서 버전: v1.0
작성일: 2026-05-08
담당자: 김태혁
역할: Bible Service Owner
담당 서비스: Bible Service — 성경 본문(KR/EN) · 주석 · Redis 24h 캐시 · 전문 검색
개발 기간: W1(5/12) ~ W5(6/17)
연관 문서: 00_개발_일정_총괄표 / 02_ERD_문서 v1.3 / 04_API_명세서 v1.5

---

## 0. 역할 핵심 선언

> **"이 프로젝트의 데이터 심장은 성경 본문이다."**
> Bible Service는 AI 코칭의 RAG 소스이자 Flutter 화면의 핵심 콘텐츠다.
> 다중 JOIN(한/영 병기) + Redis 캐시로 P95 ≤ 300ms를 달성해야
> AI SSE 스트리밍 전체 타임라인(P95 ≤ 2000ms)이 지켜진다.

### 공통 PR 완료 조건

> 모든 코드 PR은 테스트 코드 작성 후 단위 테스트와 통합 테스트가 모두 통과해야 완료로 인정한다.

- [ ] 변경 범위 테스트 코드 작성 완료 (문서-only PR은 사유 명시)
- [ ] 단위 테스트 통과
- [ ] 통합 테스트 통과
- [ ] PR 본문에 테스트 명령과 통과 결과 첨부
- [ ] 미충족 시 Draft 유지, 머지 금지

---

## 1. 소유권 선언

```
bible-service/
  └── src/main/kotlin/com/qtai/bibleservice/
      ├── domain/
      │   ├── entity/Book.java
      │   ├── entity/KrBible.java        (개역한글)
      │   ├── entity/EnBible.java        (KJV)
      │   ├── entity/Commentary.java
      │   └── repository/
      ├── usecase/
      │   ├── GetChapterUseCase.java     ← 전담 소유
      │   ├── GetVerseUseCase.java
      │   ├── GetCommentaryUseCase.java
      │   └── SearchPassageUseCase.java
      ├── infrastructure/
      │   └── cache/BibleCacheRepository.java  (Redis 24h TTL)
      └── api/
          └── BibleController.java
  └── src/main/resources/
      └── db/migration/
          ├── V1__create_bible_tables.sql
          └── V2__seed_books.sql          (66권 기본 데이터)
```

**BFF에 제공하는 공개 인터페이스**
- `GET /bible/kr/{book}/{chapter}/{verse}` — BFF의 `/me/dashboard` 오늘의 구절에서 호출
- `GET /bible/kr/{book}/{chapter}/1 (장 첫절)` — AI Service RAG 컨텍스트 조회에서 호출
- 캐시 키 형식: `cache:passage:{book}:{chapter}:{verse}` (TTL 24h)

---

## 2. Bible Service 핵심 기술 요구사항

| 요구사항 | 구현 방식 | 완료 목표 | 왜 중요한가 |
|---------|-----------|-----------|-------------|
| 한/영 병기 조회 | KR_BIBLE + EN_BIBLE 병렬 쿼리 → DTO 병합 | W1 목 | AI 코칭 소스 데이터 |
| Redis 24h 캐시 | `@Cacheable("passage")` + TTL 24h | W2 화 | P95 ≤ 300ms 달성 |
| 전문 검색 | JPQL LIKE 또는 Full-Text Index | W2 수 | 구절 검색 기능 |
| 주석 조회 | Commentary 테이블 JOIN | W2 목 | AI RAG 연계 |
| 시드 데이터 | Flyway V2 — 66권 메타 + 샘플 구절 (JHN 3장) | W1 화 | W1 테스트부터 실데이터 필요 |

---

## 3. 일별 상세 일정

### 🟩 W1 (5/12~5/22)

| 일자 | 오전 | 오후 코어 | 저녁 |
|------|------|-----------|------|
| 5/12 화 | 킥오프 참석. git pull | Flyway V1 — BOOKS·KR_BIBLE·EN_BIBLE·COMMENTARIES 테이블 | Book 엔티티 + BOOKS 66권 V2 시드 |
| 5/13 화 | Stand-up | KrBible·EnBible 엔티티 + 연관관계 (book-chapter-verse 복합 조회) | @DataJpaTest — 기본 조회 1개 |
| 5/14 수 | Stand-up | `GetChapterUseCase` — 한/영 병기 병렬 쿼리 구현 | Repository 쿼리 메서드 3개 이상 |
| 5/15 목 | Stand-up | `GetVerseUseCase` + `BibleController` 기본 엔드포인트 | X-User-Id 헤더 수신 확인 (Gateway 연동) |
| 5/16 금 | Stand-up | 단위 테스트 — UseCase Mockito | `/bible/kr/JHN/3/16` curl 성공 확인 |
| 5/19 월 | Stand-up | `BibleCacheRepository` Redis 24h TTL 설정 | 캐시 히트 로그 확인 |
| 5/20 화 | Stand-up | `GetCommentaryUseCase` + Commentary 샘플 시드 | W1 체크리스트 점검 |
| 5/21 수 | Stand-up | 통합 테스트 (@SpringBootTest + Testcontainers MySQL) | PR 정리 |
| 5/22 목 | Stand-up | **W1 Lock-in 게이트 참석 (18:00)** | W1 회고 |

**W1 완료 기준**
- [ ] `/bible/kr/JHN/3/16` → 한/영 병기 구절 반환
- [ ] `/bible/books` → 66권 목록 반환 (Flyway V2 시드)
- [ ] Flyway V1+V2 마이그레이션 성공
- [ ] Repository @DataJpaTest 통과

---

### 🟨 W2 (5/26~5/29)

| 일자 | 주요 작업 |
|------|-----------|
| 5/26 화 | 페이스 점검 (11:30). Redis 캐시 실제 TTL 동작 검증 (redis-cli TTL 확인) |
| 5/27 수 | `SearchPassageUseCase` — 키워드 전문 검색 구현 |
| 5/28 목 | Commentary 조회 완성. AI Service RAG 연동 테스트 (강상민 협력) |
| 5/29 금 | 서비스 커버리지 60%+. `/bible/commentaries/JHN/3/16` curl 확인 |

---

### 🟧 W3 (6/1~6/5) + 🟥 W4 (6/8~6/12)

| 주차 | 주요 작업 |
|------|-----------|
| W3 | BFF `/me/dashboard` 오늘의 구절 실데이터 연동. Redis 캐시 부하 테스트 (k6) |
| W4 | 회귀 테스트. 시연 JHN 3:16 데이터 완전성 확인. 커버리지 70%+ |

---

## 4. AI 에이전트 활용 가이드

| 단계 | Claude 활용처 | 주의사항 |
|------|--------------|----------|
| W1 | Flyway SQL DDL 초안, 병렬 쿼리 JPQL 작성 | 컬럼명·인덱스 02번 ERD와 대조 필수 |
| W2 | Redis 캐시 설정 코드, Full-Text 쿼리 | MySQL FULLTEXT 인덱스 적용 여부 직접 확인 |
| W3 | 테스트 케이스 생성 | 실패 케이스(존재하지 않는 book/chapter) 반드시 포함 |
