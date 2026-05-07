# ADR-0012: Notification은 v1.0 stateless WebSocket (별도 테이블 X)

## 상태
Accepted (W0 5/15 — Foundation Lock-in 사전 박제)

## 날짜
2026-05-15

## 작성자
강태오

## Reviewer
강상민, 김태혁, 이지윤, 이승욱, 김지민 (W1 Foundation Lock-in 회의에서 합의 — 03번 § 14.2)

## Context
사용자 알림(예: AI 완료 → Journal 자동 생성됨)은 v1.0 시연에 어떻게 구현하는가? 별도 NOTIFICATION_LOG 테이블 + REST 조회 endpoint를 만들면 운영 부담 ↑. 그러나 알림은 사용자에게 보여줘야 함. WebSocket으로 실시간 전달이 가장 단순.

## Decision
**v1.0: BFF Aggregator의 stateless WebSocket (STOMP)** (03번 § 1.1):

흐름:
1. AI Service가 \i.session.completed\ 발행
2. Journal Service가 자동으로 새 Journal 생성 + \
otification.requested\ 발행
3. BFF Aggregator가 \
otification.requested\ consume
4. 해당 user_id에 STOMP \/user/{userId}/queue/notifications\로 푸시

별도 NOTIFICATION_LOG 테이블 없음. 사용자 오프라인이면 알림 누락 (단, Journal은 DB에 있으니 사용자가 다음 로그인 시 대시보드에서 확인).

v1.1: NOTIFICATION_LOG 테이블 + 미수신 알림 sync (모바일 앱 시작 시 30일 이내 미수신 조회).

## Alternatives
- **v1.0부터 NOTIFICATION_LOG 테이블**: 6주 시연 + 6명 인력 부담 ↑
- **REST polling**: WebSocket 인프라 학습 곡선 회피 가능 but 실시간성 ↓ + 서버 부하 ↑
- **외부 push 알림 (FCM)**: Flutter + iOS/Android 인증 등 학습 곡선

## Consequences
**긍정:**
- 시연 단순 (사용자가 화면 보고 있음 가정)
- 운영 부담 X
- v1.1 도입 시점 명확 (mobile 사용자 비율 ↑)

**부정:**
- 사용자 오프라인 시 알림 누락 (단, 핵심 데이터는 DB에 보존)
- BFF Aggregator 다중 Pod 시 user_id sticky 필요 (03번 § 1.1 + 05번 § 3.7)

## 검증 방법
07번 § 4.6 통합 테스트: \
otification.requested\ consume 후 STOMP 메시지가 해당 user_id 세션에만 도달 (다른 user_id 세션에 누출 X)