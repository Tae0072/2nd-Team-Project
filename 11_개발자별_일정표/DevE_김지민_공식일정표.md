# 📋 QT-AI — Flutter (김지민) 상세 일정표

문서 버전: v1.0
작성일: 2026-05-08
담당자: 김지민
역할: Flutter App Owner
담당 영역: Flutter 모바일 앱 — Sliver 기반 Sync Scroll · RiverPod · DIO · SSE 스트리밍 UI
개발 기간: W1(5/15 이후) ~ W5(6/17)
연관 문서: 00_개발_일정_총괄표 / 04_API_명세서 v1.5 / 08_프론트엔드_Flutter_가이드 v1.0

---

## 0. 역할 핵심 선언

> **"사용자가 처음 보는 것이 Flutter 화면이다."**
> 시연에서 심사위원이 직접 손으로 만지는 유일한 인터페이스.
> Sliver 기반 Sync Scroll과 AI SSE 스트리밍 실시간 타이핑 효과가
> 포트폴리오의 'WOW 포인트'가 된다.
> 백엔드 API가 완성되기 전에도 Mock 데이터로 화면을 미리 완성한다.

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
flutter-app/
  ├── pubspec.yaml
  ├── lib/
  │   ├── main.dart
  │   ├── core/
  │   │   ├── network/
  │   │   │   ├── dio_client.dart         (DIO 기본 설정 + JWT interceptor)
  │   │   │   └── sse_client.dart         (dio_sse SSE 수신)
  │   │   ├── router/
  │   │   │   └── app_router.dart         (go_router 라우팅)
  │   │   └── theme/
  │   │       └── app_theme.dart
  │   ├── features/
  │   │   ├── auth/                       (로그인·회원가입)
  │   │   ├── bible/                      (성경 구절 조회 — Sliver Sync Scroll)
  │   │   ├── ai_chat/                    (AI 대화 — SSE 스트리밍 UI)
  │   │   ├── journal/                    (묵상 노트 CRUD)
  │   │   └── home/                       (대시보드)
  │   └── shared/
  │       ├── providers/                  (RiverPod providers)
  │       └── widgets/                    (공통 위젯)
  └── test/
      └── widget/                         (Widget 테스트)
```

---

## 2. Flutter App 핵심 기술 요구사항

| 요구사항 | 구현 방식 | 완료 목표 | 왜 중요한가 |
|---------|-----------|-----------|-------------|
| DIO + JWT Interceptor | `dio_interceptors` — 401 시 자동 토큰 갱신 | W1 후반 | 모든 API 호출 기반 |
| Sliver Sync Scroll | `CustomScrollView` + `SliverList` — 한/영 병기 동기화 스크롤 | W2 수 | 포트폴리오 WOW 포인트 |
| SSE 스트리밍 UI | `dio_sse` → `StreamBuilder` → 타이핑 애니메이션 | W2 목 | 시연 핵심 장면 |
| RiverPod 상태 관리 | `StateNotifierProvider` — 세션·메시지 상태 | W1 후반 | 상태 관리 일관성 |
| STOMP WebSocket 알림 | `stomp_dart_client` → 알림 배지 | W3 수 | 실시간 알림 |
| Google OAuth | `google_sign_in` → Auth Service 연동 | W2 화 | 소셜 로그인 |

---

## 3. 주요 패키지 (pubspec.yaml)

```yaml
dependencies:
  flutter_riverpod: ^2.5.1
  dio: ^5.4.3
  dio_sse: ^0.2.0            # SSE 스트리밍
  go_router: ^13.2.0
  stomp_dart_client: ^1.0.0  # STOMP WebSocket
  google_sign_in: ^6.2.1
  cached_network_image: ^3.3.1
  intl: ^0.19.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  mocktail: ^1.0.3
