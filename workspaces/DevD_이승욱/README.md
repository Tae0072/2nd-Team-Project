# DevD_이승욱 개인 작업 공간

이 폴더는 **DevD_이승욱 (Bible팀 — Journal 도메인 주도 · Flutter 빌드 책임자(시연 6/17) · 인증 · 관리자 페이지)** 의 개인 작업 공간입니다.

> **2026-05-14 v2.0 재배치:** Bible팀 3인 중 Journal 도메인 주도 + Flutter 빌드 책임자. Bible 프로토타입 → Flutter → 인증 → 관리자 페이지 일괄 진행. v1 Kafka는 보류, 도메인 간 통신은 Spring `ApplicationEventPublisher` + `@TransactionalEventListener(AFTER_COMMIT)` in-process 이벤트로 처리(ADR-0004·0007 v2 Kafka 전환 시 publisher만 교체).

## 🚫 다른 개발자(팀원)/에이전트 접근 금지

- 이 폴더(`workspaces/DevD_이승욱/`)는 **DevD_이승욱 본인만** 작성·수정·삭제할 수 있습니다.
- 다른 팀원(에이전트)은 이 폴더를 **읽지도, 수정하지도, 삭제하지도** 마십시오.
- 본인이 다른 팀원의 폴더(`workspaces/[다른 사람]/`)를 건드리는 것도 **동일하게 금지**입니다.
- 이 규칙은 `../../AGENTS.md` 에 명시되어 있습니다.

## 📁 폴더 구조

```
DevD_이승욱/
├── README.md         (이 파일)
├── workflows/        (작업 시작 전 워크플로우 문서)
│   └── _template.md  (양식 — 새 워크플로우 작성 시 복사)
├── reports/          (작업 완료 후 리포트)
│   └── _template.md  (양식 — 새 리포트 작성 시 복사)
├── docs/             (개인이 작성하는 문서·명세)
└── notes/            (개인 메모·로그·스크린샷)
```

## 📋 작업 프로세스

\\\
[워크플로우 작성] → [자기 검토] → [작업 진행] → [리포트 작성]
       ↓                ↓               ↓             ↓
  workflows/      체크리스트 확인    코드/문서      reports/
\\\

1. **시작 전 — `workflows/YYYYMMDD-[작업명].md`** 작성
   - 양식: `workflows/_template.md` 복사 후 작성
   - 작업 목표·대상 파일·단계·검증 기준·리스크 명시

2. **자기 검토** — 워크플로우의 체크리스트 모두 ✓

3. **작업 진행** — 워크플로우대로 코딩 / 문서 작성

4. **종료 후 — `reports/YYYYMMDD-[작업명].md`** 작성
   - 양식: `reports/_template.md` 복사 후 작성
   - 결과·검증·산출물·회고 정리

## 🔗 연관 문서 (모두 읽기 전용 — 수정 금지)

- 실행 가이드: `../../11_개발자별_일정표/DevD_이승욱_실행가이드.html`
- 단일 진실 원천: `../../DECISIONS.md`
- 에이전트 규칙: `../../AGENTS.md`
- API 명세서: `../../04_API_명세서.md`
- ERD: `../../02_ERD_문서.md`