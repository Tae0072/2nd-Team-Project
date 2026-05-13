# ADR-0012: Notification은 v1.0 stateless WebSocket으로 처리한다

## 상태
Accepted (2026-05-13 정합성 패치)

## 날짜
2026-05-13

## 작성자
강태오

## Reviewer
이지윤, 김태혁, 강상민, 이승욱, 김지민

## Context
AI 세션 완료 후 Bible Service가 오늘 Journal에 AI 요약을 첨부하면 사용자에게 알려야 한다. v1.0에서 별도 `NOTIFICATION_LOG` 테이블과 미수신 알림 조회 API까지 만들면 범위가 커진다. 시연에서는 사용자가 화면을 보고 있는 상황이므로 WebSocket 실시간 전달이면 충분하다.

## Decision
v1.0 알림은 BFF Aggregator의 stateless WebSocket(STOMP)으로 처리한다.

1. AI Service가 `ai.session.completed`를 발행한다.
2. Bible Service가 이벤트를 consume하여 오늘 QT Journal에 `aiSessionId`와 summary를 첨부한다.
3. Bible Service 또는 관련 producer가 `notification.requested`를 발행한다.
4. BFF Aggregator가 `notification.requested`를 consume한다.
5. 활성 세션이 있으면 `/user/{userId}/queue/notifications`로 push하고, 없으면 저장하지 않는다.

별도 알림 저장 테이블은 v1.0에 만들지 않는다. 사용자가 오프라인이면 알림은 누락될 수 있지만 Journal 자체는 DB에 남아 다음 오늘 QT/묵상 목록 조회에서 확인할 수 있다.

## Alternatives
- **v1.0부터 NOTIFICATION_LOG 테이블**: 미수신 알림 보장은 좋지만 API·DB·정합성 작업이 증가한다.
- **REST polling**: 구현은 쉽지만 실시간성이 낮고 서버 부하가 증가한다.
- **FCM/APNs push**: 모바일 인증서와 플랫폼 설정 부담이 크다.

## Consequences
**긍정:**
- 시연 플로우가 단순하다.
- 알림 저장소 없이 BFF가 WebSocket delivery에 집중한다.
- v1.1 미수신 알림 기능의 확장 지점이 분명하다.

**부정:**
- 오프라인 사용자는 실시간 알림을 놓칠 수 있다.
- BFF 다중 Pod에서는 Redis-WS 세션 레지스트리와 sticky/session routing 정책이 필요하다.

## 검증 방법
`notification.requested` consume 후 인증된 해당 사용자 세션에만 STOMP 메시지가 도달해야 한다. 다른 userId 세션에 메시지가 전달되면 안 된다.