```

---

## 4. 일별 상세 일정

### 🟩 W1 — Flutter 환경 세팅 + 기반 구축 (5/15~5/22)

> ⚠️ W1 초반(5/12~14)은 백엔드 API가 아직 없으므로 Mock 데이터로 선행

| 일자 | 오전 | 오후 코어 | 저녁 |
|------|------|-----------|------|
| 5/12 화 | 킥오프 참석 | Flutter SDK + FVM 3.24.5 환경 확인. `flutter create flutter-app` | pubspec.yaml 의존성 추가 + `flutter pub get` |
| 5/13 화 | Stand-up | `go_router` 라우팅 설정 (5개 화면). `app_theme.dart` 기본 테마 | Mock 데이터로 홈 화면 기본 레이아웃 |
| 5/14 수 | Stand-up | `DioClient` 설정 (baseUrl, timeout, JWT interceptor 골격) | RiverPod Provider 기본 구조 설계 |
| 5/15 목 | Stand-up | 로그인·회원가입 화면 UI (Auth API 연동 전 Mock) | `auth` feature 디렉토리 구조 완성 |
| 5/16 금 | Stand-up | Auth API 연동 — `POST /auth/login` DIO 호출 + JWT 저장 | 로그인 성공 → 홈 이동 플로우 |
| 5/19 월 | Stand-up | DIO JWT Interceptor 완성 (401 → 자동 토큰 갱신) | RiverPod auth 상태 관리 완성 |
| 5/20 화 | Stand-up | 성경 조회 화면 골격 — Mock 데이터로 한/영 병기 리스트 | `bible` feature UI 기본 |
| 5/21 수 | Stand-up | AI 채팅 화면 골격 — Mock 메시지 리스트 + 입력창 | SSE 수신 구조 설계 |
| 5/22 목 | Stand-up | **W1 Lock-in 게이트 참석 (18:00)** | `flutter analyze` 오류 0건 확인 |

**W1 완료 기준**
- [ ] `flutter analyze` 오류 0건
- [ ] `flutter test` 기본 통과
- [ ] 로그인 → JWT 저장 → 보호 API 호출 플로우
- [ ] `go_router` 5개 화면 라우팅

---

### 🟨 W2 (5/26~5/29) — 핵심 화면 완성

| 일자 | 주요 작업 |
|------|-----------|
| 5/26 화 | 페이스 점검 (11:30). Bible API 연동 — `GET /api/v1/passages/JHN/3` 실데이터 표시 |
| 5/27 수 | **Sliver Sync Scroll** — `CustomScrollView` + `SliverList` 한/영 병기 동기화 구현 |
| 5/28 목 | **AI SSE 스트리밍 UI** — `dio_sse` + `StreamBuilder` 타이핑 애니메이션 |
| 5/29 금 | Journal CRUD 화면 + API 연동. 전체 화면 Flow 연결 확인 |

---

### 🟧 W3 (6/1~6/5) + 🟥 W4 (6/8~6/12) + ⬛ W5 (6/15~6/17)

| 주차 | 주요 작업 |
|------|-----------|
| W3 | STOMP WebSocket 알림 배지 구현. 큐티 A→B→C→D 단계 진행 UI. Google OAuth 연동 |
| W4 | 전체 화면 UI polish. 시연 시나리오 dry-run 반복. Widget 테스트 보강 |
| W5 | 시연 데모 기기 세팅. 리허설 화면 흐름 주도. 발표 PPT 화면 설명 파트 담당 |

---

## 5. Sliver Sync Scroll 핵심 구현 패턴

```dart
// 한/영 성경 병기 동기화 스크롤
class BibleSyncScrollView extends StatefulWidget {
  @override
  State<BibleSyncScrollView> createState() => _BibleSyncScrollViewState();
}

class _BibleSyncScrollViewState extends State<BibleSyncScrollView> {
  final ScrollController _koController = ScrollController();
  final ScrollController _enController = ScrollController();
  bool _isSyncing = false;

  void _syncScroll(ScrollController master, ScrollController slave) {
    if (_isSyncing) return;
    _isSyncing = true;
    slave.jumpTo(master.offset);
    _isSyncing = false;
  }

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(child: _buildScrollView(_koController, isKorean: true)),
        Expanded(child: _buildScrollView(_enController, isKorean: false)),
      ],
    );
  }
}
```

---

## 6. SSE 스트리밍 UI 핵심 구현 패턴

```dart
// AI 응답 SSE 스트리밍 — 타이핑 애니메이션
class AiChatWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stream = ref.watch(aiStreamProvider);
    return StreamBuilder<String>(
      stream: stream,
      builder: (context, snapshot) {
        final text = snapshot.data ?? '';
        return AnimatedSwitcher(
          duration: const Duration(milliseconds: 50),
          child: Text(text, key: ValueKey(text.length)),
        );
      },
    );
  }
}
```

---

## 7. AI 에이전트 활용 가이드

| 단계 | Claude 활용처 | 주의사항 |
|------|--------------|----------|
| W1 | DIO interceptor 패턴, RiverPod provider 구조 | flutter 3.24.5 + null safety 환경 확인 |
| W2 | Sliver 스크롤 패턴, StreamBuilder SSE 처리 | 노션 기술 블로그 Flutter Sliver 챕터 먼저 확인 |
| W3 | STOMP 연결 코드, Widget 테스트 작성 | 패키지 버전 pubspec.yaml과 일치 확인 |
| 전체 | 화면 레이아웃 코드 초안 생성 | 실제 API 응답 형식(camelCase) 확인 후 모델 생성 |
