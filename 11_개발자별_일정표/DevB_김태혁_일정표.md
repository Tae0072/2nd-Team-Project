# QT-AI -- DevB (김태혁) Bible Service 상세 일정표 v2.0

> 이 문서 목적: Bible Service를 처음부터 끝까지 만드는 단계별 가이드.
> "어디서 뭘 왜 어떻게"를 명령어와 코드 수준으로 설명한다.

문서 버전: v2.0 | 작성일: 2026-05-08 | 담당자: 김태혁
연관 문서: 02_ERD_문서 v1.2 / 04_API_명세서 v1.2

---

## 0. Bible Service가 하는 일

Bible Service는 성경 본문과 주석을 제공하는 서비스다.

```
클라이언트가 구절 요청 --> Redis 캐시 확인 --> 없으면 DB 조회 --> 응답
AI Service가 RAG 컨텍스트 요청 --> 주석 포함 반환
```

**만들어야 하는 API**
```
GET /bible/books                               성경 66권 목록
GET /bible/passages/{book}/{chapter}           장 전체 구절 (한/영 병기)
GET /bible/passages/{book}/{chapter}/{verse}   단일 구절
GET /bible/commentaries/{book}/{chapter}/{verse}  주석
GET /bible/search?q=키워드                     성경 전문 검색
```

**Bible Service가 W1에 최소 기능이 있어야 하는 이유**

강상민 (AI Service) 이 W2에 RAG 테스트를 하려면 성경 본문 데이터가 있어야 한다.
빈 DB 로는 API 테스트 자체가 불가능하다.
따라서 W1 중에 요한복음 3장의 한/영 데이터가 최소한 DB에 들어가야 한다.

---

## 1. 환경 세팅 (5/12 아침)

```bash
cd C:\workspace\2nd-Team-Project
git pull origin main

.\gradlew.bat :bible-service:build -x test --no-daemon
# "BUILD SUCCESSFUL" 이 나와야 한다
```

---

## 2. Day1 -- 5/12(화): Flyway SQL + 시드 데이터

### Flyway가 필요한 이유

Flyway 없이 개발하면 팀원마다 DB 구조가 달라진다.
`V1__create_bible_tables.sql` 파일에 CREATE TABLE 을 적어두면
서비스 시작 시 자동으로 실행되어 항상 동일한 DB 구조를 보장한다.

**파일 위치**: `bible-service/src/main/resources/db/migration/`

### V1__create_bible_tables.sql

```sql
-- 성경 66권 메타 정보 테이블
CREATE TABLE IF NOT EXISTS books (
    book_id        INT AUTO_INCREMENT PRIMARY KEY,
    book_code      VARCHAR(10)  NOT NULL UNIQUE,  -- GEN, EXO, JHN 등 약어
    book_name_ko   VARCHAR(50)  NOT NULL,
    book_name_en   VARCHAR(50)  NOT NULL,
    testament      ENUM('OLD','NEW') NOT NULL,
    total_chapters INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 한국어 성경 (개역개정)
CREATE TABLE IF NOT EXISTS kr_bible (
    id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    book     VARCHAR(10) NOT NULL,
    chapter  INT NOT NULL,
    verse    INT NOT NULL,
    content  TEXT NOT NULL,
    UNIQUE KEY uq_passage (book, chapter, verse)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 영어 성경 (KJV)
CREATE TABLE IF NOT EXISTS en_bible (
    id       BIGINT AUTO_INCREMENT PRIMARY KEY,
    book     VARCHAR(10) NOT NULL,
    chapter  INT NOT NULL,
    verse    INT NOT NULL,
    content  TEXT NOT NULL,
    UNIQUE KEY uq_passage_en (book, chapter, verse)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 주석 테이블
CREATE TABLE IF NOT EXISTS commentaries (
    commentary_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    book         VARCHAR(10) NOT NULL,
    chapter      INT NOT NULL,
    verse        INT NOT NULL,
    source       VARCHAR(100) NOT NULL,
    content      TEXT NOT NULL,
    lang         ENUM('ko','en') NOT NULL DEFAULT 'ko'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE INDEX idx_kr_passage ON kr_bible(book, chapter);
CREATE INDEX idx_en_passage ON en_bible(book, chapter);
CREATE INDEX idx_commentary ON commentaries(book, chapter, verse);
```

