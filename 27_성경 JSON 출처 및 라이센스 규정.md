# 27. 성경 JSON 출처 및 라이선스 규정

> 작성자: 이지윤
> 기준 저장소: https://github.com/scrollmapper/bible_databases
> 적용 저장소: https://github.com/Tae0072/2nd-Team-Project
> 목적: QT-AI에서 사용하는 성경 JSON 원본의 출처, 라이선스, 표시 방식, 담당자별 확인 범위를 고정해 저작권 리스크를 낮춘다.

## 1. 성경 번역본 후보

QT-AI는 한글 본문과 영어 본문을 함께 제공한다. 단, 모든 번역본을 자유롭게 사용할 수 있는 것은 아니므로 무료/유료 여부와 재배포 조건을 먼저 구분한다.

### 1.1 한글 성경

| 번역본 | 성격 | 사용 비용/제약 | 프로젝트 판단 |
| --- | --- | --- | --- |
| 개역성경 / KorRV 계열 | 고어체가 있으나 무료 후보로 현실적 | 원본 데이터의 `Public Domain` 표기 확인 필요 | v1 한글 본문으로 선택 |
| 개역개정 / NKRV | 현재 한국 교회에서 널리 쓰는 번역 | 권리 제한 또는 유료 사용 검토 필요 | 사용하지 않음 |
| 새번역 / RNKSV | 현대 한국어 번역 | 권리 제한 또는 유료 사용 검토 필요 | 사용하지 않음 |
| 공동번역 / KCB | 공동 번역본 | 권리 제한 또는 유료 사용 검토 필요 | 사용하지 않음 |
| 우리말성경 | 현대어 번역 | 두란노 본문 텍스트 저장 금지 기준에 따라 사용하지 않음 | 사용하지 않음 |
| 쉬운성경 | 쉬운 문체 번역 | 권리 제한 또는 유료 사용 검토 필요 | 사용하지 않음 |
| 가톨릭 성경 | 한국 가톨릭 공식 성경 | 권리 제한 또는 유료 사용 검토 필요 | 사용하지 않음 |

### 1.2 영어 성경

| 번역본 | 성격 | 사용 비용/제약 | 프로젝트 판단 |
| --- | --- | --- | --- |
| KJV | 1611 / 1769 계열 고전 영어 번역 | 무료 사용 가능성이 높으나, 현재 기준 파일은 `GPL` 표기 확인 필요 | v1 영어 본문으로 선택하되 GPL 표시 조건 관리 |
| WEB | 공개 사용을 목표로 한 현대 영어 번역 | 무료 사용 가능성이 높음 | KJV 대체 후보 |
| ESV | 현대 영어 직역 성향 번역 | 출판사 라이선스 확인 필요 | 사용하지 않음 |
| NIV | 현대 영어 의역 성향 번역 | 출판사 라이선스 확인 필요 | 사용하지 않음 |

## 2. 프로젝트 선택

QT-AI v1은 다음 두 번역본만 사용한다.

| 언어 | 프로젝트 표시명 | 원본/저장소 표기 | 사용 목적 | 선택 이유 |
| --- | --- | --- | --- | --- |
| 한글 | KRV | KorRV / 개역성경 | 앱 한글 본문, 로컬 번들, 서버 마스터 | 무료 후보이며 F-01 한글 본문 요구사항을 만족한다. |
| 영어 | KJV | KJV | 영어 본문, 서버 마스터, 온라인 조회 | 영어 비교 본문 후보로 사용할 수 있으나 GPL 표시 조건을 관리해야 한다. |

다음 번역본은 seed, fixture, API 응답 예시, 테스트 데이터, 관리자 등록 데이터에 넣지 않는다.

- 개역개정 / NKRV
- 새번역 / RNKSV
- 공동번역 / KCB
- 우리말성경
- 쉬운성경
- 가톨릭 성경
- ESV
- NIV

성서유니온 또는 두란노 본문 텍스트도 저장하지 않는다. QT 본문 큐레이션에는 날짜별 책, 장, 절 범위 정보만 저장한다.

## 3. Git 데이터 기준

프로젝트 Git에는 아래 성경 JSON 원본을 둔다.

