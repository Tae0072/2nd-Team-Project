# 📖 QT-AI (큐티 AI 앱) — Frontend Flutter 가이드 v1.0

> **문서 버전:** v1.0
> **작성일:** 2026-05-07
> **연관 문서:** [01_프로젝트_계획서 v1.3](./01_프로젝트_계획서.md) / [02_ERD_문서 v1.2](./02_ERD_문서.md) / [03_아키텍처_정의서 v1.2](./03_아키텍처_정의서.md) / [04_API_명세서 v1.2](./04_API_명세서.md) / [05_보안_명세서 v1.0](./05_보안_명세서.md) / [06_DevOps_운영_매뉴얼 v1.0](./06_DevOps_운영_매뉴얼.md) / [07_테스트_전략 v1.0](./07_테스트_전략.md)
> **owner:** 김지민 (Frontend Flutter Owner)
> **Frontend 키워드:** Flutter 3.x · Dart 3.x · Riverpod 2.x · go_router · Dio + Retrofit · freezed · flutter_secure_storage · stomp_dart_client · dio_sse 또는 직접 SSE · Material 3 · go_router_builder · GetIt(선택) · flutter_localizations
> **W1 Lock-in 산출물:** 본 문서 + lutter-app/ 프로젝트 골격 + Riverpod 표준 Provider 1개 + Dio Interceptor (JWT·Refresh·ProblemDetail) + 5 화면 라우팅 골격 + secure_storage 키 표준 + lutter test 통과
> **목적:** 1차(HMS)의 핵심 실패 패턴 — **Mustache SSR + jQuery 혼재로 화면 상태 추적 불가, 토큰 보관·갱신 표준 없음, 백엔드 변경 시 클라이언트 깨짐** — 을 본질적으로 차단. 6명이 4 service 백엔드를 작업하는 동안 김지민 1명이 Flutter 모바일을 단독으로 풀스코프 구현. 표준 패턴 위에서 비슷 실력으로도 5 화면 + SSE + STOMP + JWT + 입체 묵상까지 완성 가능하도록 박제.

---

## 📌 변경 이력

| 버전 | 날짜 | 작성자 | 주요 변경 |
| --- | --- | --- | --- |
| v1.0 | 2026-05-07 | 강태오 (Lead) + 김지민 (Frontend Owner) | 초기 작성 — 16 sections — 1차 SSR/jQuery 패턴 분석 + Flutter 풀스코프 전환 + Riverpod·go_router·Dio·SSE·STOMP 표준 + 5 화면 가이드 + 테스트·빌드·접근성 + W1 체크리스트 |

---

## 목차