### V2__seed_books.sql

```sql
INSERT INTO books (book_code, book_name_ko, book_name_en, testament, total_chapters) VALUES
('GEN','창세기','Genesis','OLD',50),
('PSA','시편','Psalms','OLD',150),
('ISA','이사야','Isaiah','OLD',66),
('MAT','마태복음','Matthew','NEW',28),
('JHN','요한복음','John','NEW',21),
('ROM','로마서','Romans','NEW',16),
('REV','요한계시록','Revelation','NEW',22);
```

### V3__seed_john3_ko.sql (테스트용 -- 시연에서 주로 3:16 사용)

```sql
INSERT INTO kr_bible (book, chapter, verse, content) VALUES
('JHN',3,1,'그 때에 바리새인 중에 니고데모라 하는 사람이 있으니 유대인의 지도자라'),
('JHN',3,2,'그가 밤에 예수께 와서 이르되 랍비여 우리가 당신은 하나님께로부터 오신 선생인 줄 아나이다'),
('JHN',3,3,'예수께서 대답하여 이르시되 진실로 진실로 네게 이르노니 사람이 거듭나지 아니하면 하나님의 나라를 볼 수 없느니라'),
('JHN',3,16,'하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니 이는 그를 믿는 자마다 멸망하지 않고 영생을 얻게 하려 하심이라'),
('JHN',3,17,'하나님이 그 아들을 세상에 보내신 것은 세상을 심판하려 하심이 아니요 그로 말미암아 세상이 구원을 받게 하려 하심이라');
```

### V4__seed_john3_en.sql

```sql
INSERT INTO en_bible (book, chapter, verse, content) VALUES
('JHN',3,1,'There was a man of the Pharisees, named Nicodemus, a ruler of the Jews:'),
('JHN',3,2,'The same came to Jesus by night, and said unto him, Rabbi, we know that thou art a teacher come from God'),
('JHN',3,3,'Jesus answered and said unto him, Verily, verily, I say unto thee, Except a man be born again, he cannot see the kingdom of God.'),
('JHN',3,16,'For God so loved the world, that he gave his only begotten Son, that whosoever believeth in him should not perish, but have everlasting life.'),
('JHN',3,17,'For God sent not his Son into the world to condemn the world; but that the world through him might be saved.');
```

### V5__seed_commentary.sql

```sql
INSERT INTO commentaries (book, chapter, verse, source, content, lang) VALUES
('JHN',3,16,'매튜 헨리 주석',
 '이 구절은 복음의 핵심이다. 하나님의 사랑은 세상을 향한 것으로, 단순한 감정이 아닌 독생자를 주심으로 표현되었다.',
 'ko'),
('JHN',3,16,'Matthew Henry Commentary',
 'This verse contains the gospel in miniature. The love of God is the cause; the gift of His Son is the expression; believing is the condition; eternal life is the result.',
 'en');
```

---

## 3. Day2~3 -- 5/13~5/14: Entity + Repository

### KrBible.kt (한국어 성경 Entity)

**왜 한국어/영어 Entity를 따로 만드는가?**
한국어 성경(개역개정)과 영어 성경(KJV)은 별도 테이블에 저장한다.
한/영 병기 조회 시 두 테이블을 병렬 쿼리로 가져와서 합친다.

```kotlin
// bible-service/.../domain/entity/KrBible.kt
package com.qtai.bibleservice.domain.entity

import jakarta.persistence.*

@Entity
@Table(name = "kr_bible")
class KrBible(
    @Column(nullable = false, length = 10)
    val book: String,          // "JHN"

    @Column(nullable = false)
    val chapter: Int,          // 3

    @Column(nullable = false)
    val verse: Int,            // 16

    @Column(nullable = false, columnDefinition = "TEXT")
    val content: String,       // "하나님이 세상을..."

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    val id: Long = 0
)
```

