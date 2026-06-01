# 27. 성경 JSON 출처 및 라이센스 규정

> 작성자: 이지윤
> 기준 저장소: https://github.com/scrollmapper/bible_databases
> 목적: QT-AI에서 사용할 성경 본문 데이터의 출처, 라이센스, 사용 가능 범위를 실제 본문 적재 전에 정리한다.

## 1. 사용 방향 요약

QT-AI 프로젝트의 v1 성경 본문 데이터는 다음 번역본을 우선 검토한다.

| 언어 | 프로젝트 표기 | 원본/저장소 표기 | 사용 목적 | 검토 상태 |
| --- | --- | --- | --- | --- |
| 한국어 | KRV | KorRV / 개역성경 / 개역한글 계열 | 앱 한글 본문, 로컬 번들, 서버 마스터 후보 | Lead 검토 필요 |
| 영어 | KJV | KJV | 영어 본문, 서버 마스터, 온라인 조회 후보 | Lead 검토 필요 |

후보 저장소는 `scrollmapper/bible_databases`를 기준으로 검토한다.

- 원본 저장소: https://github.com/scrollmapper/bible_databases
- 저장소 특징: 여러 성경 번역본을 MySQL, SQLite, CSV, JSON, YAML, TXT, MD 형식으로 제공한다.
- GitHub README 기준으로 `KJV`, `KorRV` 항목이 존재한다.
- 저장소 전체 라이선스는 GitHub 화면 기준 MIT로 표시된다.
- 단, 각 번역본/원문 데이터의 실제 라이선스는 개별 파일 또는 SQL 상단 주석을 별도로 확인해야 한다.

> 주의: 저장소 전체 라이선스와 각 성경 본문 데이터의 원저작권 상태가 항상 동일하다고 단정하지 않는다. 특히 한국어 성경은 민감하므로 Public Domain 표기가 있더라도 원출처 확인 또는 Lead 검토가 필요하다.

## 2. 한국어 번역본 검토

| 번역본 명칭 | 특징 및 용도 | 저작권/사용 판단 |
| --- | --- | --- |
| 개역한글 / 개역성경 계열 | 고어체가 있으나 무료 성경 데이터 후보로 가장 현실적이다. 프로젝트에서는 KRV로 표기 예정이다. | 사용 후보. 단, 실제 파일의 Public Domain 표기와 원출처 확인 필요 |
| 개역개정 / NKRV | 현재 한국 교회에서 널리 사용하는 표준 번역 | 유료/권리 제한. 프로젝트 금지 번역본으로 사용하지 않음 |
| 새번역 / RNKSV | 현대 한국어 번역, 가독성 좋음 | 유료. 사용하지 않음 |
| 공동번역 / KCB | 개신교/가톨릭 공동 번역 | 유료. 사용하지 않음 |
| 우리말성경 | 두란노서원 현대어 번역 | 유료. 두란노 본문 텍스트 저장 금지 기준에 따라 사용하지 않음 |
| 쉬운성경 | 어린이/청소년 대상 쉬운 번역 | 유료. 사용하지 않음 |
| 가톨릭 성경 | 한국 가톨릭 공식 성경 | 유료. 사용하지 않음 |

## 3. 영어 번역본 검토

| 번역본 | 출판연도 | 번역 방식 | 가독성 | 상업적 무료 사용 판단 | 프로젝트 판단 |
| --- | --- | --- | --- | --- | --- |
| KJV | 1611 / 1769 계열 | 직역 | 고어체 | 가능성이 높음 | v1 영어 본문 후보 |
| NIV | 1978 | 의역 | 쉬움 | 제한/유료 | 사용하지 않음 |
| ESV | 2001 | 직역 중심 | 좋음 | 제한/유료 | v1 사용 안 함. 향후 유료/파트너십 검토 가능 |
| WEB | 2000 | 직역 | 좋음 | 무료 사용 가능성이 높음 | 대체 후보 가능. 단, 브랜드 신뢰도 검토 필요 |

### ESV 참고

ESV는 English Standard Version의 약자로, 2001년에 Crossway에서 출판한 현대 영어 성경이다. KJV보다 읽기 쉽고 NIV보다 원어에 더 가까운 직역 성향이 강하다는 장점이 있으나, 상업 앱에서 사용하려면 출판사 라이선스 확인이 필요하다.

따라서 v1에서는 무료/공개 사용 가능성이 높은 KJV를 우선 사용하고, 이후 유료 기능 또는 파트너십 모델에서 ESV 같은 현대 영어 번역본을 검토하는 방향이 적절하다.

## 4. 라이선스 판단 기준

### Public Domain 후보

Public Domain으로 명시된 데이터는 법적으로 저작권 제약이 없을 가능성이 높다. 다만 앱 배포와 서비스 신뢰를 위해 다음을 기록한다.