| 프로젝트 파일 | 언어 | 원본 기준 | 용도 |
| --- | --- | --- | --- |
| `성경/KorRV.json` | 한글 | `scrollmapper/bible_databases`의 KorRV JSON | 한글 본문 원본 |
| `성경/KJV.json` | 영어 | `scrollmapper/bible_databases`의 KJV JSON | 영어 본문 원본 |

원본 저장소와 라이선스 확인 위치는 아래와 같다.

| 번역본 | 실제 JSON 데이터 | 라이선스 확인 위치 | SQL 상단 라이선스 표기 |
| --- | --- | --- | --- |
| KorRV | `formats/json/KorRV.json` | `formats/sql/KorRV.sql` | `Public Domain` |
| KJV | `formats/json/KJV.json` | `formats/sql/KJV.sql` | `GPL` |

주의할 점은 저장소 전체 라이선스와 개별 성경 데이터의 라이선스를 구분해야 한다는 것이다. GitHub 저장소 전체가 MIT로 보이더라도, 실제 번역본 데이터는 SQL 상단의 `License` 표기를 우선 확인한다.

## 4. 출처 표시 방식

성경 본문은 앱 화면, 관리자 화면, README, 발표 자료, API 문서 중 본문 출처가 필요한 위치에 출처를 남긴다. 사용자가 직접 성경 본문을 보는 화면에는 최소한 설정/정보 화면 또는 라이선스 화면에서 확인 가능한 출처 링크를 제공한다.

### 4.1 Public Domain 표시

Public Domain 표기가 있더라도 출처를 생략하지 않는다. 앱 신뢰도와 검토 추적성을 위해 아래 항목을 남긴다.

| 항목 | 표시 기준 |
| --- | --- |
| 번역본 | KRV / KorRV |
| 출처 | `https://github.com/scrollmapper/bible_databases` |
| 원본 파일 | `formats/json/KorRV.json` |
| 라이선스 확인 위치 | `formats/sql/KorRV.sql` |
| 라이선스 표기 | `Public Domain` |
| 사용 범위 | QT-AI 한글 성경 본문 표시 |

권장 문구:

```text
KRV Bible Data
Source: https://github.com/scrollmapper/bible_databases
Source translation key: KorRV
License notice checked from formats/sql/KorRV.sql: Public Domain
Used by QT-AI for Korean Bible text display.
```

### 4.2 GPL 표시

GPL은 단순 출처 표기만으로 끝나지 않을 수 있다. GPL 데이터가 앱, 서버, 번들, DB, 변환 파일, 다운로드 파일에 포함되면 사용자가 해당 데이터의 원본 또는 수정본에 접근할 수 있어야 하고, 복사/수정/재배포 권리를 앱 약관이나 배포 방식으로 막으면 안 된다.

현재 KJV 기준 파일은 `formats/sql/KJV.sql` 상단에 `License: GPL`로 표시되어 있다. GPL 버전이 원본 파일에 명확히 적혀 있지 않으면 임의로 GPL-2.0 또는 GPL-3.0이라고 단정하지 않는다. 최종 표기 전 Lead가 원본 저장소의 라이선스 파일, SQL 메타데이터, README를 함께 확인한다.

권장 문구:

```text
KJV Bible Data
Original Source: https://github.com/scrollmapper/bible_databases
Source translation key: KJV
License notice checked from formats/sql/KJV.sql: GPL
Modified by QT-AI: Converted or loaded into the project data format when applicable.
Modified Source/Data: https://github.com/Tae0072/2nd-Team-Project
```

## 5. GPL 최소 가이드

KJV처럼 GPL로 표시된 데이터는 아래 조건을 최소 기준으로 관리한다.