### KrBibleRepository.kt

```kotlin
// bible-service/.../domain/repository/KrBibleRepository.kt
package com.qtai.bibleservice.domain.repository

import com.qtai.bibleservice.domain.entity.KrBible
import org.springframework.data.jpa.repository.JpaRepository

interface KrBibleRepository : JpaRepository<KrBible, Long> {

    // 특정 장의 모든 구절을 절 번호 순서로 조회
    fun findByBookAndChapterOrderByVerse(book: String, chapter: Int): List<KrBible>

    // 단일 구절 조회
    fun findByBookAndChapterAndVerse(book: String, chapter: Int, verse: Int): KrBible?

    // 키워드 검색 (LIKE 쿼리)
    fun findByContentContaining(keyword: String): List<KrBible>
}
```

EnBibleRepository 도 동일한 패턴으로 작성한다 (클래스명만 En으로 바꿈).

---

## 4. Day3~5 -- 5/14~5/16: UseCase + Redis 캐시

### Redis 캐시를 쓰는 이유

성경 구절은 데이터가 바뀌지 않는다.
매 요청마다 DB를 조회하는 것은 비효율적이다.
Redis에 24시간 캐시하면:
- DB 부하 크게 감소
- 응답 속도: Redis 캐시 히트 1~2ms vs DB 조회 10~50ms

### GetChapterUseCase.kt

```kotlin
// bible-service/.../usecase/GetChapterUseCase.kt
package com.qtai.bibleservice.usecase

import com.qtai.bibleservice.domain.repository.KrBibleRepository
import com.qtai.bibleservice.domain.repository.EnBibleRepository
import org.springframework.cache.annotation.Cacheable
import org.springframework.stereotype.Service

@Service
class GetChapterUseCase(
    private val krBibleRepository: KrBibleRepository,
    private val enBibleRepository: EnBibleRepository
) {
    // @Cacheable: 처음 호출 시 DB 조회 후 Redis에 저장
    //             이후 동일한 key로 호출하면 Redis에서 바로 반환 (DB 조회 안 함)
    @Cacheable(value = ["chapterCache"], key = "#book + ':' + #chapter")
    fun getChapter(book: String, chapter: Int): ChapterResponse {

        val krVerses = krBibleRepository.findByBookAndChapterOrderByVerse(book, chapter)
        val enVerses = enBibleRepository.findByBookAndChapterOrderByVerse(book, chapter)

        if (krVerses.isEmpty()) {
            throw IllegalArgumentException("${book} ${chapter}장을 찾을 수 없습니다.")
        }

        // 절 번호를 기준으로 한국어/영어 합치기
        val merged = krVerses.map { kr ->
            val en = enVerses.find { it.verse == kr.verse }
            VerseResponse(
                book    = kr.book,
                chapter = kr.chapter,
                verse   = kr.verse,
                textKo  = kr.content,
                textEn  = en?.content      // 영어가 없으면 null
            )
        }

        return ChapterResponse(book = book, chapter = chapter, verses = merged)
    }
}

data class VerseResponse(
    val book: String, val chapter: Int, val verse: Int,
    val textKo: String?, val textEn: String?
)

data class ChapterResponse(
    val book: String, val chapter: Int, val verses: List<VerseResponse>
)
```

**application.yml 에 캐시 설정 추가**:
```yaml
spring:
  cache:
    type: redis
    redis:
      time-to-live: 86400000   # 24시간 (밀리초: 24 * 60 * 60 * 1000)
```

**Application 클래스에 @EnableCaching 추가**:
```kotlin
@SpringBootApplication
@EnableCaching    // 이게 없으면 @Cacheable 이 동작하지 않는다!
class BibleServiceApplication
```

---

## 5. Day5~9 -- 5/16~5/22: Controller + 테스트

### BibleController.kt

