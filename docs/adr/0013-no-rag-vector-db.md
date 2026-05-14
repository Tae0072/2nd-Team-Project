# ADR-0013: RAG / 벡터 DB / 엘라스틱서치 도입 제외

## 상태
Accepted (2026-05-14 강사 지도)

## 날짜
2026-05-14

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
2026-05-13까지 AI 도메인은 ChromaDB 기반 RAG로 본문·해설·QT 방법론 collection을 인덱싱하고, AI 응답에 `rag_sources`를 강제 인용하도록 설계되어 있었다(09_AI 가이드 §6). 2026-05-14 회의에서 강사는 "RAG/벡터 DB는 비정형 데이터(PDF 수십~수백 개, 한글파일, 이미지 등)를 RDB로 정형화하기 어려울 때 필요하다. QT-AI는 성경 본문이 장·절 단위로 매우 정형화되어 있어 정확한 셀렉트가 가능하므로 RDB만으로 충분하다"고 지도했다.

## Decision
v1·v2 모두 **RAG / 벡터 DB / 엘라스틱서치를 도입하지 않는다.**

| 항목 | 결정 |
| --- | --- |
| ChromaDB | ❌ 사용 안 함 |
| 다른 벡터 DB (Pinecone, Weaviate, Qdrant 등) | ❌ 사용 안 함 |
| 엘라스틱서치 / OpenSearch | ❌ 사용 안 함 |
| RAG 파이프라인 (embedding · vector search) | ❌ 사용 안 함 |
| 검색 방식 | **MySQL B-tree 인덱스** (정확한 좌표 셀렉트) + 필요 시 FULLTEXT 인덱스 |
| AI 출처 참조 | **사전 적재 해설 row 참조**. `ai_turns.sources` JSON 컬럼은 사용된 `bible_explanations.id` 배열 |
| SSE 이벤트 필드 | `rag_sources` → **`sources`** 로 리네이밍 |

### AI 출처 컨텍스트 주입 흐름

1. AI 세션 시작 시 본문 좌표(`bookCode`, `chapter`, `verse`)로 `bible_explanations` row를 미리 조회.
2. 조회 결과(쉬운 요약·배경 설명·어려운 단어·출처)를 LLM system prompt에 텍스트로 주입.
3. LLM 응답 후 `ai_turns.sources`에 사용한 `bible_explanations.id` 배열 기록.

## Alternatives
- **ChromaDB 유지 (이전 결정)**: 정형 데이터에 과한 인프라. 강사 판단으로 폐기.
- **MySQL FULLTEXT만 사용**: 의미적 유사도 부족하지만 v1 범위에서는 충분.
- **엘라스틱서치 도입**: 운영 부담 증가, 학생 프로젝트 범위 초과.

## Consequences
**긍정:**
- ChromaDB Pod·sentence-transformers·인덱싱 스크립트 운영 부담 제거.
- AI 응답 출처가 DB row 단위로 명확 (디버깅·관리자 모니터링 용이).
- AI 도메인 코드가 단순화 (RAG client 제거).

**부정:**
- AI가 사전 적재되지 않은 본문에 대해 출처를 인용할 수 없음 → `bible_explanations` 사전 적재 범위가 곧 AI 답변 범위. 적재 일정 = AI 답변 범위 일정.
- 의미적 검색(예: "사랑에 관한 구절") 지원 불가 → 필요해지면 v2에서 FULLTEXT 또는 외부 검색 도입 재논의.
- 09_AI 가이드 §6 RAG 컨텍스트 표준 절 전면 폐기, 02_ERD §4 AI ERD의 `rag_sources` 컬럼 의미 재정의, 17_데이터시드 §4 RAG 시드 절 폐기 필요.

## 검증 방법
W1 Lock-in 5/22까지:
1. ai-service 빌드에 ChromaDB·sentence-transformers·embedding 라이브러리 의존성 0건.
2. `ai_turns.sources` JSON 값이 `bible_explanations.id` 배열로 채워짐.
3. 09_AI 가이드 §6 폐기·치환 완료.