| 항목 | 기록 기준 |
| --- | --- |
| 원본 출처 | `https://github.com/scrollmapper/bible_databases` |
| 번역본 코드 | 예: `KorRV`, `KJV` |
| 프로젝트 표시명 | 예: `KRV`, `KJV` |
| 라이선스 | `Public Domain` 또는 파일 상단 표기 그대로 |
| 출처 표기 | 앱 설정/정보 화면에 표시 |
| 원출처 확인 | 한국어 성경의 경우 Lead 검토 필요 |

권장 표기 예시:

```text
KRV Bible Data
Source: https://github.com/scrollmapper/bible_databases
Source translation key: KorRV
License: Public Domain 표시 확인 필요
Used by QT-AI Project for Bible text display.
```

```text
KJV Bible Data
Source: https://github.com/scrollmapper/bible_databases
Source translation key: KJV
License: Public Domain 표시 확인 필요
Used by QT-AI Project for English Bible text display.
```

### GPL 후보

GPL 데이터도 상업 서비스에서 사용할 수는 있지만, 사용자가 GPL 데이터에 대해 복사/수정/재배포 권리를 실제로 행사할 수 있어야 한다. 앱 약관이나 배포 방식이 이를 막으면 문제가 될 수 있다.

GPL 데이터를 사용하려면 최소한 다음을 충족해야 한다.

| 항목 | 필요 조치 |
| --- | --- |
| 원본 출처 | 원본 GitHub URL 명시 |
| 라이선스 | GPL 버전과 전문 링크 제공 |
| 수정 여부 | SQL -> JSON 변환, 공백 정규화, 앱 DB 포맷 변환 등 기록 |
| 수정본 제공 | 앱에 들어간 최종 데이터 또는 변환본 공개 URL 제공 |
| 사용자 권리 | 복사/수정/재배포 권리를 앱 약관에서 제한하지 않음 |
| 검토 필요성 | 앱 전체 GPL 영향 여부 Lead/법무 검토 필요 |

GPL 표기 예시:

```text
King James Version (KJV) Bible Data
Original Source: https://github.com/scrollmapper/bible_databases
License: GNU General Public License (GPL)
Modified by QT-AI Project: Converted to app database format and normalized data structure.
Modified Source/Data: https://github.com/{team}/qt-ai-bible-data
GPL License: https://www.gnu.org/licenses/gpl-3.0.html
```

## 5. 출처 표시 적용 대상과 담당자

아래 내용은 팀 포트폴리오 README와 개인 일정표 기준으로 출처 표시가 필요할 수 있는 성경 본문 관련 작업을 간략히 정리한 것이다. 각 담당자는 실제 구현 시점에 사용자 화면, API 응답, 관리자 화면, 문서 중 어디에 출처 표시가 필요한지와 표시 방법을 확인한 뒤 작업한다.

| 출처 표시 필요 작업 | 담당자 | 확인할 내용 |
| --- | --- | --- |
| 성경 JSON / KRV, KJV 출처 표시 | 이지윤 | 성경 본문 데이터의 원본 저장소, 번역본 코드, 라이선스, 앱/문서 표기 문구 |
| Today QT 본문 범위 출처 / 성서유니온 기준 | 이지윤 중심, Lead 확인 | 본문 텍스트는 저장하지 않고 날짜별 책/장/절 범위 정보만 사용하는지, 범위 기준 출처를 어떻게 표시할지 |
| AI 해설 출처 메타데이터 | 강상민 | 승인된 해설과 용어 풀이가 사용자에게 노출될 때 출처 또는 근거 정보가 함께 표시되는지 |

이 문서는 성경 본문과 성경 본문을 근거로 한 해설/범위 정보의 출처 표시 기준을 다룬다. 찬양 데이터, 일반 나눔 데이터, 사용자 작성 노트는 이 문서의 성경 JSON 출처 검토 범위에 포함하지 않는다.

## 6. 프로젝트 적용 원칙

1. v1에서는 한국어 KRV, 영어 KJV만 우선 검토한다.
2. 개역개정, NIV, ESV는 seed/test/fixture/response 데이터에 넣지 않는다.
3. 성서유니온/두란노 본문 텍스트는 저장하지 않는다.
4. 실제 성경 본문 텍스트는 출처 후보가 승인된 뒤에만 적재한다.
5. `data/bible-sources/README.md`에는 원본 JSON이나 본문 텍스트를 넣지 않고, 출처/라이선스/재배포 가능 여부만 기록한다.
6. Public Domain 표기가 있더라도 한국어 성경은 Lead 검토 후 `APPROVED`로 변경한다.
7. 라이선스가 불명확하면 `NEEDS_LEAD_REVIEW`로 남기고 실제 본문 적재를 막는다.