```kotlin
// bible-service/.../api/BibleController.kt
package com.qtai.bibleservice.api

import com.qtai.bibleservice.usecase.GetChapterUseCase
import org.springframework.web.bind.annotation.*

@RestController
@RequestMapping("/bible")
class BibleController(private val getChapterUseCase: GetChapterUseCase) {

    @GetMapping("/passages/{book}/{chapter}")
    fun getChapter(
        @PathVariable book: String,
        @PathVariable chapter: Int
    ) = getChapterUseCase.getChapter(book, chapter)

    @GetMapping("/books")
    fun listBooks() = mapOf("message" to "구현 예정")
}
```

### curl 테스트

```bash
.\gradlew.bat :bible-service:bootRun

# 요한복음 3장 조회
curl http://localhost:8082/bible/passages/JHN/3
# 기대: {"book":"JHN","chapter":3,"verses":[{"verse":1,"textKo":"...","textEn":"..."},...]}
```

### @DataJpaTest 단위 테스트

```kotlin
// bible-service/src/test/kotlin/.../repository/KrBibleRepositoryTest.kt
@DataJpaTest    // JPA 관련 컴포넌트만 로드 (전체 앱보다 훨씬 빠름)
class KrBibleRepositoryTest {

    @Autowired
    lateinit var krBibleRepository: KrBibleRepository

    @Test
    fun `요한복음 3장 구절 조회`() {
        val verses = krBibleRepository.findByBookAndChapterOrderByVerse("JHN", 3)
        assertTrue(verses.isNotEmpty(), "JHN 3장에 구절이 있어야 함")
    }

    @Test
    fun `요한복음 3장 16절 단일 조회`() {
        val verse = krBibleRepository.findByBookAndChapterAndVerse("JHN", 3, 16)
        assertNotNull(verse, "요한복음 3:16 이 존재해야 함")
        assertTrue(verse!!.content.contains("하나님"))
    }

    @Test
    fun `존재하지 않는 책 조회 시 빈 목록`() {
        val verses = krBibleRepository.findByBookAndChapterOrderByVerse("UNKNOWN", 1)
        assertTrue(verses.isEmpty())
    }
}
```

```bash
.\gradlew.bat :bible-service:test --no-daemon
```

---

## 6. Redis 캐시 실제 동작 확인

```bash
# K8s Redis에 포트 포워딩 후 redis-cli 접속
kubectl port-forward svc/qtai-redis-master 6379:6379 -n qtai &
redis-cli -h localhost

# 캐시 키 확인
127.0.0.1:6379> keys *
# "chapterCache::JHN:3" 같은 키가 보이면 캐시 저장 성공

# TTL 확인 (86400 근처면 24시간 맞음)
127.0.0.1:6379> TTL "chapterCache::JHN:3"
```

---

## 7. 자주 발생하는 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `@Cacheable` 이 동작 안 함 | @EnableCaching 없음 | Application 클래스에 `@EnableCaching` 추가 |
| Redis 연결 실패 | Redis URL 잘못됨 | `spring.data.redis.url` 확인 |
| Flyway 시드 실패 | SQL 파일명 오류 또는 SQL 문법 오류 | MySQL 콘솔에서 SQL 직접 실행해보기 |
| Entity 저장 후 null 반환 | @Transactional 없음 | UseCase 메서드에 `@Transactional` 추가 |
| `EmptyResultDataAccessException` | 데이터가 없는 책/장 조회 | 시드 데이터 먼저 확인, Optional 처리 |

---

## 8. W2~W4 주간 요약

| 주차 | 김태혁 핵심 작업 |
|------|----------------|
| W2 (5/26~5/29) | Redis 캐시 TTL 실제 검증, SearchPassageUseCase 구현, AI RAG 연동 테스트 |
| W3 (6/1~6/5) | BFF 대시보드 오늘의 구절 실데이터 연동, k6 부하 테스트 |
| W4 (6/8~6/12) | 시연 JHN 3:16 데이터 완전성 확인, 커버리지 70%+ |