1. [개요·범위·1차 패턴 분석](#1-개요범위1차-패턴-분석)
2. [기술 스택 결정](#2-기술-스택-결정)
3. [프로젝트 구조 (Clean Architecture)](#3-프로젝트-구조-clean-architecture)
4. [상태 관리 — Riverpod 2.x](#4-상태-관리--riverpod-2x)
5. [라우팅 — go_router](#5-라우팅--go_router)
6. [네트워크 레이어 — Dio + Retrofit + Interceptor](#6-네트워크-레이어--dio--retrofit--interceptor)
7. [인증 — JWT·Refresh Rotation·secure_storage](#7-인증--jwtrefresh-rotationsecure_storage)
8. [SSE 클라이언트 — AI 큐티 4단계 스트리밍](#8-sse-클라이언트--ai-큐티-4단계-스트리밍)
9. [STOMP WebSocket 클라이언트 — 알림](#9-stomp-websocket-클라이언트--알림)
10. [화면 구현 가이드 — 5 핵심 화면](#10-화면-구현-가이드--5-핵심-화면)
11. [UI 디자인 시스템·테마·국제화](#11-ui-디자인-시스템테마국제화)
12. [에러 처리 — ProblemDetail·재시도·offline](#12-에러-처리--problemdetail재시도offline)
13. [Flutter 테스트 (Widget·Integration·Golden)](#13-flutter-테스트-widgetintegrationgolden)
14. [빌드·배포·CI/CD](#14-빌드배포cicd)
15. [성능·접근성·관측성](#15-성능접근성관측성)
16. [1차(HMS) SSR 패턴 ↔ Flutter 가드레일 + W1 Lock-in 체크리스트](#16-1차hms-ssr-패턴--flutter-가드레일--w1-lock-in-체크리스트)

---
## 1. 개요·범위·1차 패턴 분석

### 1.1 본 문서가 다루는 범위

본 문서는 QT-AI 모바일 앱(Flutter)의 클라이언트 구현 표준을 박제한다. 6명 팀에서 김지민이 단독으로 5 화면 + 실시간 통신 (SSE·STOMP) + 인증·토큰 관리를 구현하는 데 필요한 모든 패턴을 한 곳에 모았다.

본 문서가 **다루는 것:**
- Flutter SDK·Dart 버전·핵심 패키지 결정 (재배포 호환성 + 한국 시장 점유율 기준)
- 프로젝트 폴더 구조 (Clean Architecture 변형 — feature 단위)
- Riverpod 2.x로 표준 Provider 패턴 (AsyncNotifier·StreamProvider·Consumer 어디에 무엇을 두는지)
- go_router 선언적 라우팅 + 인증 가드 + deeplink 표준
- Dio + Retrofit + freezed 조합 + JWT·Refresh·ProblemDetail Interceptor
- secure_storage 키 명명 표준 + 토큰 lifecycle (저장→사용→갱신→폐기)
- AI 큐티 SSE 클라이언트 (event token / turn_completed / error / end 4 종류 처리)
- STOMP WebSocket 클라이언트 (CONNECT 시 JWT 헤더 + user/{userId}/queue 구독)
- 5 핵심 화면 (Dashboard·입체 묵상·AI 큐티·묵상 노트 목록·노트 작성/편집)
- 디자인 시스템 (Material 3 + 팀 색상·타이포·간격 토큰)
- 에러 처리 (RFC 9457 ProblemDetail → 사용자 메시지·재시도 결정)
- 테스트 (Widget·Integration·Golden)
- iOS·Android 빌드 분기 + CI/CD 통합 (06번 § 3.3)
- 접근성 (Semantics·VoiceOver·TalkBack)·관측성 (Sentry·Firebase Performance)

본 문서가 **다루지 않는 것 (다른 문서 참조):**
- 백엔드 API 계약 → 04번
- 인증 토큰 발급·검증 정책 → 05번 § 3
- AI 응답 SSE 프로토콜 → 04번 § 6.3
- STOMP CONNECT 인증 검증 (BFF 측) → 04번 § 10.2
- AI 프롬프트 운영 → 09번 (이지윤 강상민 페어 — 별도 작성 예정)

**v1.0 시연 범위 매트릭스 (Android 우선):**

| 항목 | v1.0 (6/17 발표) | v1.1 (Q3 검토) |
| --- | --- | --- |
| 대상 OS | **Android 우선** (Android 7.0 / API 24+) | iOS 14+ 추가 |
| 화면 | 5개 핵심 (대시보드·AI 대화·입체 묵상·노트 작성·알림) | + 설정·통계·history |
| 인증 | JWT + Google OAuth | + Apple Sign-In (iOS 출시 시) |
| 오프라인 | ❌ (네트워크 필수) | 부분 캐시 (Bible 본문) |
| 다크 모드 | ❌ (라이트 only) | 라이트/다크 토글 |
| 다국어 | ❌ (한국어 only) | 영어 ARB 추가 |
| 푸시 알림 | ❌ (앱 켜진 동안만 STOMP) | FCM (Firebase Cloud Messaging) |

**근거 — Android 우선:** 6주 시연 일정에 iOS 인증·App Store Review·Apple Developer Program(USD 99/yr) 부담 ↑. 대학생 데모 환경은 Android emulator 100% 관외. iOS는 v1.1에 검토 (§ 14.4).

### 1.2 1차(HMS) 프론트엔드 패턴 분석 — 무엇을 차단하는가

| 1차 사고 패턴 | 본질적 원인 | 2차 가드레일 |
| --- | --- | --- |
| Mustache 서버 사이드 렌더링 + jQuery — 화면 상태가 DOM에 흩어져 있어 어디에서 버그가 났는지 추적 불가 | 상태가 DOM에 분산 + 단방향 데이터 흐름 X | Riverpod 2.x로 모든 화면 상태를 Provider로 통합. DevTools에서 어떤 Provider가 어떤 값을 들고 있는지 즉시 확인 (§ 4) |
| 인증 토큰을 cookie + localStorage에 혼재로 저장 → XSS 시 탈취 위험 | 토큰 보관 표준 부재 | flutter_secure_storage (iOS Keychain + Android Keystore)에만 저장. localStorage(SharedPreferences) 절대 사용 X (§ 7.2) |
| Refresh Token 갱신 race condition — 토큰 만료 시 동시 요청 N개가 동시 refresh → 서버에서 conflict | 클라이언트가 race 차단 안 함 | Dio Interceptor에 Mutex 또는 synchronized 패키지로 refresh 직렬화 + queueing (§ 6.4) |
| API 변경 시 클라이언트가 깨졌는지 백엔드 머지 후에야 발견 | 계약 검증 없음 | 04번 OpenAPI yaml에서 dart 모델 자동 생성 (build_runner + retrofit_generator) — 백엔드 PR과 클라이언트 PR이 같은 spec 보장 (§ 6.2) |
| 에러 메시지를 화면에 그대로 노출 (예: SQL exception 한 줄) | 에러 매핑 표준 부재 | RFC 9457 ProblemDetail의 code enum 13종을 사용자 메시지로 매핑 (§ 12.1) |
| WebSocket 연결이 끊기면 사용자가 모름 | 연결 상태 UI 없음 | STOMP 연결 상태 Provider + AppBar에 연결 indicator (§ 9.4) |

### 1.3 Owner 책임 분담 + 페어 구조

| 영역 | Primary | 페어 백업 |
| --- | --- | --- |
| Flutter 프로젝트 골격·라우팅·상태 관리 | 김지민 | 강태오 (Lead) |
| 인증 토큰·secure_storage·Refresh 흐름 | 김지민 | 이지윤 (Auth Service Owner — API 계약 합의) |
| AI SSE 클라이언트 | 김지민 | 강상민 (AI Service Owner — SSE 이벤트 4종류 합의) |
| STOMP 알림 클라이언트 | 김지민 | 강태오 (BFF Aggregator Owner — STOMP CONNECT 합의) |
| 디자인 시스템·테마·국제화 | 김지민 | (단독) |
| 입체 묵상 화면 Sliver 스크롤 | 김지민 | 강태오 (Lead — 수업 진도 검증) |
| 빌드·CI/CD (Android/iOS 분리) | 김지민 + 강태오 | (페어) |

01번 § 6.6 D 페어 매트릭스: 김지민 ↔ 강상민 | AI 대화 Flutter UI ↔ AI Service 계약. SSE 이벤트 종류 변경 시 강상민과 페어 합의.

---

## 2. 기술 스택 결정

### 2.1 SDK + 언어 버전

| 항목 | 결정 | 근거 |
| --- | --- | --- |
| Flutter SDK | **3.24.x stable** (Dart 3.5+) | 2026-05 시점 stable 채널 — Material 3 default + Impeller renderer (Android stable) |
| Dart | **3.5+** | sealed class·pattern matching·records — 04번 ProblemDetail 매핑에 필수 |
| Min Android SDK | **API 24 (Android 7.0)** | 한국 시장 99%+ 커버 (Google Play 통계 기준) |
| Target Android SDK | **API 34 (Android 14)** | Google Play 정책 (2025년 8월부터 API 34 강제) |
| Min iOS | **iOS 14** | flutter_secure_storage·stomp_dart_client 모두 호환 |

> **W0 Lock-in:** 본 버전 외 다른 SDK 사용 X. lutter --version 결과를 lutter-app/.fvmrc 또는 README에 박제. 김지민이 fvm(Flutter Version Manager)로 버전 고정.

### 2.2 핵심 패키지 결정 표

| 영역 | 패키지 | 버전 | 대안 / 기각 사유 |
| --- | --- | --- | --- |
| 상태 관리 | **flutter_riverpod** | ^2.5.0 | Bloc — boilerplate 많음 / Provider — 상태 합성 부족 / GetX — 마법 메서드 많아 디버깅 어려움 |
| 코드 생성 | **riverpod_generator** | ^2.4.0 | 수동 Provider 작성 — 타입 안전성 ↓ |
| 라우팅 | **go_router** | ^14.0.0 | Navigator 2.0 직접 사용 — 학습 곡선 ↑ / auto_route — 수업 커버 X |
| HTTP 클라이언트 | **dio** | ^5.4.0 | http 패키지 — Interceptor·취소 토큰 부족 |
| HTTP DTO 코드 생성 | **retrofit** + retrofit_generator | ^4.1.0 | chopper — 사용자 적음 |
| JSON 직렬화 | **json_serializable** + json_annotation | ^6.7.0 / ^4.9.0 | (필수) |
| 불변 모델 | **freezed** + freezed_annotation | ^2.5.0 / ^2.4.0 | data class 직접 작성 — copyWith·equals 보일러플레이트 |
| 보안 저장소 | **flutter_secure_storage** | ^9.2.0 | shared_preferences — XSS 또는 root 시 노출 |
| WebSocket (STOMP) | **stomp_dart_client** | ^2.0.0 | web_socket_channel 직접 — STOMP 프레임 파싱 부담 |
| SSE | (직접 구현 with dio) | (Dart Stream API 활용) | dio_sse — 패키지 maintenance 불활성 → 직접 구현 (§ 8.2) |
| 로컬 저장 | **drift** (선택) | ^2.16.0 | v1.0은 사용 X (offline 지원 X), v1.1에 도입 |
| 분석·로깅 | **sentry_flutter** | ^8.4.0 | Firebase Crashlytics — 백엔드 Loki와 추적 ID 연동 어려움 |
| 국제화 | **flutter_localizations** + intl | (SDK 내장) / ^0.19.0 | (Flutter 표준) |

### 2.3 패키지 versioning 정책

- **모든 dependency는 caret(^) 범위로 명시** — minor 업데이트는 자동, breaking change 차단
- **pubspec.lock은 commit한다** — CI·로컬·다른 팀원 모두 동일 의존성 트리
- **breaking change 발견 시 ADR 작성** — 09번 ADR 디렉토리에 (예:  013-flutter-riverpod-3-migration.md)
- **dev_dependency는 pubspec.yaml에 명시** — build_runner, riverpod_generator, retrofit_generator, json_serializable, freezed, mockito, flutter_test (SDK), integration_test (SDK)

### 2.4 패키지 보안 검증

W1 시작 시 김지민이 다음을 1회 실행:

`ash
flutter pub deps --json > deps.json
flutter pub outdated  # 오래된 패키지 확인
`

각 패키지의 pub.dev 점수 80+ + maintainer가 활성인지 확인. 알려진 CVE는 Snyk 또는 OSV 검색.

---

## 3. 프로젝트 구조 (Clean Architecture)

### 3.1 폴더 구조 — feature 단위 분리

lutter-app/ 프로젝트는 **feature 단위로 분리** (auth, dashboard, passage, ai_session, journal). 각 feature 안에 layer (data·domain·presentation) 분리. 1차 HMS의 "controller·service·dao 묶음" 패턴 반복 X — feature 간 격리가 service 격리와 자연스럽게 매칭.

`
flutter-app/
├── lib/
│   ├── main.dart                         # 진입점 (ProviderScope + MyApp)
│   ├── app.dart                          # MaterialApp.router + 테마
│   ├── core/                             # 모든 feature 공통
│   │   ├── config/
│   │   │   ├── env.dart                  # API_BASE_URL, BFF_BASE_URL 등 (.env 파싱)
│   │   │   └── flavors.dart              # dev / staging / prod
│   │   ├── di/
│   │   │   └── providers.dart            # 글로벌 Riverpod Provider (DioProvider 등)
│   │   ├── network/
│   │   │   ├── dio_client.dart           # Dio + Interceptor 조립
│   │   │   ├── auth_interceptor.dart     # JWT 헤더 부착 + 401 시 refresh
│   │   │   ├── problem_detail.dart       # RFC 9457 매핑 (freezed)
│   │   │   └── api_exception.dart        # ProblemDetail → ApiException 변환
│   │   ├── storage/
│   │   │   ├── secure_storage.dart       # flutter_secure_storage wrapper
│   │   │   └── storage_keys.dart         # 키 명명 표준 (§ 7.3)
│   │   ├── sse/
│   │   │   └── sse_client.dart           # SSE 직접 구현 (§ 8.2)
│   │   ├── websocket/
│   │   │   └── stomp_client.dart         # stomp_dart_client wrapper
│   │   ├── ui/
│   │   │   ├── theme.dart                # Material 3 테마 + 디자인 토큰
│   │   │   ├── widgets/                  # 공통 위젯 (LoadingIndicator·ErrorBanner 등)
│   │   │   └── snackbar.dart             # 표준 Snackbar 헬퍼
│   │   └── l10n/                         # 국제화 (KR 우선, EN v1.1)
│   │       ├── app_ko.arb
│   │       └── app_en.arb (v1.1)
│   ├── features/
│   │   ├── auth/
│   │   │   ├── data/
│   │   │   │   ├── auth_api.dart         # Retrofit 인터페이스 (login/register/refresh/logout/oauth/me)
│   │   │   │   ├── auth_api.g.dart       # 자동 생성
│   │   │   │   └── auth_repository.dart  # API 호출 + secure_storage
│   │   │   ├── domain/
│   │   │   │   ├── user.dart             # freezed User 모델
│   │   │   │   └── token_pair.dart       # freezed TokenPair
│   │   │   └── presentation/
│   │   │       ├── login_page.dart
│   │   │       ├── register_page.dart
│   │   │       └── auth_provider.dart    # Riverpod AuthNotifier
│   │   ├── dashboard/
│   │   │   ├── data/dashboard_api.dart   # Retrofit (BFF /me/dashboard)
│   │   │   ├── domain/dashboard.dart
│   │   │   └── presentation/dashboard_page.dart
│   │   ├── passage/                      # 입체 묵상
│   │   │   ├── data/passage_api.dart     # Retrofit (BFF /passages/...)
│   │   │   ├── domain/
│   │   │   └── presentation/passage_view_page.dart
│   │   ├── ai_session/                   # AI 큐티 4단계
│   │   │   ├── data/
│   │   │   │   ├── ai_api.dart           # Retrofit (sessions, abandon)
│   │   │   │   └── ai_sse_client.dart    # SSE 전용 (turns endpoint)
│   │   │   ├── domain/
│   │   │   │   ├── session.dart
│   │   │   │   └── turn.dart
│   │   │   └── presentation/
│   │   │       ├── ai_session_page.dart
│   │   │       └── ai_session_provider.dart  # StreamNotifier
│   │   ├── journal/
│   │   │   ├── data/journal_api.dart
│   │   │   ├── domain/journal.dart
│   │   │   └── presentation/
│   │   │       ├── journal_list_page.dart
│   │   │       ├── journal_detail_page.dart
│   │   │       └── journal_edit_page.dart
│   │   └── notifications/
│   │       ├── data/notifications_stomp.dart  # STOMP 구독
│   │       └── presentation/notifications_provider.dart  # StreamNotifier
│   └── router/
│       ├── app_router.dart               # go_router 설정
│       └── auth_guard.dart               # redirect 함수
├── test/
│   ├── features/                         # feature별 widget·unit test
│   └── core/                             # core 모듈 unit test
├── integration_test/                     # 통합 테스트 (E2E)
├── android/
├── ios/
├── pubspec.yaml
├── pubspec.lock
├── analysis_options.yaml                 # Lint 규칙
├── build.yaml                            # build_runner 설정
└── README.md
`

### 3.2 Layer 책임 정의

각 feature 안의 3 layer:

| Layer | 책임 | 의존 방향 |
| --- | --- | --- |
| **presentation** | Widget·Provider·UI 상태 | domain만 의존 (data 직접 X) |
| **domain** | freezed 모델·Repository interface(선택) | (의존 X — 순수 Dart) |
| **data** | API 클라이언트·DTO·Repository 구현 | domain만 의존 |

> **ArchUnit 같은 검증은 Flutter에 없지만**, dart analyze + nalysis_options.yaml의 import 규칙으로 강제 가능. 또는 PR 리뷰 체크리스트에 명시 (§ 16).

### 3.3 import 규칙 (ArchUnit 대용)

nalysis_options.yaml에 다음을 추가 — dart analyze 시 import 위반 즉시 발견:

`yaml
analyzer:
  errors:
    # presentation layer가 data layer를 직접 import 하면 error
    invalid_use_of_internal_member: error
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"

linter:
  rules:
    # 절대 path import 강제 (상대 path ../../../ 금지 — 의존 방향 헷갈림)
    always_use_package_imports: true
    # 사용 안 하는 import 금지
    unused_import: error
    # public API 문서화
    public_member_api_docs: false  # v1.0은 false, v1.1에 true
`

추가로 dart_code_metrics 패키지 도입 시 더 강한 import 룰 가능 (v1.1 검토).

---
## 4. 상태 관리 — Riverpod 2.x

### 4.1 Riverpod 선택 근거 + 표준 Provider 종류 매트릭스

Riverpod 2.x는 컴파일 타임 안정성·코드 생성·테스트 편의성에서 Bloc·Provider·GetX보다 우위. 김지민의 수업 진도(RiverPod 커버됨)와 정확히 매칭.

다음 5종 Provider만 사용. 다른 종류 도입 시 ADR 필요:

| Provider 종류 | 용도 | 예시 |
| --- | --- | --- |
| `Provider` | 불변 의존성 (Dio·Repository·Service) | `dioProvider`, `authRepositoryProvider` |
| `FutureProvider` | 1회성 비동기 데이터 (Bible 책 목록 등 read-only) | `booksProvider` |
| `StreamProvider` | 지속 스트림 (STOMP 알림·SSE 토큰) | `notificationsStreamProvider`, `aiSessionTurnsProvider` |
| `AsyncNotifier` | 비동기 상태 + 변경 메서드 (login·logout 등) | `authNotifierProvider` |
| `Notifier` | 동기 상태 + 변경 메서드 (UI 토글·필터 등) | `journalFilterProvider` |

### 4.2 Provider 코드 생성 표준

riverpod_generator로 모든 Provider 자동 생성. 수동 작성 X.

```dart
// lib/features/auth/presentation/auth_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
import '../data/auth_repository.dart';
import '../domain/user.dart';

part 'auth_provider.g.dart';

@riverpod
class AuthNotifier extends _$AuthNotifier {
  @override
  Future<User?> build() async {
    final repo = ref.watch(authRepositoryProvider);
    final token = await repo.readAccessToken();
    if (token == null) return null;
    return await repo.fetchMe();
  }

  Future<void> login({required String email, required String password}) async {
    state = const AsyncValue.loading();
    state = await AsyncValue.guard(() async {
      final repo = ref.read(authRepositoryProvider);
      await repo.login(email: email, password: password);
      return await repo.fetchMe();
    });
  }

  Future<void> logout() async {
    final repo = ref.read(authRepositoryProvider);
    await repo.logout();
    state = const AsyncValue.data(null);
  }
}
```

build_runner 명령:

```bash
dart run build_runner build --delete-conflicting-outputs
# 또는 watch 모드
dart run build_runner watch --delete-conflicting-outputs
```

### 4.3 Provider 의존성 그래프 표준

| 화면 (Page) | 사용하는 Provider | 흐름 |
| --- | --- | --- |
| LoginPage | `authNotifierProvider` | 로그인 메서드 호출 + state 관찰 |
| DashboardPage | `dashboardProvider` (FutureProvider) | BFF /me/dashboard 호출 결과 |
| PassageViewPage | `passageProvider(bookCode, chapter, verse)` family | BFF /passages/.../... 호출 |
| AiSessionPage | `aiSessionProvider(sessionId)` (StreamNotifier) + `aiSessionMetaProvider` | SSE 스트림 + 세션 메타 합성 |
| JournalListPage | `journalListProvider` + `journalFilterProvider` | 페이지네이션 + 필터 합성 |
| (모든 화면) | `notificationsStreamProvider` (전역) | STOMP 알림 — AppBar에 indicator |

### 4.4 ref.watch vs ref.read vs ref.listen

**원칙:**
- **build 메서드 안에서는 `ref.watch`** — Provider 값 변경 시 자동 rebuild
- **이벤트 핸들러 (onPressed 등) 안에서는 `ref.read`** — 1회 읽기만, rebuild X
- **side effect (Snackbar·Navigation 등) 위해서는 `ref.listen`** — 변경 감지 + 작업

```dart
class LoginPage extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authNotifierProvider);

    ref.listen<AsyncValue<User?>>(authNotifierProvider, (previous, next) {
      if (next.value != null && previous?.value == null) {
        context.go('/dashboard');
      }
      if (next.hasError) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(next.error.toString())),
        );
      }
    });

    return Scaffold(
      body: ElevatedButton(
        onPressed: () {
          ref.read(authNotifierProvider.notifier).login(
            email: emailController.text,
            password: passwordController.text,
          );
        },
        child: const Text('로그인'),
      ),
    );
  }
}
```

### 4.5 Provider 격리 원칙

- **feature 간 Provider 직접 참조 금지** — feature_A의 Provider가 feature_B의 Provider를 watch 하면 결합도 증가
- 공유 데이터(예: 현재 User·연결 상태)는 `core/di/providers.dart`에 둠
- feature는 core의 Provider만 watch

```dart
// 안티 패턴 — journal feature가 auth feature 직접 참조
final journalListProvider = FutureProvider<List<Journal>>((ref) async {
  final user = await ref.watch(authNotifierProvider.future);  // feature 간 결합
  // ...
});

// 표준 — core에 currentUserIdProvider 두고 journal은 그것만 watch
// lib/core/di/providers.dart
@riverpod
Future<int?> currentUserId(CurrentUserIdRef ref) async {
  final user = await ref.watch(authNotifierProvider.future);
  return user?.id;
}

// lib/features/journal/presentation/journal_list_provider.dart
@riverpod
Future<List<Journal>> journalList(JournalListRef ref) async {
  final userId = await ref.watch(currentUserIdProvider.future);
  if (userId == null) return [];
  final repo = ref.watch(journalRepositoryProvider);
  return repo.list(userId: userId);
}
```

### 4.6 자주 빠지는 함정 메트릭스

| 함정 | 증상 | 원인 | 해결 |
| --- | --- | --- | --- |
| `setState` 호출 | 화면 일부 안 그려짐 | Riverpod 프로젝트에서 StatefulWidget setState 사용 | `ConsumerStatefulWidget` + `ref.read().notifier.method()` 으로 전환 |
| `ref.watch` vs `ref.read` 혼동 | 불필요한 rebuild | build 밖에서 watch 호출 | build안에서만 watch, 콜백(onPressed 등)에서는 read |
| Provider 의존 cycle | runtime crash | `aProvider → bProvider → aProvider` | DI 구조 재설계 — core/di/providers.dart에서 단방향 그래프 계수 |
| `AsyncValue.error` 무시 | 에러 상황 표시 안 됨 | `state.when(error: ..., data: ...)` 에서 생략 | 모든 when에 error/loading/data 3상태 모두 처리 (§ 12 참조) |
| `keepAlive: true` 남발 | 메모리 누수 | 잠시 쓰고 잊은 Provider에 keepAlive | `dioProvider`·`stompClientProvider`·`notificationsStreamProvider`만 keepAlive |
| Provider family 인자 변경 | 매번 새 instance | family 인자가 record 아닌 Map | record `({String book, int ch})` 또는 freezed equatable 객체로 전달 |

---

## 5. 라우팅 — go_router

### 5.1 선언적 라우팅 + 인증 가드

go_router 14.x 사용. Navigator 2.0의 선언적 API를 깔끔하게 wrapping. 인증 가드는 `redirect` 함수 한 곳에 박제.

```dart
// lib/router/app_router.dart
import 'package:go_router/go_router.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'app_router.g.dart';

@riverpod
GoRouter appRouter(AppRouterRef ref) {
  final auth = ref.watch(authNotifierProvider);

  return GoRouter(
    initialLocation: '/dashboard',
    redirect: (context, state) {
      final isLoggingIn = state.matchedLocation == '/login' || state.matchedLocation == '/register';
      final isAuthenticated = auth.value != null;

      if (!isAuthenticated && !isLoggingIn) return '/login';
      if (isAuthenticated && isLoggingIn) return '/dashboard';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (_, __) => const LoginPage()),
      GoRoute(path: '/register', builder: (_, __) => const RegisterPage()),
      GoRoute(
        path: '/dashboard',
        builder: (_, __) => const DashboardPage(),
        routes: [
          GoRoute(
            path: 'passage/:bookCode/:chapter/:verse',
            builder: (context, state) => PassageViewPage(
              bookCode: state.pathParameters['bookCode']!,
              chapter: int.parse(state.pathParameters['chapter']!),
              verse: int.parse(state.pathParameters['verse']!),
            ),
          ),
        ],
      ),
      GoRoute(
        path: '/ai/sessions/:sessionId',
        builder: (context, state) => AiSessionPage(
          sessionId: int.parse(state.pathParameters['sessionId']!),
        ),
      ),
      GoRoute(
        path: '/journals',
        builder: (_, __) => const JournalListPage(),
        routes: [
          GoRoute(
            path: 'new',
            builder: (_, __) => const JournalEditPage.create(),
          ),
          GoRoute(
            path: ':journalId',
            builder: (context, state) => JournalDetailPage(
              journalId: int.parse(state.pathParameters['journalId']!),
            ),
          ),
          GoRoute(
            path: ':journalId/edit',
            builder: (context, state) => JournalEditPage.edit(
              journalId: int.parse(state.pathParameters['journalId']!),
            ),
          ),
        ],
      ),
    ],
    errorBuilder: (context, state) => NotFoundPage(message: state.error.toString()),
  );
}
```

### 5.2 Navigation 호출 표준

- `context.go('/path')` — replace (back stack 제거)
- `context.push('/path')` — push (back으로 돌아갈 수 있음)
- `context.pop()` — back

| 시나리오 | 메서드 | 이유 |
| --- | --- | --- |
| 로그인 성공 → Dashboard | `context.go('/dashboard')` | back으로 로그인 화면 못 돌아오게 |
| 로그아웃 → 로그인 | `context.go('/login')` | 동일 |
| Dashboard → 묵상 노트 목록 | `context.push('/journals')` | back으로 Dashboard 돌아올 수 있게 |
| 묵상 노트 작성 → 목록 | `context.pop()` (또는 `context.go('/journals')`) | 작성 후 목록으로 |
| 알림 클릭 → 새 Journal 자동 생성 | `context.push('/journals/$journalId')` | back으로 이전 화면 |

### 5.3 Deeplink 표준 (v1.1 검토)

v1.0은 deeplink 사용 X (시연에 외부 알림 X). v1.1에 push notification(FCM) 도입 시 다음 deeplink 지원:

| URL | 동작 |
| --- | --- |
| `qtai://journal/{id}` | JournalDetailPage 열기 |
| `qtai://session/{id}` | AiSessionPage 이어서 |

`go_router`의 `routerDelegate.parseRouteInformation`으로 deeplink 처리.

---

## 6. 네트워크 레이어 — Dio + Retrofit + Interceptor

### 6.1 Dio 인스턴스 + Provider

```dart
// lib/core/network/dio_client.dart
import 'package:dio/dio.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'auth_interceptor.dart';
import '../config/env.dart';

part 'dio_client.g.dart';

@Riverpod(keepAlive: true)
Dio dio(DioRef ref) {
  final dio = Dio(BaseOptions(
    baseUrl: Env.apiBaseUrl,  // 예: http://qtai.local/api/v1
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    sendTimeout: const Duration(seconds: 10),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    validateStatus: (status) => status != null && status >= 200 && status < 500,
  ));
  dio.interceptors.add(AuthInterceptor(ref));
  dio.interceptors.add(LogInterceptor(
    requestBody: false,
    responseBody: false,
    request: true,
    requestHeader: false,
  ));
  return dio;
}
```

**인터셉터 체이닝 흐름 (⚠️ 순서 주의):**

```
Request 흐름:
  TraceInterceptor.onRequest    → W3C traceparent 헤더 생성 (§ 6.4.1)
  AuthInterceptor.onRequest     → Authorization 헤더 첨부
  LogInterceptor.onRequest      → 로그 (Authorization 마스킹)

Response 흐름 (역순):
  LogInterceptor.onResponse
  AuthInterceptor.onResponse    (no-op)
  TraceInterceptor.onResponse   (no-op)

Error 흐름 (역순):
  LogInterceptor.onError
  AuthInterceptor.onError       → 401 시 Refresh + retry (§ 6.4)
  TraceInterceptor.onError
```

> **⚠️ 입력 순서 주의:** TraceInterceptor가 AuthInterceptor보다 먼저 `add` 되어야 요청 시 traceparent가 먼저 생성되고, 에러 시 역순으로 AuthInterceptor의 401 retry가 TraceInterceptor보다 먼저 실행됨. 수동 재시도 완료 후에도 traceparent는 동일하게 유지되어야 분산 추적이 일관됨.

### 6.2 Retrofit 인터페이스 — API 계약 자동 생성

04번 OpenAPI yaml에서 dart 모델 자동 생성하는 패턴은 v1.1 (`openapi_generator` 패키지). v1.0은 김지민이 직접 Retrofit 인터페이스 작성 + 백엔드 owner와 페어 합의.

```dart
// lib/features/auth/data/auth_api.dart
import 'package:dio/dio.dart';
import 'package:retrofit/retrofit.dart';
import '../domain/user.dart';
import '../domain/token_pair.dart';

part 'auth_api.g.dart';

@RestApi()
abstract class AuthApi {
  factory AuthApi(Dio dio, {String baseUrl}) = _AuthApi;

  @POST('/auth/register')
  Future<User> register(@Body() RegisterRequest request);

  @POST('/auth/login')
  Future<TokenPair> login(@Body() LoginRequest request);

  @POST('/auth/refresh')
  Future<TokenPair> refresh(@Body() RefreshRequest request);

  @POST('/auth/logout')
  Future<void> logout(@Body() RefreshRequest request);

  @GET('/auth/me')
  Future<User> me();

  @POST('/auth/me/deactivate')
  Future<void> deactivate();

  @POST('/auth/oauth/google')
  Future<TokenPair> oauthGoogle(@Body() OAuthGoogleRequest request);
}
```

### 6.3 freezed DTO + json_serializable

```dart
// lib/features/auth/domain/user.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'user.freezed.dart';
part 'user.g.dart';

@freezed
class User with _$User {
  const factory User({
    required int id,
    required String email,
    required String nickname,
    required String role,  // ROLE_USER | ROLE_ADMIN
    @Default(false) bool emailVerified,
    required DateTime createdAt,
  }) = _User;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
}

// lib/features/auth/domain/token_pair.dart
@freezed
class TokenPair with _$TokenPair {
  const factory TokenPair({
    required String accessToken,
    required String refreshToken,
    required int expiresIn,
    required int refreshExpiresIn,
  }) = _TokenPair;

  factory TokenPair.fromJson(Map<String, dynamic> json) => _$TokenPairFromJson(json);
}
```

### 6.4 AuthInterceptor — JWT 부착 + 401 시 Refresh + race 차단

```dart
// lib/core/network/auth_interceptor.dart
import 'package:dio/dio.dart';
import 'package:riverpod/riverpod.dart';
import 'package:synchronized/synchronized.dart';
import '../storage/secure_storage.dart';

class AuthInterceptor extends QueuedInterceptor {
  final Ref ref;
  final Lock _refreshLock = Lock();

  AuthInterceptor(this.ref);

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    if (options.path.startsWith('/auth/login') ||
        options.path.startsWith('/auth/register') ||
        options.path.startsWith('/auth/refresh') ||
        options.path.startsWith('/auth/oauth/google')) {
      return handler.next(options);
    }
    final accessToken = await SecureStorage.instance.readAccessToken();
    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    return handler.next(options);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    // 401 — Access Token 만료 → Refresh 시도
    if (err.response?.statusCode == 401 &&
        err.requestOptions.extra['_retried'] != true) {
      // 동시 401 N개가 와도 Refresh는 1번만 실행 (race 차단)
      final newTokens = await _refreshLock.synchronized<TokenPair?>(() async {
        // 다른 thread가 이미 갱신했으면 그 토큰 사용
        final currentAccess = await SecureStorage.instance.readAccessToken();
        if (currentAccess != null && currentAccess != _extractToken(err.requestOptions)) {
          return TokenPair(
            accessToken: currentAccess,
            refreshToken: await SecureStorage.instance.readRefreshToken() ?? '',
            expiresIn: 0,
            refreshExpiresIn: 0,
          );
        }
        try {
          final refreshToken = await SecureStorage.instance.readRefreshToken();
          if (refreshToken == null) return null;
          final dio = Dio(BaseOptions(baseUrl: err.requestOptions.baseUrl));
          final res = await dio.post('/auth/refresh', data: {'refreshToken': refreshToken});
          final tokens = TokenPair.fromJson(res.data);
          await SecureStorage.instance.writeTokens(
            access: tokens.accessToken,
            refresh: tokens.refreshToken,
          );
          return tokens;
        } catch (_) {
          await SecureStorage.instance.clearTokens();
          ref.invalidate(authNotifierProvider);
          return null;
        }
      });

      if (newTokens != null) {
        err.requestOptions.headers['Authorization'] = 'Bearer ${newTokens.accessToken}';
        err.requestOptions.extra['_retried'] = true;
        try {
          final response = await ref.read(dioProvider).fetch(err.requestOptions);
          return handler.resolve(response);
        } catch (e) {
          return handler.next(err);
        }
      }
    }
    return handler.next(err);
  }

  String _extractToken(RequestOptions options) =>
      (options.headers['Authorization'] as String? ?? '').replaceFirst('Bearer ', '');
}
```

핵심:
- `QueuedInterceptor` 사용 — 동시 401 응답이 와도 onError는 큐로 직렬 처리
- `synchronized`로 refresh를 1회만 실행 — race condition 차단 (1차 사고 패턴 방어)
- `_retried` extra flag로 무한 재시도 차단

#### 6.4.1 TraceInterceptor — W3C Trace Context 자동 생성

분산 추적은 Flutter 요청이 Gateway → BFF → 4 service → Kafka envelope까지 **같은 traceId로 연결**되어야 Tempo에서 전 구간 span tree로 조회 가능. Flutter가 요청 마다 W3C traceparent 헤더를 생성해서 보내야 함.

```dart
// lib/core/network/trace_interceptor.dart
import 'dart:math';
import 'package:dio/dio.dart';

class TraceInterceptor extends Interceptor {
  static final _random = Random.secure();

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    // W3C traceparent: version-trace_id-span_id-flags
    final traceId = _hex(16);  // 32 hex chars
    final spanId = _hex(8);    // 16 hex chars
    options.headers['traceparent'] = '00-$traceId-$spanId-01';
    options.extra['traceId'] = traceId;
    handler.next(options);
  }

  String _hex(int bytes) {
    final buf = StringBuffer();
    for (var i = 0; i < bytes; i++) {
      buf.write(_random.nextInt(256).toRadixString(16).padLeft(2, '0'));
    }
    return buf.toString();
  }
}
```

Dio Provider에 등록:

```dart
dio.interceptors.add(TraceInterceptor());           // 1. traceparent 먼저
dio.interceptors.add(AuthInterceptor(ref));         // 2. Authorization
dio.interceptors.add(LogInterceptor(...));          // 3. 로그
```

**사용 시나리오:**
- 사용자가 "AI 답변이 이상해요" 신고 → Sentry에 필수로 traceId 포함 (§ 15.3) → 운영자가 Tempo에서 해당 traceId 검색 → Flutter→Gateway→BFF→AI Service→Anthropic 전 구간 로그 1회 조회.
- 06번 § 12와 정합 (W3C Trace Context 표준).

### 6.5 ProblemDetail 매핑

```dart
// lib/core/network/problem_detail.dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'problem_detail.freezed.dart';
part 'problem_detail.g.dart';

@freezed
class ProblemDetail with _$ProblemDetail {
  const factory ProblemDetail({
    required String type,
    required String title,
    required int status,
    required String code,
    String? detail,
    String? instance,
    String? traceId,
  }) = _ProblemDetail;

  factory ProblemDetail.fromJson(Map<String, dynamic> json) => _$ProblemDetailFromJson(json);
}

// lib/core/network/api_exception.dart
class ApiException implements Exception {
  final ProblemDetail problem;
  ApiException(this.problem);

  String get userMessage => _codeToUserMessage(problem.code);

  static String _codeToUserMessage(String code) => switch (code) {
    'INVALID_CREDENTIALS' => '이메일 또는 비밀번호가 올바르지 않습니다.',
    'EMAIL_DUPLICATE' => '이미 가입된 이메일입니다.',
    'TOKEN_EXPIRED' => '세션이 만료되었습니다. 다시 로그인해 주세요.',
    'RATE_LIMITED' => '잠시 후 다시 시도해 주세요.',
    'JOURNAL_NOT_OWNED' => '본인 노트만 열람할 수 있습니다.',
    'INVALID_STATUS_TRANSITION' => '발행된 노트는 다시 초안으로 되돌릴 수 없습니다.',
    'LLM_UNAVAILABLE' => 'AI 응답에 일시적인 문제가 발생했습니다.',
    'LLM_TIMEOUT' => 'AI 응답이 늦어지고 있습니다. 잠시 후 다시 시도해 주세요.',
    'PROMPT_INJECTION_DETECTED' => '입력에 허용되지 않는 내용이 포함되어 있습니다.',
    'PASSAGE_NOT_FOUND' => '해당 구절을 찾을 수 없습니다.',
    'SERVICE_UNAVAILABLE' => '서비스 일부에 일시적인 문제가 발생했습니다.',
    _ => '요청을 처리하지 못했습니다. 잠시 후 다시 시도해 주세요.',
  };
}
```

### 6.6 BFF용 별도 Dio 인스턴스 (선택)

BFF Aggregator는 base URL이 다를 수 있음 (실제로는 같은 Gateway 통해 라우팅이지만, 분리 가독성 위해 wrapping). v1.0은 단일 Dio 사용 + path로 구분.

---

## 7. 인증 — JWT·Refresh Rotation·secure_storage

### 7.1 토큰 lifecycle 표준 (5 phase)

| Phase | 트리거 | 동작 |
| --- | --- | --- |
| **1. 발급** | 로그인 성공 / OAuth Google 성공 | TokenPair 응답 → secure_storage에 저장 → AuthNotifier가 User 호출 |
| **2. 사용** | API 호출 마다 | AuthInterceptor가 Authorization 헤더 부착 |
| **3. 갱신** | 401 + Refresh Token 유효 | AuthInterceptor가 /auth/refresh 호출 → 새 TokenPair 저장 → 원 요청 재시도 |
| **4. 폐기 (정상)** | 사용자 로그아웃 | /auth/logout 호출 → secure_storage clear → AuthNotifier state = null |
| **5. 폐기 (강제)** | Refresh 실패 (만료·revoke·blacklist) | secure_storage clear → AuthNotifier invalidate → 자동으로 /login 리다이렉트 (router redirect) |

### 7.2 secure_storage 사용 + 절대 위반 금지

**1차 사고 패턴:** 토큰을 cookie + localStorage 혼재 → XSS 시 탈취

**2차 가드레일:**
- 토큰은 `flutter_secure_storage`에만 저장 (iOS Keychain + Android EncryptedSharedPreferences 또는 Keystore)
- `shared_preferences`, `path_provider`로 파일 시스템에 저장 ❌
- 메모리 변수에 토큰 평문 보관 ❌ (가능한 한 storage에서 read 후 즉시 사용)

```dart
// lib/core/storage/secure_storage.dart
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'storage_keys.dart';

class SecureStorage {
  static final SecureStorage instance = SecureStorage._();
  SecureStorage._();

  static const _options = AndroidOptions(
    encryptedSharedPreferences: true,
  );
  static const _iOSOptions = IOSOptions(
    accessibility: KeychainAccessibility.first_unlock,
  );

  final _storage = const FlutterSecureStorage(
    aOptions: _options,
    iOptions: _iOSOptions,
  );

  Future<void> writeTokens({required String access, required String refresh}) async {
    await Future.wait([
      _storage.write(key: StorageKeys.accessToken, value: access),
      _storage.write(key: StorageKeys.refreshToken, value: refresh),
    ]);
  }

  Future<String?> readAccessToken() => _storage.read(key: StorageKeys.accessToken);
  Future<String?> readRefreshToken() => _storage.read(key: StorageKeys.refreshToken);

  Future<void> clearTokens() async {
    await Future.wait([
      _storage.delete(key: StorageKeys.accessToken),
      _storage.delete(key: StorageKeys.refreshToken),
    ]);
  }
}
```

### 7.3 Storage 키 명명 표준

```dart
// lib/core/storage/storage_keys.dart
class StorageKeys {
  StorageKeys._();

  // 인증 토큰
  static const accessToken = 'auth.access_token';
  static const refreshToken = 'auth.refresh_token';

  // 사용자 식별 (UI 즉시 표시 용 — 검증은 서버가)
  static const cachedUserId = 'auth.cached_user_id';
  static const cachedNickname = 'auth.cached_nickname';

  // 디바이스 ID (v1.1 푸시 알림 등록용)
  static const deviceId = 'device.id';
}
```

**원칙:** 키는 `{namespace}.{name}` 형식. 평문 표시 가능한 데이터(닉네임 등)도 secure_storage 사용 — 일관성 + iOS App 삭제 시 자동 정리.

### 7.4 OAuth Google 로그인 흐름

```dart
// 1. google_sign_in 패키지로 ID Token 획득
import 'package:google_sign_in/google_sign_in.dart';

final googleSignIn = GoogleSignIn(scopes: ['email', 'openid']);
final account = await googleSignIn.signIn();
if (account == null) return;  // 사용자가 취소
final auth = await account.authentication;
final idToken = auth.idToken;
if (idToken == null) throw Exception('idToken 누락');

// 2. Auth Service에 ID Token 전송 → 백엔드가 JWK로 검증
final tokens = await ref.read(authRepositoryProvider).oauthGoogle(idToken: idToken);
// → AuthRepository.oauthGoogle은 내부적으로 secure_storage에 저장
```

> **김지민 ↔ 이지윤 페어 합의 사항 (W1):** Google ID Token의 만료(`exp`) 시각을 클라이언트에서 미리 검증할지, 백엔드 거절(401 OAUTH_TOKEN_INVALID)에 의존할지. 표준은 **백엔드 의존** — 클라이언트는 idToken을 그대로 전송, 검증은 서버.

### 7.5 자동 로그아웃 (Refresh 만료)

router의 `redirect` 함수가 `authNotifierProvider`의 state를 watch — Refresh 실패 시 state가 null이 되면 자동으로 /login으로.

추가로 SnackBar 또는 Dialog로 "세션이 만료되었습니다" 안내. `ref.listen<AsyncValue<User?>>`로 처리.

---

## 8. SSE 클라이언트 — AI 큐티 4단계 스트리밍

### 8.1 SSE 표준 — 04번 § 6.3과 정합

AI Service의 SSE는 4 종류 이벤트 발행:

| event 이름 | data 형태 | 의미 |
| --- | --- | --- |
| `token` | `{"text": "..."}` | LLM 토큰 1개 (스트리밍 표시) |
| `turn_completed` | `{"turnId": int, "ragSources": [{"docId": str, "relevance": float}]}` | 한 턴 완료 + RAG 출처 |
| `error` | `{"code": "LLM_TIMEOUT", "message": "..."}` | 오류 (사용자에게 표시) |
| `end` | `[DONE]` (또는 빈 객체) | 스트림 정상 종료 |

### 8.2 Dio + Stream 직접 구현

`dio_sse` 같은 외부 패키지는 maintenance 불활성. Dart의 `Stream<List<int>>` API + 텍스트 디코딩으로 직접 구현이 안전하고 디버깅 쉬움.

```dart
// lib/core/sse/sse_client.dart
import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';

class SseEvent {
  final String? event;  // event 이름 (없으면 'message')
  final String data;    // data 본문
  final String? id;     // SSE id (재연결용)

  SseEvent({this.event, required this.data, this.id});
}

class SseClient {
  final Dio dio;
  SseClient(this.dio);

  Stream<SseEvent> stream({
    required String path,
    required Map<String, dynamic> body,
    Map<String, String>? extraHeaders,
  }) async* {
    final response = await dio.post<ResponseBody>(
      path,
      data: body,
      options: Options(
        responseType: ResponseType.stream,
        headers: {
          'Accept': 'text/event-stream',
          'Cache-Control': 'no-cache',
          ...?extraHeaders,
        },
      ),
    );

    final responseBody = response.data!;
    final byteStream = responseBody.stream;
    final lineStream = byteStream
        .transform(utf8.decoder)
        .transform(const LineSplitter());

    String? eventName;
    String? eventId;
    final dataBuffer = StringBuffer();

    await for (final line in lineStream) {
      if (line.isEmpty) {
        // SSE 이벤트 종결 (빈 줄)
        if (dataBuffer.isNotEmpty) {
          yield SseEvent(
            event: eventName,
            data: dataBuffer.toString(),
            id: eventId,
          );
          eventName = null;
          eventId = null;
          dataBuffer.clear();
        }
        continue;
      }

      if (line.startsWith(':')) continue;  // 코멘트 라인 무시

      final colonIdx = line.indexOf(':');
      if (colonIdx == -1) continue;

      final field = line.substring(0, colonIdx);
      final value = line.substring(colonIdx + 1).trimLeft();

      switch (field) {
        case 'event':
          eventName = value;
          break;
        case 'data':
          if (dataBuffer.isNotEmpty) dataBuffer.write('\n');
          dataBuffer.write(value);
          break;
        case 'id':
          eventId = value;
          break;
      }
    }

    // 마지막 이벤트가 빈 줄 없이 끝나면 flush
    if (dataBuffer.isNotEmpty) {
      yield SseEvent(event: eventName, data: dataBuffer.toString(), id: eventId);
    }
  }
}
```

### 8.3 AI 세션 SSE Provider — StreamNotifier

```dart
// lib/features/ai_session/data/ai_sse_client.dart
import 'package:freezed_annotation/freezed_annotation.dart';
import '../../../core/sse/sse_client.dart';

part 'ai_sse_client.freezed.dart';

@freezed
class AiTurnEvent with _$AiTurnEvent {
  const factory AiTurnEvent.token(String text) = AiTurnEventToken;
  const factory AiTurnEvent.turnCompleted({
    required int turnId,
    required List<RagSource> ragSources,
  }) = AiTurnEventCompleted;
  const factory AiTurnEvent.error({required String code, required String message}) = AiTurnEventError;
  const factory AiTurnEvent.end() = AiTurnEventEnd;
}

@freezed
class RagSource with _$RagSource {
  const factory RagSource({required String docId, required double relevance}) = _RagSource;
  factory RagSource.fromJson(Map<String, dynamic> json) => _$RagSourceFromJson(json);
}

class AiSseClient {
  final SseClient sse;
  AiSseClient(this.sse);

  Stream<AiTurnEvent> turnStream({
    required int sessionId,
    required String step,
    required String content,
  }) {
    return sse.stream(
      path: '/ai/sessions/$sessionId/turns',
      body: {'step': step, 'content': content},
    ).map(_parseEvent);
  }

  AiTurnEvent _parseEvent(SseEvent raw) {
    switch (raw.event) {
      case 'token':
        final json = jsonDecode(raw.data) as Map<String, dynamic>;
        return AiTurnEvent.token(json['text'] as String);
      case 'turn_completed':
        final json = jsonDecode(raw.data) as Map<String, dynamic>;
        return AiTurnEvent.turnCompleted(
          turnId: json['turnId'] as int,
          ragSources: ((json['ragSources'] as List?) ?? [])
              .map((e) => RagSource.fromJson(e as Map<String, dynamic>))
              .toList(),
        );
      case 'error':
        final json = jsonDecode(raw.data) as Map<String, dynamic>;
        return AiTurnEvent.error(
          code: json['code'] as String,
          message: json['message'] as String,
        );
      case 'end':
        return const AiTurnEvent.end();
      default:
        return AiTurnEvent.error(code: 'UNKNOWN_EVENT', message: 'Unknown event: ${raw.event}');
    }
  }
}
```

### 8.4 화면에서 사용 — StreamNotifier 패턴

```dart
// lib/features/ai_session/presentation/ai_session_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'ai_session_provider.g.dart';

@riverpod
class AiSessionTurns extends _$AiSessionTurns {
  final List<Turn> _completed = [];
  final StringBuffer _streamingText = StringBuffer();

  @override
  Stream<AiSessionState> build(int sessionId) async* {
    yield AiSessionState(turns: const [], streamingText: '');
  }

  Future<void> sendMessage({required String step, required String content}) async {
    _streamingText.clear();
    final client = ref.read(aiSseClientProvider);
    await for (final event in client.turnStream(
      sessionId: sessionId,
      step: step,
      content: content,
    )) {
      switch (event) {
        case AiTurnEventToken(:final text):
          _streamingText.write(text);
          state = AsyncValue.data(AiSessionState(
            turns: List.unmodifiable(_completed),
            streamingText: _streamingText.toString(),
          ));
          break;
        case AiTurnEventCompleted(:final turnId, :final ragSources):
          _completed.add(Turn.assistant(
            id: turnId,
            content: _streamingText.toString(),
            ragSources: ragSources,
          ));
          _streamingText.clear();
          state = AsyncValue.data(AiSessionState(
            turns: List.unmodifiable(_completed),
            streamingText: '',
          ));
          break;
        case AiTurnEventError(:final code, :final message):
          state = AsyncValue.error(
            ApiException(ProblemDetail(
              type: '', title: 'AI 오류', status: 500,
              code: code, detail: message, instance: '',
            )),
            StackTrace.current,
          );
          return;
        case AiTurnEventEnd():
          return;
      }
    }
  }
}
```

### 8.5 SSE 안전 가드레일

| 위험 | 가드레일 |
| --- | --- |
| 사용자가 화면 나가도 스트림 계속 흐름 → 메모리·네트워크 누수 | `StreamNotifier`의 `ref.onDispose`로 stream subscription cancel |
| Anthropic 응답 30초+ 멈춤 | Dio `receiveTimeout: 60s` (4분 LLM 응답 대비), 타임아웃 시 ApiException 변환 |
| event 파싱 실패 (서버가 잘못된 JSON 보냄) | try-catch로 감싸고 ApiException error code `MALFORMED_SSE` 처리 |
| 동시에 같은 세션에 2 SSE 연결 | AI Service가 409 Conflict 반환 (04번 § 6.3) → 클라이언트가 SnackBar 표시 |
| Gateway buffering filter 적용 (SSE 끊김) | 04번 § 9.6 — Gateway가 SSE path 우회 (강태오 owner) |

> **김지민 ↔ 강상민 페어 합의 사항 (W1):** event 종류 4개(token/turn_completed/error/end) 외 추가 event(ex. `step_advanced`) 발생 시 스펙 합의 후 본 문서 + 04번 갱신.

---

## 9. STOMP WebSocket 클라이언트 — 알림

### 9.1 STOMP 선택 근거 + 04번 § 10.2와 정합

WebSocket 위에 STOMP 프로토콜 사용 — Spring 백엔드와 표준 매칭. 순수 WebSocket보다 메시지 라우팅(`/user/{userId}/queue/notifications`) + ACK + 자동 재연결이 쉬움.

### 9.2 stomp_dart_client wrapper

```dart
// lib/core/websocket/stomp_client.dart
import 'package:stomp_dart_client/stomp.dart';
import 'package:stomp_dart_client/stomp_config.dart';
import 'package:stomp_dart_client/stomp_frame.dart';
import '../storage/secure_storage.dart';
import '../config/env.dart';

class QtaiStompClient {
  StompClient? _client;
  final _connectionStateController = StreamController<StompConnectionState>.broadcast();

  Stream<StompConnectionState> get connectionState => _connectionStateController.stream;
  bool get isConnected => _client?.connected ?? false;

  Future<void> connect() async {
    final accessToken = await SecureStorage.instance.readAccessToken();
    if (accessToken == null) throw Exception('Access token 없음');

    _client = StompClient(
      config: StompConfig(
        url: Env.wsBaseUrl,  // 예: ws://qtai.local/api/v1/ws/notifications
        onConnect: _onConnect,
        onDisconnect: (_) => _connectionStateController.add(StompConnectionState.disconnected),
        onWebSocketError: (e) {
          _connectionStateController.add(StompConnectionState.error);
        },
        onStompError: (frame) {
          _connectionStateController.add(StompConnectionState.error);
        },
        beforeConnect: () async {
          _connectionStateController.add(StompConnectionState.connecting);
        },
        // STOMP CONNECT 프레임에 JWT 부착 (BFF가 검증 — 04번 § 10.2)
        stompConnectHeaders: {'Authorization': 'Bearer $accessToken'},
        webSocketConnectHeaders: {'Authorization': 'Bearer $accessToken'},
        // 자동 재연결 (5초 간격)
        reconnectDelay: const Duration(seconds: 5),
        // heartbeat (서버 30초, 클라 30초)
        heartbeatIncoming: const Duration(seconds: 30),
        heartbeatOutgoing: const Duration(seconds: 30),
      ),
    );
    _client!.activate();
  }

  void _onConnect(StompFrame frame) {
    _connectionStateController.add(StompConnectionState.connected);
  }

  Future<void> disconnect() async {
    _client?.deactivate();
    _connectionStateController.add(StompConnectionState.disconnected);
  }

  StompUnsubscribe? subscribe({
    required String destination,
    required void Function(StompFrame frame) callback,
  }) {
    if (!isConnected) return null;
    return _client!.subscribe(destination: destination, callback: callback);
  }
}

enum StompConnectionState { disconnected, connecting, connected, error }
```

### 9.3 알림 Provider — StreamProvider로 전역 관리

```dart
// lib/features/notifications/presentation/notifications_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'notifications_provider.g.dart';

@Riverpod(keepAlive: true)
class NotificationsStream extends _$NotificationsStream {
  @override
  Stream<Notification> build() async* {
    final stomp = ref.watch(stompClientProvider);
    final userId = await ref.watch(currentUserIdProvider.future);
    if (userId == null) return;

    if (!stomp.isConnected) {
      await stomp.connect();
    }

    final controller = StreamController<Notification>();

    final unsub = stomp.subscribe(
      destination: '/user/$userId/queue/notifications',
      callback: (frame) {
        try {
          final json = jsonDecode(frame.body!) as Map<String, dynamic>;
          controller.add(Notification.fromJson(json));
        } catch (e) {
          // 파싱 실패는 silently drop — 사용자에게 영향 X
        }
      },
    );

    ref.onDispose(() {
      unsub?.call(unsubscribeHeaders: {});
      controller.close();
    });

    yield* controller.stream;
  }
}

@freezed
class Notification with _$Notification {
  const factory Notification({
    required String notificationId,
    required int userId,
    required String type,  // JOURNAL_AUTO_CREATED 등 (events/schema/notification.requested-value.json)
    required Map<String, dynamic> payload,
    required DateTime requestedAt,
  }) = _Notification;

  factory Notification.fromJson(Map<String, dynamic> json) => _$NotificationFromJson(json);
}
```

### 9.4 연결 상태 UI — AppBar 인디케이터

```dart
// lib/core/ui/widgets/connection_indicator.dart
class ConnectionIndicator extends ConsumerWidget {
  const ConnectionIndicator({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stompClient = ref.watch(stompClientProvider);
    return StreamBuilder<StompConnectionState>(
      stream: stompClient.connectionState,
      builder: (context, snapshot) {
        final state = snapshot.data ?? StompConnectionState.disconnected;
        final color = switch (state) {
          StompConnectionState.connected => Colors.green,
          StompConnectionState.connecting => Colors.amber,
          StompConnectionState.error => Colors.red,
          StompConnectionState.disconnected => Colors.grey,
        };
        return Padding(
          padding: const EdgeInsets.all(8.0),
          child: Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
        );
      },
    );
  }
}
```

각 화면의 AppBar `actions`에 `ConnectionIndicator()` 1개 표시. 사용자가 한 눈에 알림 연결 상태 인지.

### 9.5 STOMP 안전 가드레일

| 위험 | 가드레일 |
| --- | --- |
| Refresh 후 토큰 변경 → STOMP 인증 만료 | `authNotifierProvider` listen → 토큰 변경 시 stomp `disconnect()` → `connect()` 재실행 |
| BFF Pod 재시작 → STOMP 끊김 | stomp_dart_client의 `reconnectDelay: 5s` 자동 재연결 |
| 같은 user_id에 2 device 동시 연결 | BFF가 둘 다 인정 (sticky session) — 둘 다 알림 받음 |
| 알림 폭주 (대량 메시지) | v1.0은 미처리 — v1.1에 client-side throttle (1/sec) 검토 |
| 모바일 백그라운드 → WebSocket 끊김 | iOS·Android 모두 백그라운드 시 끊김 (정상). 포그라운드 복귀 시 재연결. v1.1에 FCM 푸시로 보완 |

> **김지민 ↔ 강태오 페어 합의 사항 (W1):** STOMP CONNECT 프레임의 헤더 명 (Authorization vs X-Auth) — 표준은 **Authorization: Bearer**.

---

## 10. 화면 구현 가이드 — 5 핵심 화면

### 10.1 화면 매트릭스

| # | 화면 | 경로 | 주 Provider | 주 API |
| --- | --- | --- | --- | --- |
| 1 | LoginPage / RegisterPage | `/login`, `/register` | `authNotifierProvider` | `/auth/login`, `/auth/register`, `/auth/oauth/google` |
| 2 | DashboardPage | `/dashboard` | `dashboardProvider` (BFF) | `/me/dashboard` |
| 3 | PassageViewPage (입체 묵상) | `/dashboard/passage/:bookCode/:chapter/:verse` | `passageProvider(family)` | `/passages/:b/:c/:v` (BFF) |
| 4 | AiSessionPage (AI 큐티 4단계) | `/ai/sessions/:sessionId` | `aiSessionTurnsProvider(sessionId)` | `/ai/sessions/:id`, `/ai/sessions/:id/turns` (SSE), `/ai/sessions/:id/abandon` |
| 5a | JournalListPage | `/journals` | `journalListProvider` + `journalFilterProvider` | `/journals?page=&size=&status=` |
| 5b | JournalDetailPage / JournalEditPage | `/journals/:id`, `/journals/new`, `/journals/:id/edit` | feature 내 단일 Provider | `/journals/:id` GET·PATCH·DELETE, `/journals` POST |

### 10.2 화면 1 — LoginPage·RegisterPage

```dart
// lib/features/auth/presentation/login_page.dart
class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});
  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authNotifierProvider);

    ref.listen<AsyncValue<User?>>(authNotifierProvider, (prev, next) {
      if (next.value != null && prev?.value == null) {
        context.go('/dashboard');
      }
      if (next.hasError) {
        final exception = next.error;
        final message = exception is ApiException
            ? exception.userMessage
            : '로그인에 실패했습니다.';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message)));
      }
    });

    return Scaffold(
      appBar: AppBar(title: const Text('큐티 AI')),
      body: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              TextFormField(
                controller: _emailController,
                decoration: const InputDecoration(labelText: '이메일'),
                keyboardType: TextInputType.emailAddress,
                validator: (v) => (v == null || !v.contains('@')) ? '이메일을 입력해 주세요' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                decoration: const InputDecoration(labelText: '비밀번호'),
                obscureText: true,
                validator: (v) => (v == null || v.length < 8) ? '8자 이상' : null,
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: authState.isLoading ? null : _onLogin,
                child: authState.isLoading
                    ? const CircularProgressIndicator()
                    : const Text('로그인'),
              ),
              TextButton(
                onPressed: () => context.go('/register'),
                child: const Text('회원가입'),
              ),
              const Divider(),
              ElevatedButton.icon(
                icon: const Icon(Icons.login),
                label: const Text('Google 로그인'),
                onPressed: _onGoogleLogin,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _onLogin() async {
    if (!_formKey.currentState!.validate()) return;
    await ref.read(authNotifierProvider.notifier).login(
      email: _emailController.text.trim(),
      password: _passwordController.text,
    );
  }

  Future<void> _onGoogleLogin() async {
    // OAuth 흐름 — § 7.4 참조
  }
}
```

### 10.3 화면 2 — DashboardPage (4-service 어그리게이션)

```dart
// lib/features/dashboard/presentation/dashboard_page.dart
class DashboardPage extends ConsumerWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncDashboard = ref.watch(dashboardProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('홈'),
        actions: const [ConnectionIndicator(), SizedBox(width: 8)],
      ),
      body: asyncDashboard.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => ErrorView(error: e, onRetry: () => ref.invalidate(dashboardProvider)),
        data: (dashboard) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(dashboardProvider),
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // 사용자 인사
              Text('안녕하세요, ${dashboard.user.nickname}님',
                  style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 24),

              // 오늘의 구절 카드 (Bible)
              _PassageCard(verse: dashboard.todayPassage),
              const SizedBox(height: 16),

              // 진행 중 AI 세션 카드 (있으면)
              if (dashboard.aiSession != null)
                _AiSessionCard(session: dashboard.aiSession!),

              // 최근 묵상 노트 요약 (있으면)
              if (dashboard.journalSummary != null)
                _JournalSummaryCard(summary: dashboard.journalSummary!),

              // partial result 알림 (어떤 service가 실패했는지)
              if (dashboard.failures.isNotEmpty)
                _PartialFailureBanner(failures: dashboard.failures),
            ],
          ),
        ),
      ),
    );
  }
}

class _PassageCard extends StatelessWidget {
  final Verse verse;
  const _PassageCard({required this.verse});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: InkWell(
        onTap: () => context.push(
          '/dashboard/passage/${verse.bookCode}/${verse.chapter}/${verse.verse}',
        ),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('오늘의 구절', style: Theme.of(context).textTheme.labelMedium),
              const SizedBox(height: 8),
              Text(
                '${_bookKrName(verse.bookCode)} ${verse.chapter}:${verse.verse}',
                style: Theme.of(context).textTheme.titleMedium,
              ),
              const SizedBox(height: 8),
              Text(verse.text, style: Theme.of(context).textTheme.bodyLarge),
            ],
          ),
        ),
      ),
    );
  }
}
```

**핵심 패턴:**
- `AsyncValue.when(loading/error/data)` 표준 — 모든 비동기 화면이 동일 패턴
- `RefreshIndicator` → `ref.invalidate(provider)` 으로 pull-to-refresh
- partial result(`failures[]`) 명시적 표시 — 어떤 service 장애인지 사용자가 알 수 있게

### 10.4 화면 3 — PassageViewPage (입체적 묵상)

BFF가 Bible Service에 3번 호출해서 (현재 절·같은 장 모든 절·책 메타) 합친 응답. Sliver 스크롤로 본문 + 같은 장 절 목록 표시.

```dart
class PassageViewPage extends ConsumerWidget {
  final String bookCode;
  final int chapter;
  final int verse;

  const PassageViewPage({
    super.key,
    required this.bookCode,
    required this.chapter,
    required this.verse,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncView = ref.watch(passageViewProvider((
      bookCode: bookCode, chapter: chapter, verse: verse,
    )));

    return Scaffold(
      body: asyncView.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => ErrorView(error: e),
        data: (view) => CustomScrollView(
          slivers: [
            SliverAppBar.large(
              title: Text('${view.book.krName} ${chapter}:${verse}'),
              floating: true,
              actions: [
                IconButton(
                  icon: const Icon(Icons.smart_toy),
                  tooltip: 'AI 큐티 시작',
                  onPressed: () => _startAiSession(context, ref),
                ),
              ],
            ),
            // 현재 절 강조 카드
            SliverToBoxAdapter(child: _CurrentVerseCard(verse: view.currentVerse)),
            // 같은 장의 모든 절 (현재 절 자동 스크롤)
            SliverList.builder(
              itemCount: view.chapterVerses.length,
              itemBuilder: (_, i) {
                final v = view.chapterVerses[i];
                final isCurrent = v.verse == verse;
                return _ChapterVerseTile(verse: v, highlighted: isCurrent);
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _startAiSession(BuildContext context, WidgetRef ref) async {
    final session = await ref.read(aiRepositoryProvider).createSession(
      bookCode: bookCode, chapter: chapter, verse: verse,
    );
    if (context.mounted) {
      context.push('/ai/sessions/${session.id}');
    }
  }
}
```

**Sliver 사용 근거:** 같은 장의 절이 100+개일 수 있음. `ListView`보다 `SliverList`가 메모리 효율 + AppBar 동기 스크롤이 자연스러움. 김지민 수업 진도(Sliver)와 정확히 매칭.

### 10.5 화면 4 — AiSessionPage (AI 큐티 4단계)

가장 복잡한 화면. SSE 스트림 + 사용자 입력 + 단계 진행 표시.

```dart
class AiSessionPage extends ConsumerStatefulWidget {
  final int sessionId;
  const AiSessionPage({super.key, required this.sessionId});

  @override
  ConsumerState<AiSessionPage> createState() => _AiSessionPageState();
}

class _AiSessionPageState extends ConsumerState<AiSessionPage> {
  final _inputController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  Widget build(BuildContext context) {
    final asyncSession = ref.watch(aiSessionMetaProvider(widget.sessionId));
    final asyncTurns = ref.watch(aiSessionTurnsProvider(widget.sessionId));

    return Scaffold(
      appBar: AppBar(
        title: asyncSession.maybeWhen(
          data: (s) => Text('${_stepLabel(s.currentStep)} 단계'),
          orElse: () => const Text('AI 큐티'),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.cancel),
            tooltip: '세션 중단',
            onPressed: _onAbandon,
          ),
        ],
      ),
      body: Column(
        children: [
          // 단계 progress
          asyncSession.maybeWhen(
            data: (s) => _StepProgress(currentStep: s.currentStep),
            orElse: () => const SizedBox.shrink(),
          ),
          // 대화 메시지 목록
          Expanded(
            child: asyncTurns.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => ErrorView(error: e),
              data: (state) => ListView.builder(
                controller: _scrollController,
                padding: const EdgeInsets.all(16),
                itemCount: state.turns.length + (state.streamingText.isNotEmpty ? 1 : 0),
                itemBuilder: (_, i) {
                  if (i < state.turns.length) {
                    return _TurnBubble(turn: state.turns[i]);
                  } else {
                    // 스트리밍 중인 턴 (typing indicator)
                    return _StreamingBubble(text: state.streamingText);
                  }
                },
              ),
            ),
          ),
          // 입력 영역
          _InputArea(
            controller: _inputController,
            enabled: !asyncTurns.maybeWhen(loading: () => true, orElse: () => false),
            onSend: _onSend,
          ),
        ],
      ),
    );
  }

  Future<void> _onSend() async {
    final text = _inputController.text.trim();
    if (text.isEmpty) return;
    final session = await ref.read(aiSessionMetaProvider(widget.sessionId).future);
    _inputController.clear();
    await ref.read(aiSessionTurnsProvider(widget.sessionId).notifier).sendMessage(
      step: session.currentStep,
      content: text,
    );
    // 새 메시지로 스크롤
    _scrollController.animateTo(
      _scrollController.position.maxScrollExtent,
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOut,
    );
  }

  Future<void> _onAbandon() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('세션을 중단하시겠습니까?'),
        content: const Text('진행 중인 단계가 사라집니다.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context, false), child: const Text('취소')),
          TextButton(onPressed: () => Navigator.pop(context, true), child: const Text('중단')),
        ],
      ),
    );
    if (confirmed != true) return;
    await ref.read(aiRepositoryProvider).abandon(widget.sessionId);
    if (mounted) context.pop();
  }
}
```

**핵심 패턴:**
- `_StreamingBubble` — `streamingText` Provider를 watch해서 실시간 token 표시
- `_StepProgress` — A→B→C→D 단계 시각화
- `RagSource` 출력 — `_TurnBubble`이 ragSources 있으면 "출처: 주석 #1, 논문 #5" 표시
- 세션 중단 시 confirm dialog (실수로 중단 방지)

### 10.6 화면 5a·5b — Journal 목록·상세·편집

```dart
// lib/features/journal/presentation/journal_list_page.dart
class JournalListPage extends ConsumerWidget {
  const JournalListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final asyncList = ref.watch(journalListProvider);
    final filter = ref.watch(journalFilterProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('묵상 노트'),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.filter_list),
            onSelected: (s) => ref.read(journalFilterProvider.notifier).setStatus(s),
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'ALL', child: Text('전체')),
              PopupMenuItem(value: 'DRAFT', child: Text('초안')),
              PopupMenuItem(value: 'PUBLISHED', child: Text('발행')),
            ],
          ),
        ],
      ),
      body: asyncList.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => ErrorView(error: e),
        data: (page) => RefreshIndicator(
          onRefresh: () async => ref.invalidate(journalListProvider),
          child: ListView.separated(
            itemCount: page.items.length,
            separatorBuilder: (_, __) => const Divider(),
            itemBuilder: (_, i) {
              final j = page.items[i];
              return ListTile(
                title: Text(j.title),
                subtitle: Text('${j.status} · ${_formatDate(j.updatedAt)}'),
                onTap: () => context.push('/journals/${j.id}'),
              );
            },
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/journals/new'),
        child: const Icon(Icons.add),
      ),
    );
  }
}
```

JournalEditPage — `JournalEditPage.create()` 와 `JournalEditPage.edit(journalId: id)` 두 명명자 생성자로 분기. 같은 코드 재사용 + 의도 명확.

```dart
class JournalEditPage extends ConsumerStatefulWidget {
  final int? journalId;  // null이면 새 작성, 있으면 편집

  const JournalEditPage.create() : journalId = null, super(key: null);
  const JournalEditPage.edit({super.key, required this.journalId});

  @override
  ConsumerState<JournalEditPage> createState() => _JournalEditPageState();
}
```

PATCH 시 status 전이 검증: DRAFT → PUBLISHED만 허용 (04번 § 7.4 v1.2 정정 정합). UI에서 PUBLISHED 상태 노트는 status 토글 disabled.

---

## 11. UI 디자인 시스템·테마·국제화

### 11.0 디자인 원칙 5개 (위반 시 결과 명시)

디자인 토큰·폰트·간격을 결정하기 전에 5개 원칙에 동의. 이 원칙을 위반하는 구현은 PR 거절.

| 원칙 | 의미 | 위반 시 결과 |
| --- | --- | --- |
| **읽기 가독성 우선** | 본 앱은 묵상 도구 — 폰트·줄간격·여백이 시각적 피로 직접 영향 | 사용자 이탈 |
| **상태 변화 즉시 반영** | API 응답 → UI 업데이트는 200ms 이내 (Riverpod `AsyncValue`) | "버튼 눌렀는데 반응 없는 앱" |
| **에러는 친절하게** | RFC 9457 `code` → 한국어 사용자 메시지 매핑 (`detail` 직접 노출 X) | 기술 용어 노출 |
| **재시도는 명시적** | 네트워크 에러 시 자동 retry는 idempotent endpoint(GET·PUT·DELETE)만. POST는 사용자 버튼 | 중복 결제·중복 노트 생성 |
| **로딩 상태 명시** | API 호출 시 skeleton 또는 progress indicator 필수. 빈 화면 X | "앱이 멈춘 줄 앜" |

본 원칙은 § 4.4 (`AsyncValue.when(loading/error/data)` 표준) + § 11.4 (`ErrorView`·`LoadingIndicator`·`EmptyState` 공통 위젯) + § 12 (자동 vs 수동 재시도)에서 설계 수준으로 구현됨.

### 11.1 디자인 토큰 — Material 3 기반

```dart
// lib/core/ui/theme.dart
import 'package:flutter/material.dart';

class AppTheme {
  AppTheme._();

  // 색상 토큰 — 큐티 앱 정체성 (차분한 블루·앰버 강조)
  static const _seedColor = Color(0xFF2A4D69);  // 깊은 블루

  static ThemeData light() {
    return ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: _seedColor,
        brightness: Brightness.light,
      ),
      textTheme: _textTheme(Brightness.light),
      useMaterial3: true,
      appBarTheme: const AppBarTheme(centerTitle: false, elevation: 0),
      cardTheme: CardTheme(
        elevation: 1,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
      ),
    );
  }

  static ThemeData dark() {
    return ThemeData(
      colorScheme: ColorScheme.fromSeed(
        seedColor: _seedColor,
        brightness: Brightness.dark,
      ),
      textTheme: _textTheme(Brightness.dark),
      useMaterial3: true,
    );
  }

  static TextTheme _textTheme(Brightness b) {
    final base = b == Brightness.light ? Typography.blackMountainView : Typography.whiteMountainView;
    return base.copyWith(
      // 본문 (성경 구절·묵상 본문) — 가독성 최우선
      bodyLarge: base.bodyLarge?.copyWith(fontSize: 17, height: 1.6),
      bodyMedium: base.bodyMedium?.copyWith(fontSize: 15, height: 1.5),
      // 제목
      headlineSmall: base.headlineSmall?.copyWith(fontWeight: FontWeight.w600),
      titleMedium: base.titleMedium?.copyWith(fontWeight: FontWeight.w500),
    );
  }
}
```

### 11.2 폰트 — 한글 가독성 최우선

| 용도 | 폰트 | 근거 |
| --- | --- | --- |
| 본문 (성경·묵상 노트·AI 응답) | **Pretendard** (KR + EN 통합) | 한글 가독성 + 영어 자연스러움. v1.0 우선 |
| 강조 (성경 권/장/절 표시) | Pretendard SemiBold | 본문과 시각 구분 |
| 코드 폰트 (혹시 필요 시) | JetBrains Mono | (현재 사용 X) |

`pubspec.yaml`에 폰트 등록:

```yaml
fonts:
  - family: Pretendard
    fonts:
      - asset: assets/fonts/Pretendard-Regular.otf
        weight: 400
      - asset: assets/fonts/Pretendard-Medium.otf
        weight: 500
      - asset: assets/fonts/Pretendard-SemiBold.otf
        weight: 600
      - asset: assets/fonts/Pretendard-Bold.otf
        weight: 700
```

라이센스: Pretendard OFL (open font license) — 상업·재배포 허용.

### 11.3 간격·radius·shadow 표준

```dart
// lib/core/ui/spacing.dart
class Spacing {
  Spacing._();
  static const xs = 4.0;
  static const s = 8.0;
  static const m = 16.0;
  static const l = 24.0;
  static const xl = 32.0;
  static const xxl = 48.0;
}

class Radii {
  Radii._();
  static const s = 4.0;
  static const m = 8.0;
  static const l = 12.0;
  static const xl = 16.0;
  static const pill = 999.0;
}
```

원칙:
- `Padding(padding: EdgeInsets.all(16))` 같은 매직 넘버 X — `Spacing.m` 사용
- 모든 카드는 `Radii.l` (12px)
- shadow는 elevation 1 또는 0 (Material 3는 shadow 최소화 권장)

### 11.4 공통 위젯

```dart
// lib/core/ui/widgets/error_view.dart
class ErrorView extends StatelessWidget {
  final Object error;
  final VoidCallback? onRetry;

  const ErrorView({super.key, required this.error, this.onRetry});

  @override
  Widget build(BuildContext context) {
    final message = error is ApiException
        ? (error as ApiException).userMessage
        : '알 수 없는 오류가 발생했습니다.';
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(Spacing.l),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 48),
            const SizedBox(height: Spacing.m),
            Text(message, textAlign: TextAlign.center),
            if (onRetry != null) ...[
              const SizedBox(height: Spacing.l),
              FilledButton(onPressed: onRetry, child: const Text('다시 시도')),
            ],
          ],
        ),
      ),
    );
  }
}
```

기타 공통 위젯:
- `LoadingIndicator` — 통일된 CircularProgressIndicator wrapper
- `EmptyState({icon, title, message, action})` — 빈 목록 상태
- `SectionHeader({title, action?})` — 화면 안 섹션 구분
- `OutlinedTag({label, color})` — 태그·뱃지 (status 표시 등)
- `_ConnectionIndicator` (§ 9.4)

### 11.5 국제화 (i18n) — KR 우선 + EN v1.1

`flutter_localizations` + `intl` + ARB 파일.

```
lib/core/l10n/
├── app_ko.arb     # 기본 (한국어)
└── app_en.arb     # v1.1
```

ARB 예:
```json
{
  "appTitle": "큐티 AI",
  "auth_login": "로그인",
  "auth_register": "회원가입",
  "auth_email": "이메일",
  "auth_password": "비밀번호",
  "ai_session_title": "AI 큐티",
  "ai_step_a": "관찰 (Observation)",
  "ai_step_b": "해석 (Interpretation)",
  "ai_step_c": "적용 (Application)",
  "ai_step_d": "결단 (Decision)",
  "journal_list_title": "묵상 노트",
  "journal_status_draft": "초안",
  "journal_status_published": "발행"
}
```

`pubspec.yaml`:
```yaml
flutter:
  generate: true
```

`l10n.yaml`:
```yaml
arb-dir: lib/core/l10n
template-arb-file: app_ko.arb
output-localization-file: app_localizations.dart
```

화면에서 사용:
```dart
final l10n = AppLocalizations.of(context)!;
Text(l10n.auth_login);  // "로그인"
```

### 11.6 다크 모드

`MaterialApp.router`에서 `themeMode: ThemeMode.system` — 시스템 설정 따라가기.

밤 묵상 시 OLED 디스플레이의 눈 부담을 줄이려면 다크 모드가 자연스러움. 모든 위젯이 `ColorScheme`을 통해 색상 사용 → 자동 적응.

---

## 12. 에러 처리 — ProblemDetail·재시도·offline

### 12.1 에러 분류 + 표준 처리

| 에러 종류 | 분류 기준 | 처리 |
| --- | --- | --- |
| 네트워크 단절 | `DioException` type=connectionError | "인터넷 연결을 확인해 주세요" + 재시도 버튼 |
| 서버 5xx | status >= 500 | "잠시 후 다시 시도해 주세요" + 자동 재시도 X (사용자 선택) |
| Rate Limit (429) | code=RATE_LIMITED | "잠시 후 다시 시도해 주세요" + 입력 잠금 5초 |
| 인증 실패 (401·만료) | code=TOKEN_EXPIRED·UNAUTHORIZED | AuthInterceptor가 처리 → 자동 logout 또는 refresh |
| 권한 없음 (403) | code=JOURNAL_NOT_OWNED 등 | "본인 자원만 접근 가능합니다" + back |
| 입력 검증 (400) | code=VALIDATION_FAILED | 폼 필드 옆에 inline 에러 표시 |
| 자원 없음 (404) | code=*_NOT_FOUND | "찾을 수 없습니다" + back |
| 충돌 (409) | code=*_RACE_CONFLICT 등 | "다른 곳에서 동시 수정 중입니다" + 자동 재로딩 |
| AI 응답 오류 | code=LLM_UNAVAILABLE·LLM_TIMEOUT·PROMPT_INJECTION_DETECTED | SnackBar + 입력 내용 보존 |

### 12.2 ApiException 매핑 (§ 6.5와 통합)

`AuthInterceptor`의 `onError`가 4xx·5xx 응답을 `ApiException`으로 변환 + ProblemDetail 파싱:

```dart
// lib/core/network/auth_interceptor.dart 추가
Future<ApiException> _toApiException(Response response) async {
  try {
    final json = response.data is String
        ? jsonDecode(response.data) as Map<String, dynamic>
        : response.data as Map<String, dynamic>;
    return ApiException(ProblemDetail.fromJson(json));
  } catch (_) {
    return ApiException(ProblemDetail(
      type: 'about:blank',
      title: '알 수 없는 오류',
      status: response.statusCode ?? 500,
      code: 'UNKNOWN',
      detail: '응답을 해석할 수 없습니다.',
      instance: '',
    ));
  }
}
```

화면에서는 `ApiException.userMessage`만 보여주고 `code`·`traceId`는 Sentry로 전송 (§ 15.3).

### 12.3 재시도 전략 — 자동 vs 수동

| 상황 | 자동 재시도 | 수동 재시도 |
| --- | --- | --- |
| 401 + Refresh Token 유효 | ✅ AuthInterceptor (1회) | — |
| 503 (Service Unavailable) | ❌ (사용자 의도 모름) | ✅ ErrorView의 onRetry 버튼 |
| 504 (Timeout) | ❌ | ✅ |
| 429 (Rate Limit) | ❌ (서버 부하 가중) | ✅ 5초 대기 후 |
| 네트워크 connectionError | ❌ | ✅ |
| 5xx (일반) | ❌ | ✅ |

**원칙:** 자동 재시도는 **idempotent + 사용자 의도 명확**할 때만. POST·PATCH·DELETE는 자동 재시도 X (서버에서 멱등 처리되어도 클라이언트가 두 번 동의한 것 아님).

### 12.4 offline 처리 — v1.0과 v1.1

**v1.0:**
- 네트워크 단절 감지 → 모든 요청에 Snackbar "인터넷 연결을 확인해 주세요"
- 마지막 성공한 Dashboard 데이터를 메모리에 1회 보존 (앱 재시작 시 사라짐) — Riverpod의 `KeepAlive` 옵션 활용
- 진정한 offline 모드 (큐 + 동기화) 없음

**v1.1 (Drift 도입):**
- Journal 작성·편집을 로컬 DB에 우선 저장 → 온라인 복귀 시 동기화
- AI 세션은 서버 의존 도메인이라 offline 지원 X

`connectivity_plus` 패키지로 네트워크 상태 감지 가능 (v1.1).

### 12.5 Sentry 통합 — 클라이언트 에러 보고

```dart
// lib/main.dart
import 'package:sentry_flutter/sentry_flutter.dart';

Future<void> main() async {
  await SentryFlutter.init(
    (options) {
      options.dsn = const String.fromEnvironment('SENTRY_DSN');
      options.tracesSampleRate = 0.2;  // 20% 샘플링 (v1.0 시연 트래픽)
      options.environment = Env.flavor;  // dev / staging / prod
      options.beforeSend = (event, hint) {
        // 토큰·이메일 등 PII 마스킹
        if (event.request?.headers != null) {
          event.request!.headers!.removeWhere((k, _) => k.toLowerCase() == 'authorization');
        }
        return event;
      };
    },
    appRunner: () => runApp(
      const ProviderScope(child: MyApp()),
    ),
  );
}
```

ApiException을 Sentry에 보고할 때 `traceId`를 fingerprint에 추가 — 백엔드 Tempo trace와 매칭.

---

## 13. Flutter 테스트 (Widget·Integration·Golden)

### 13.1 테스트 피라미드 — 07번 § 9와 정합

| 계층 | 비율 | 도구 | 범위 |
| --- | --- | --- | --- |
| Unit | 60% | `flutter_test` + `mockito` | Repository·Provider·매퍼·유틸 |
| Widget | 30% | `flutter_test` (`testWidgets`) | 단일 ConsumerWidget의 상태별 렌더 |
| Integration | 10% | `integration_test` | 5 화면 E2E (실제 API 또는 mock 서버) |
| Golden | (cross-cut) | `golden_toolkit` | 디자인 시스템 회귀 |

### 13.2 dev_dependencies

```yaml
dev_dependencies:
  flutter_test:
    sdk: flutter
  integration_test:
    sdk: flutter
  mockito: ^5.4.4
  build_runner: ^2.4.0
  riverpod_generator: ^2.4.0
  retrofit_generator: ^9.0.0
  json_serializable: ^6.7.0
  freezed: ^2.5.0
  golden_toolkit: ^0.15.0
  patrol: ^3.0.0  # (선택, integration_test 강화)
```

### 13.3 Unit 테스트 — Repository·Provider

```dart
// test/features/auth/data/auth_repository_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([AuthApi, SecureStorage])
import 'auth_repository_test.mocks.dart';

void main() {
  late AuthRepository repo;
  late MockAuthApi api;
  late MockSecureStorage storage;

  setUp(() {
    api = MockAuthApi();
    storage = MockSecureStorage();
    repo = AuthRepository(api: api, storage: storage);
  });

  group('login', () {
    test('성공 시 token 저장 + User 반환', () async {
      when(api.login(any)).thenAnswer((_) async => TokenPair(
        accessToken: 'AT', refreshToken: 'RT', expiresIn: 900, refreshExpiresIn: 1209600,
      ));
      when(api.me()).thenAnswer((_) async => User(
        id: 1, email: 'a@b.com', nickname: 'tester', role: 'ROLE_USER',
        emailVerified: true, createdAt: DateTime(2026, 5, 7),
      ));
      when(storage.writeTokens(access: anyNamed('access'), refresh: anyNamed('refresh')))
          .thenAnswer((_) async {});

      final user = await repo.login(email: 'a@b.com', password: 'pw12345678');

      expect(user.email, 'a@b.com');
      verify(storage.writeTokens(access: 'AT', refresh: 'RT')).called(1);
    });

    test('401 응답 시 ApiException(INVALID_CREDENTIALS) throw', () async {
      when(api.login(any)).thenThrow(ApiException(ProblemDetail(
        type: '', title: '', status: 401, code: 'INVALID_CREDENTIALS',
        instance: '',
      )));

      expect(
        () => repo.login(email: 'a@b.com', password: 'wrong'),
        throwsA(isA<ApiException>().having((e) => e.problem.code, 'code', 'INVALID_CREDENTIALS')),
      );
      verifyNever(storage.writeTokens(access: anyNamed('access'), refresh: anyNamed('refresh')));
    });
  });
}
```

Provider 테스트는 `ProviderContainer` 사용:

```dart
// test/features/auth/presentation/auth_provider_test.dart
test('login 성공 시 state가 User 로 변경', () async {
  final container = ProviderContainer(overrides: [
    authRepositoryProvider.overrideWithValue(MockAuthRepository()),
  ]);
  addTearDown(container.dispose);

  await container.read(authNotifierProvider.notifier).login(
    email: 'a@b.com', password: 'pw12345678',
  );
  final state = container.read(authNotifierProvider);
  expect(state.value, isNotNull);
  expect(state.value?.email, 'a@b.com');
});
```

### 13.4 Widget 테스트 — 화면 상태별 렌더

```dart
// test/features/auth/presentation/login_page_test.dart
void main() {
  testWidgets('로그인 버튼 비활성화 — loading 중', (tester) async {
    await tester.pumpWidget(
      ProviderScope(
        overrides: [
          authNotifierProvider.overrideWith(() => _LoadingAuthNotifier()),
        ],
        child: const MaterialApp(home: LoginPage()),
      ),
    );

    final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
    expect(button.onPressed, isNull);  // loading 중 비활성화
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
  });

  testWidgets('잘못된 이메일 입력 시 inline 에러 표시', (tester) async {
    await tester.pumpWidget(
      ProviderScope(child: const MaterialApp(home: LoginPage())),
    );

    await tester.enterText(find.byType(TextFormField).first, 'invalid');
    await tester.tap(find.text('로그인'));
    await tester.pump();

    expect(find.text('이메일을 입력해 주세요'), findsOneWidget);
  });
}
```

### 13.5 Integration 테스트 — E2E 핵심 시나리오

`integration_test/` 폴더에 두고 실제 디바이스 또는 emulator에서 실행. v1.0 시연용 핵심 시나리오 5개 (07번 § 9.4와 매칭):

| # | 시나리오 | 검증 포인트 |
| --- | --- | --- |
| 1 | 로그인 → Dashboard 진입 | 토큰 저장·BFF /me/dashboard 호출·partial result 표시 |
| 2 | 입체 묵상 화면 진입·스크롤 | 같은 장 절 표시·현재 절 자동 스크롤 |
| 3 | AI 큐티 4단계 (A→B→C→D) | SSE 토큰 스트림·turn_completed·세션 완료 |
| 4 | AI 세션 완료 → STOMP 알림 → Journal 자동 생성 화면 진입 | WebSocket 연결·알림 수신·deeplink |
| 5 | 묵상 노트 CRUD | 작성·편집·발행 (DRAFT→PUBLISHED) 전이 검증 |

```dart
// integration_test/login_to_dashboard_test.dart
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('로그인 → Dashboard 진입', (tester) async {
    app.main();  // lib/main.dart
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(const Key('login_email')), 'tester@example.com');
    await tester.enterText(find.byKey(const Key('login_password')), 'pw12345678');
    await tester.tap(find.text('로그인'));
    await tester.pumpAndSettle(const Duration(seconds: 5));

    expect(find.text('홈'), findsOneWidget);
    expect(find.text('오늘의 구절'), findsOneWidget);
  });
}
```

> **백엔드 의존:** Integration 테스트는 실제 BFF + 4 service가 필요. CI에서는 docker-compose로 `auth-service` + `bible-service` + `bff-aggregator` + `mysql` + `redis` + WireMock(Anthropic) 띄우고 실행 (06번 § 3.3과 정합).

### 13.6 Golden 테스트 — 디자인 시스템 회귀

```dart
// test/golden/login_page_golden_test.dart
import 'package:golden_toolkit/golden_toolkit.dart';

void main() {
  testGoldens('LoginPage — light·dark·tablet', (tester) async {
    final builder = DeviceBuilder()
      ..addScenario(widget: const LoginPage(), name: 'phone_light')
      ..addScenario(widget: const LoginPage(), name: 'phone_dark', textScaleSize: 1.0);

    await tester.pumpDeviceBuilder(builder);
    await screenMatchesGolden(tester, 'login_page_devices');
  });
}
```

골든 이미지 갱신: `flutter test --update-goldens`. PR에서 골든 변경 발생 시 1명 이상 디자인 리뷰.

### 13.7 커버리지 게이트

| Service | unit + widget 커버리지 목표 |
| --- | --- |
| flutter-app/ | 60%+ |

`flutter test --coverage` → `coverage/lcov.info` → CI에서 게이트.

### 13.8 페어 합의 사항

- **김지민 ↔ 강태오:** ArchUnit 같은 의존 방향 검증을 Flutter에서는 `dart analyze` + 수동 PR 리뷰로 대체. v1.1에 `dart_code_metrics` 도입 검토 (07번 § 11과 일관)
- **김지민 ↔ 4 service owner:** integration 테스트의 mock 서버 fixture 합의 — 각 service가 `tests/contract/fixtures/` 디렉토리에 표준 응답 JSON 박제 (04번 OpenAPI 예시 활용)

---

## 14. 빌드·배포·CI/CD

### 14.1 Flavor — dev / staging / prod

`flutter_flavorizr` 또는 수동으로 3 flavor 분리. 각 flavor의 `Env`:

| Flavor | API_BASE_URL | SENTRY_DSN | Application ID (Android) | Bundle Id (iOS) |
| --- | --- | --- | --- | --- |
| **dev** | `http://10.0.2.2:8080/api/v1` (Android emulator) / `http://localhost:8080/api/v1` (iOS simulator) | (Sentry dev DSN) | `com.qtai.app.dev` | `com.qtai.app.dev` |
| **staging** | `https://staging.qtai.example.com/api/v1` | (Sentry staging DSN) | `com.qtai.app.staging` | `com.qtai.app.staging` |
| **prod** | `https://api.qtai.example.com/api/v1` | (Sentry prod DSN) | `com.qtai.app` | `com.qtai.app` |

`lib/core/config/env.dart`:

```dart
enum Flavor { dev, staging, prod }

class Env {
  static late Flavor flavor;
  static late String apiBaseUrl;
  static late String wsBaseUrl;
  static late String sentryDsn;

  static Future<void> initialize(Flavor f) async {
    flavor = f;
    switch (f) {
      case Flavor.dev:
        apiBaseUrl = 'http://10.0.2.2:8080/api/v1';
        wsBaseUrl = 'ws://10.0.2.2:8080/api/v1/ws/notifications';
        sentryDsn = const String.fromEnvironment('SENTRY_DSN_DEV', defaultValue: '');
        break;
      case Flavor.staging:
        apiBaseUrl = 'https://staging.qtai.example.com/api/v1';
        wsBaseUrl = 'wss://staging.qtai.example.com/api/v1/ws/notifications';
        sentryDsn = const String.fromEnvironment('SENTRY_DSN_STAGING', defaultValue: '');
        break;
      case Flavor.prod:
        apiBaseUrl = 'https://api.qtai.example.com/api/v1';
        wsBaseUrl = 'wss://api.qtai.example.com/api/v1/ws/notifications';
        sentryDsn = const String.fromEnvironment('SENTRY_DSN_PROD', defaultValue: '');
        break;
    }
  }
}
```

### 14.2 빌드 명령

| 목적 | 명령 |
| --- | --- |
| dev 디버그 (Android) | `flutter run --flavor dev -t lib/main_dev.dart` |
| staging 릴리즈 (Android) | `flutter build apk --flavor staging -t lib/main_staging.dart --release --dart-define=SENTRY_DSN_STAGING=...` |
| prod 릴리즈 (Android) | `flutter build appbundle --flavor prod -t lib/main_prod.dart --release --dart-define=SENTRY_DSN_PROD=...` |
| dev 디버그 (iOS) | `flutter run --flavor dev -t lib/main_dev.dart` |
| prod 릴리즈 (iOS) | `flutter build ipa --flavor prod -t lib/main_prod.dart --release --dart-define=SENTRY_DSN_PROD=...` |

### 14.3 Android signing — 시연 환경

v1.0 시연은 release 빌드 + debug 서명 키 (Google Play 미배포). v1.1에 production keystore 도입.

`android/app/build.gradle`:

```gradle
android {
    signingConfigs {
        release {
            // v1.0: 디버그 키 (시연 전용)
            storeFile file('debug.keystore')
            storePassword 'android'
            keyAlias 'androiddebugkey'
            keyPassword 'android'
            // v1.1: env 변수에서 production keystore 읽기
        }
    }
    buildTypes {
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
}
```

> **W0 Lock-in:** debug.keystore를 GitHub에 commit X (`.gitignore`에 추가). v1.0은 김지민 로컬에서 빌드 후 산출물 APK만 시연.

### 14.4 iOS provisioning — v1.1까지 시연 X

v1.0은 시연 전 김지민 로컬 macOS에서 iOS 시뮬레이터로 시연. 실제 iOS 디바이스는 Apple Developer Program 가입 필요 → v1.1에 검토.

> **만약 시연 중 iOS 데모도 필요하다면**: 김지민 또는 다른 팀원이 Apple Developer Program (USD 99/yr) 가입 + Personal Team으로 7일 임시 프로비저닝.

### 14.5 CI/CD — GitHub Actions

`.github/workflows/flutter-ci.yml`:

```yaml
name: flutter-ci
on:
  push:
    branches: [main, develop]
    paths: ['flutter-app/**']
  pull_request:
    paths: ['flutter-app/**']

jobs:
  analyze-test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: flutter-app
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.24.x'
          channel: stable
          cache: true
      - run: flutter pub get
      - run: dart run build_runner build --delete-conflicting-outputs
      - run: flutter analyze
      - run: flutter test --coverage
      - uses: codecov/codecov-action@v4
        with:
          file: flutter-app/coverage/lcov.info
          flags: flutter

  build-android:
    needs: analyze-test
    runs-on: ubuntu-latest
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    defaults:
      run:
        working-directory: flutter-app
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'temurin', java-version: '17' }
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.24.x', channel: stable, cache: true }
      - run: flutter pub get
      - run: dart run build_runner build --delete-conflicting-outputs
      - run: flutter build apk --flavor dev -t lib/main_dev.dart --debug
      - uses: actions/upload-artifact@v4
        with:
          name: qtai-dev-apk
          path: flutter-app/build/app/outputs/flutter-apk/app-dev-debug.apk
          retention-days: 14
```

CI 5 jobs (06번 § 3.3과 일관):
1. `analyze-test` (dart analyze + flutter test) — 항상
2. `build-android` (debug APK) — main push 시
3. `integration-test` (선택) — main push 시 + emulator
4. `golden-test` (Linux runner) — PR 시 (디자인 회귀 검증)
5. `release-build` (v1.1) — tag push 시 release AAB

### 14.6 v1.0 시연 시나리오

| 시나리오 | 환경 |
| --- | --- |
| Android 시연 | 김지민 노트북 → Android emulator (Pixel 6, API 34) → debug APK 실행 |
| iOS 시연 (선택) | 김지민 macOS → iOS 시뮬레이터 (iPhone 15 Pro) → debug 실행 |
| 백엔드 | Minikube 클러스터 (강태오 노트북) — `qtai.local` 도메인 hosts 매핑 |
| 데모 데이터 | 사전 시드된 Bible 본문 + 1 user account |

---

## 15. 성능·접근성·관측성

### 15.1 렌더링 성능

| 영역 | 목표 | 가드레일 |
| --- | --- | --- |
| 첫 화면 진입 (cold start) | < 2초 | `splash_screen` 패키지 + Riverpod `keepAlive`로 자주 쓰는 Provider 사전 초기화 |
| 화면 전환 | 60fps 유지 | `Hero` 애니메이션 신중히 사용 (큰 위젯 X), `Navigator.push` 시 heavy build 제거 |
| 스크롤 (Sliver·ListView) | 60fps | `SliverList.builder`·`ListView.builder` 사용 (전체 build X), 1000+ item일 때 `SliverFixedExtentList` 검토 |
| AI SSE 스트리밍 | 토큰 도착 → 화면 표시 < 50ms | Provider state 갱신 시 `select`로 부분 watch (전체 위젯 트리 rebuild 차단) |
| WebSocket 알림 | 도착 → AppBar indicator 변경 < 100ms | StreamProvider + 단일 `StreamBuilder` |

**Impeller renderer (Flutter 3.20+):**
- Android stable에서 default → Skia보다 빠른 GPU 활용
- iOS는 default → 안정적
- iOS·Android 모두 차이 없게 동작 검증 (W3·W4)

### 15.2 메모리

| 영역 | 가드레일 |
| --- | --- |
| 이미지 캐시 | `cached_network_image` 사용 (대량 이미지 시) — v1.0은 사용 X (Bible 텍스트만), v1.1 검토 |
| Provider | `keepAlive` 신중히 사용 — 큰 데이터(`List<Verse>` 1000+) 들고 있는 Provider는 화면 떠나면 dispose 권장 |
| WebSocket | `notificationsStreamProvider`만 `keepAlive` (사용자 세션 동안 유지) |

### 15.3 관측성 — Sentry + Trace ID 매칭

- **Sentry breadcrumbs**: 각 Page 진입 시 `Sentry.addBreadcrumb(Breadcrumb(category: 'navigation', message: 'PassageViewPage entered'))` 자동 추가 (커스텀 NavigatorObserver)
- **Trace ID 전파**: 백엔드가 응답 헤더에 `X-Trace-Id` 또는 ProblemDetail의 `traceId`로 보냄 → ApiException 발생 시 fingerprint에 추가 → Tempo trace와 매칭
- **사용자 식별**: 로그인 후 `Sentry.configureScope((scope) => scope.setUser(SentryUser(id: userId.toString())))` — 로그아웃 시 clear

```dart
// lib/core/observability/navigator_observer.dart
class SentryNavigatorObserver extends NavigatorObserver {
  @override
  void didPush(Route route, Route? previousRoute) {
    Sentry.addBreadcrumb(Breadcrumb(
      category: 'navigation',
      message: 'route push: ${route.settings.name}',
      level: SentryLevel.info,
      type: 'navigation',
    ));
  }
}
```

### 15.4 접근성 (a11y)

**한국어 모바일 시장의 a11y 요구는 EU·US보다 약하지만, 시연 평가에서 가산점.**

| 영역 | 표준 |
| --- | --- |
| Semantics | 모든 `IconButton`·`InkWell`에 `tooltip` 또는 `Semantics(label: ...)` 부착 |
| 색 대비 | Material 3 기본 toolkit이 WCAG AA 충족 — 커스텀 색 도입 시 `colorScheme.onPrimary` 등 사용 |
| 텍스트 크기 | `MediaQuery.textScaleFactor` 존중 — 고정 fontSize 지양 |
| 키보드 네비게이션 | TextField 사이 `tab` 이동 (Android·iOS 모두 자동 지원) |
| VoiceOver / TalkBack | `Semantics` 위젯 + `excludeSemantics` 적절히 사용 |

```dart
// 안티 패턴
IconButton(icon: Icon(Icons.add), onPressed: _add);  // 스크린 리더 "버튼" 만 읽음

// 표준
IconButton(
  icon: const Icon(Icons.add),
  tooltip: '새 묵상 노트 작성',  // a11y label + visual tooltip
  onPressed: _add,
);

// 또는 명시적 Semantics
Semantics(
  label: '새 묵상 노트 작성',
  button: true,
  child: IconButton(...),
);
```

### 15.5 사용자 행동 분석 (선택, v1.1)

v1.0은 Sentry 만 사용. v1.1에 다음 검토:
- **Firebase Analytics** — 화면 진입·버튼 클릭 이벤트
- **PostHog** — 자체 호스팅 가능 + funnel 분석

v1.0 시연에서는 사용자 행동 분석 X — 데모 사용자 1명만.

### 15.6 라이프사이클 — 앱 백그라운드·포그라운드

```dart
class AppLifecycleObserver extends ConsumerWidget with WidgetsBindingObserver {
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    final stomp = ref.read(stompClientProvider);
    switch (state) {
      case AppLifecycleState.resumed:
        // 포그라운드 복귀 → STOMP 재연결
        if (!stomp.isConnected) stomp.connect();
        // 진행 중 SSE 세션이 있으면 새 토큰 발급 후 이어서 (v1.0은 미지원, v1.1)
        break;
      case AppLifecycleState.paused:
        // 백그라운드 → STOMP는 자동 끊김 (정상)
        break;
      default:
        break;
    }
  }
}
```

iOS·Android 모두 백그라운드에서 WebSocket 끊김. 포그라운드 복귀 시 `connectionIndicator`가 잠시 amber → green 전환 (사용자에게 보임). v1.1 push notification(FCM) 도입 시 백그라운드 알림도 가능.

---

## 16. 1차(HMS) SSR 패턴 ↔ Flutter 가드레일 + W1 Lock-in 체크리스트

### 16.1 1차 사고 패턴 ↔ 2차 가드레일 매트릭스 (확장)

| # | 1차(HMS) 사고 패턴 | 본질적 원인 | Flutter 가드레일 (어디 박제됐는지) |
| --- | --- | --- | --- |
| 1 | Mustache + jQuery — 화면 상태가 DOM에 분산되어 디버그 어려움 | 단방향 데이터 흐름 X | Riverpod 2.x 표준 5종 Provider — § 4 |
| 2 | 토큰을 cookie + localStorage 혼재 저장 — XSS 시 노출 | 보관 표준 X | flutter_secure_storage 강제 + StorageKeys 명명 표준 — § 7.2, § 7.3 |
| 3 | Refresh 갱신 race condition — 동시 요청 N개 충돌 | 클라이언트 race 차단 X | QueuedInterceptor + synchronized Lock — § 6.4 |
| 4 | API 변경 시 클라이언트 깨짐을 머지 후에야 인지 | 계약 검증 X | Retrofit 인터페이스 + freezed DTO + 백엔드 owner 페어 합의 — § 6.2, § 6.3 |
| 5 | 에러 메시지 SQL exception 노출 | 에러 매핑 표준 X | RFC 9457 ProblemDetail의 `code` enum → 사용자 메시지 매핑 (13종) — § 6.5, § 12.2 |
| 6 | WebSocket 끊김 인지 없음 | 연결 상태 UI X | StompConnectionState Provider + ConnectionIndicator AppBar 표시 — § 9.4 |
| 7 | Refresh 실패 후에도 화면이 안 바뀜 — 사용자가 "안 됨" 만 호소 | logout 흐름 정의 X | router redirect가 authNotifier state watch → 자동 /login 이동 — § 5.1, § 7.5 |
| 8 | 에러를 무한 retry 하다가 서버 부하 가중 | 재시도 정책 X | 자동 재시도는 401 + Refresh 1회만, 나머지는 사용자 trigger — § 12.3 |
| 9 | 디자인 토큰 산발 — 화면별 padding 다름 | 표준 토큰 X | Spacing·Radii 토큰 + Material 3 colorScheme — § 11.1, § 11.3 |
| 10 | 고정 fontSize → 텍스트 작게·크게 안 됨 | textScaleFactor 무시 | bodyLarge/Medium에 height 1.6 + textScaleFactor 존중 — § 11.1, § 15.4 |
| 11 | 토큰을 SnackBar에 그대로 표시한 적 있음 | PII 마스킹 X | Sentry beforeSend에서 Authorization 헤더 strip + 사용자에게는 userMessage만 — § 12.5 |
| 12 | Bible Service 응답이 1000+ verse일 때 화면 buffering | ListView 사용 | Sliver* + builder 패턴 강제 — § 10.4, § 15.1 |
| 13 | 로그인 후 dashboard 진입 시 4 service 모두 await 직렬 → 느림 | 병렬 호출 X | BFF가 어그리게이션 (강태오) + Flutter는 단일 dashboardProvider만 — § 10.3 |
| 14 | AI 응답 끊김 시 사용자가 모름 | 스트림 종료 처리 X | SSE event `error`·`end` 명시 처리 + ApiException 매핑 — § 8.4, § 8.5 |
| 15 | 알림 폭주로 화면 freeze | throttle X | StreamProvider + 단일 StreamBuilder (v1.1에 throttle 검토) — § 9.5 |

### 16.2 W1 Lock-in 체크리스트 (5/22 금까지)

**프로젝트 골격:**
- [ ] `flutter-app/` 프로젝트 골격 생성 — `flutter create flutter-app --org com.qtai`
- [ ] `pubspec.yaml`에 § 2.2 핵심 패키지 모두 등록
- [ ] `pubspec.lock` commit
- [ ] `analysis_options.yaml`에 § 3.3 import 규칙 적용
- [ ] `.fvmrc` 또는 README에 SDK 버전 박제 (3.24.x)
- [ ] `dart run build_runner build` 1회 실행 + 산출물 `*.g.dart`·`*.freezed.dart` 정상

**폴더 구조:**
- [ ] `lib/core/` 5 폴더 (config, di, network, storage, ui)
- [ ] `lib/features/` 6 feature (auth, dashboard, passage, ai_session, journal, notifications)
- [ ] 각 feature 안에 data·domain·presentation 3 layer

**Riverpod·라우팅:**
- [ ] `authNotifierProvider` (AsyncNotifier) — 표준 Provider 1개 박제
- [ ] `appRouter` go_router 설정 + redirect 인증 가드
- [ ] 5 화면 라우팅 골격 (LoginPage, DashboardPage, PassageViewPage, AiSessionPage, JournalListPage) — 빈 Scaffold 라도 OK

**네트워크·인증:**
- [ ] `dioProvider` + AuthInterceptor (JWT 부착·401 시 Refresh·QueuedInterceptor·synchronized Lock) — § 6.4 코드 그대로 박제
- [ ] `SecureStorage` wrapper + `StorageKeys` 명명 표준 — § 7.2, § 7.3
- [ ] `ProblemDetail` freezed + `ApiException` 13종 code 매핑 — § 6.5, § 12.2
- [ ] AuthApi Retrofit 인터페이스 (login·register·refresh·logout·me·oauthGoogle) — § 6.2

**테스트:**
- [ ] `flutter test` 실행 → 0 fail (initial smoke test 1개 라도 통과)
- [ ] 단위 테스트 1개: AuthRepository.login 성공 + 401 시 ApiException — § 13.3
- [ ] Widget 테스트 1개: LoginPage 로딩 중 버튼 비활성화 — § 13.4
- [ ] (선택) golden 1개: LoginPage light/dark — § 13.6

**빌드·CI/CD:**
- [ ] dev flavor 빌드 성공 — `flutter run --flavor dev` (Android emulator)
- [ ] `.github/workflows/flutter-ci.yml` 4 job 골격 (analyze-test, build-android) — § 14.5
- [ ] Sentry DSN dev/staging/prod 3개 발급 + `--dart-define` 표준화 — § 14.1

**페어 합의:**
- [ ] 김지민 ↔ 이지윤: Auth API 계약 (login, refresh, oauth/google) — Retrofit 인터페이스로 박제
- [ ] 김지민 ↔ 강상민: AI SSE 이벤트 4종 (token, turn_completed, error, end) — `AiTurnEvent` sealed class로 박제
- [ ] 김지민 ↔ 강태오: BFF dashboard 응답·STOMP CONNECT 헤더 명·SSE Gateway 우회 — 04번 § 9.6 + § 10.2 정합

### 16.3 W2~W5 진척 마일스톤 (01번 § 8 일정과 정합)

| 주차 | Flutter 산출물 |
| --- | --- |
| **W1 (5/18~22)** | (위 체크리스트 — Foundation Lock-in) |
| **W2 (5/26~29)** | LoginPage·RegisterPage 완성 + DashboardPage 어그리게이션 호출 + JournalListPage 골격 |
| **W3 (6/1~5)** | PassageViewPage Sliver 스크롤 + AiSessionPage SSE 스트리밍 + STOMP 알림 indicator |
| **W4 (6/8~12)** | JournalEditPage CRUD + status 전이 + 다크 모드 + Golden 테스트 5개 + Integration 5 시나리오 |
| **W5 (6/15~17)** | 시연 빌드 (Android emulator + iOS simulator) + Sentry release 등록 + 발표 자료 |

### 16.4 페이스 점검 (01번 § 6.5 D 페이스 매트릭스)

| 점검 시점 | 체크 항목 | 임계 |
| --- | --- | --- |
| W1 금 (5/22) | 위 W1 체크리스트 모두 ✅ | 80%+ → OK / 60~79% → 페어 1회 (강태오) / 60% 미만 → Lead 와 범위 조정 회의 |
| W2 화 (5/26) 11:30 | DashboardPage 호출 동작 | partial result 표시 OK |
| W3 화 (6/2) 11:30 | AI SSE 스트림 동작 | 토큰 표시 + turn_completed 처리 OK |
| W4 화 (6/9) 11:30 | 5 화면 모두 진입 가능 | 각 화면 loading/error/data 3 상태 모두 동작 |

### 16.5 김지민 단독 풀스코프의 위험 회피

**가장 큰 위험:** 김지민이 모바일 풀스코프(5 화면 + SSE + STOMP + JWT + Material 3)를 6주 내 완성. 백엔드 4명은 service 1개씩 — Frontend는 1명이 전체 클라이언트.

**구조적 안전망:**
1. **본 문서가 모든 패턴을 박제** — 새 화면 추가 시 § 10의 5 화면을 템플릿으로 복사
2. **W1 골격 + 표준 Provider/Interceptor를 강태오와 페어** — Lead의 검수 필수
3. **W2 화 11:30 + W3 화 11:30 + W4 화 11:30 페이스 점검** — 50% 기준 미달 시 Lead가 즉시 페어
4. **5 화면 중 1개를 잘라낼 수 있는 우선순위** (시연 위해): 필수(Login·Dashboard·AiSession·JournalList) > 선택(PassageView·JournalEdit). PassageView가 가장 어려움 → W4 시점에 미달이면 PassageView 단순화 (Bible Service 단일 호출 → Sliver 없이 단순 ListView)
5. **OAuth Google·다크 모드·Golden 테스트는 v1.1 가능 항목** — W4까지 미달 시 v1.0에서 제거하고 README에 박제

---

> **본 문서는 v1.0 기준이며 W2부터 발생하는 패턴 변경은 ADR 작성 후 본 문서에 반영.** ADR Reviewer 1명 이상 (이승욱·강상민 우선).
