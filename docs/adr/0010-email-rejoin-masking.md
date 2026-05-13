# ADR-0010: 탈퇴자 이메일 마스킹 정책은 v1.1로 연기한다

## 상태
Deferred (v1.1)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
USERS.email은 UNIQUE 제약이다. 계정 탈퇴를 구현하면 탈퇴 사용자가 같은 이메일로 재가입할 수 있도록 이메일 마스킹 또는 archive 정책이 필요하다. 그러나 2026-05-12 결정으로 계정 탈퇴 기능과 `user.deactivated` 이벤트는 MVP 범위에서 제외되었다.

## Decision
v1.0에서는 계정 탈퇴 API와 이메일 마스킹을 구현하지 않는다. 정책 초안은 v1.1 후보로 보존한다.

v1.1에서 계정 탈퇴를 구현할 경우 기본 후보는 다음과 같다.

```sql
UPDATE users
SET deleted_at = NOW(6),
    email = CONCAT('u_', id, '_deactivated_', UNIX_TIMESTAMP(), '@deleted.local')
WHERE id = ?;
```

마스킹된 이메일은 UNIQUE 제약 충돌을 피하고 원본 이메일 노출을 줄인다. 원본 이메일 보관이 필요하면 보관 기간과 접근 권한을 별도 보안 ADR로 결정한다.

## Alternatives
- **v1.0에 탈퇴까지 구현**: MVP 범위 대비 인증·보안·보상 이벤트 작업이 과도하다.
- **탈퇴 시 hard delete**: Journal 보존과 감사 요구에 맞지 않는다.
- **탈퇴자 재가입 금지**: 사용자 경험이 나쁘고 추후 정책 변경이 어렵다.

## Consequences
**긍정:**
- v1.0 인증 범위가 회원가입·로그인·로그아웃·refresh·Google OAuth로 단순해진다.
- `user.deactivated` Kafka topic과 보상 흐름을 만들지 않아도 된다.

**부정:**
- v1.0에서는 사용자가 계정을 탈퇴할 수 없다.
- ERD와 보안 문서에 남은 탈퇴 관련 표현은 "v1.1 후보"로 분명히 표기해야 한다.

## 검증 방법
OpenAPI에 `/auth/me/deactivate`가 없어야 하며, Kafka schema와 `DECISIONS.md`에 `user.deactivated`를 v1.0 구현 토픽으로 두지 않는다.