| 항목 | 최소 기준 |
| --- | --- |
| 원본 출처 | 원본 GitHub 저장소 URL과 파일 경로를 표시한다. |
| 라이선스 | `GPL` 표기를 유지한다. GPL 버전이 불명확하면 버전을 단정하지 않는다. |
| 수정 여부 | JSON 정규화, DB 적재, SQLite 변환, 공백 수정, 절 좌표 병합 여부를 기록한다. |
| 수정본 제공 | 앱이나 서버에 포함된 최종 데이터 또는 변환본에 접근 가능한 위치를 제공한다. |
| 사용자 권리 | 성경 데이터의 복사, 수정, 재배포 권리를 약관이나 화면 문구로 제한하지 않는다. |
| 앱 배포 | Flutter 앱 번들에 GPL 데이터가 포함되는 경우, 앱 배포 방식과 GPL 의무 충돌 여부를 Lead가 확인한다. |
| 서버 배포 | 서버 DB에 GPL 데이터가 들어가는 경우, API 응답과 데이터 제공 범위가 라이선스 의무를 침해하지 않는지 확인한다. |
| 문서/발표 | README, 발표 자료, 포트폴리오에 KJV 출처와 GPL 표기를 누락하지 않는다. |

GPL 관련 작업에서 확신이 없으면 `APPROVED`로 처리하지 말고 Lead 검토 대상으로 남긴다.

## 6. 출처 표시 담당 파트

아래 파트는 GPL 또는 성경 출처 표기를 특히 유심히 봐야 한다.

| 파트 | 담당자 | 확인할 내용 |
| --- | --- | --- |
| 성경 JSON 원본 / 출처 문서 | 이지윤 | `성경/KorRV.json`, `성경/KJV.json`의 원본 저장소, 파일 경로, 라이선스 표기, 문서 최신화 |
| Lead / API / 릴리즈 검토 | 강태오 | GPL 데이터가 앱/서버/문서/배포 방식에 미치는 영향, 최종 PR 승인, README 출처 표기 |
| Flutter 앱 / 설정·정보 화면 | 김지민 | 앱 사용자가 성경 출처와 라이선스를 확인할 수 있는 화면 또는 링크 제공 |
| 관리자 웹 | 김지민 | 관리자 화면에서 본문 또는 해설을 노출할 때 출처 표기 누락 방지 |
| 성경·QT API | 이지윤·김태혁 | API 응답, 번들 다운로드, Today QT 조회에서 번역본 코드와 출처 메타데이터 누락 방지 |
| AI 해설·Q&A | 강상민 | AI 해설, 용어 풀이, Q&A 응답에 성경 본문 또는 근거 본문이 포함될 때 출처 메타데이터 유지 |
| 시뮬레이터 | 김태혁 | 장면 스크립트, 자막, 클립 설명에 성경 본문이 포함될 때 출처 표기 기준 확인 |
| note/sharing/praise | 이승욱·김지민 | 공유 글, 노트 인용, 찬양 큐레이션 화면에서 성경 본문·찬양 데이터 출처가 섞이지 않도록 확인 |

## 7. 프로젝트 적용 원칙

1. v1 성경 본문은 `성경/KorRV.json`과 `성경/KJV.json`만 기준 데이터로 둔다.
2. KRV/KorRV는 Public Domain 표기를 확인하되 출처 표시를 유지한다.
3. KJV는 GPL 표기를 유지하고, 앱/서버/문서/배포 단계에서 GPL 최소 가이드를 따른다.
4. 저장소 전체 MIT 표기만 보고 개별 성경 데이터 라이선스를 MIT로 단정하지 않는다.
5. 성경 JSON을 DB, SQLite, fixture, seed, API 예시로 가공하면 가공 방식과 출처 표시 위치를 PR 본문에 적는다.
6. 유료 또는 권리 제한 번역본은 프로젝트 데이터에 넣지 않는다.
7. 라이선스가 불명확하면 구현을 멈추고 Lead 검토를 받는다.

## 8. 필독 대상

이 문서는 성경 본문, QT 본문, 해설, AI 응답, 시뮬레이터, 노트 인용, 관리자 화면, 발표 자료를 다루는 모든 프로젝트 담당자가 읽어야 한다.

AI 에이전트도 성경 데이터나 관련 문서를 수정하기 전에 이 문서를 먼저 읽어야 한다. 특히 KJV 또는 GPL 표기가 등장하는 작업에서는 출처, 수정 여부, 사용자 제공 방식, 담당자 검토 여부를 확인한 뒤 변경한다.
