# QT-AI -- Flutter (김지민) 앱 상세 일정표 v2.0

> 이 문서 목적: Flutter 앱을 처음부터 완성하는 단계별 가이드.
> 백엔드 API 가 없어도 Mock 데이터로 화면을 먼저 만든다.

문서 버전: v2.0 | 작성일: 2026-05-08 | 담당자: 김지민
연관 문서: 04_API_명세서 v1.2 / 08_프론트엔드_Flutter_가이드 v1.0

---

## 0. Flutter 앱이 하는 일

QT-AI 앱은 성경 큐티를 돕는 모바일 앱이다.

**5개 주요 화면**
```
1. 로그인/회원가입     -- Auth Service 연결
2. 홈/대시보드         -- BFF Service 연결
3. 성경 구절 화면      -- Bible Service 연결 (Sliver Sync Scroll 핵심)
4. AI 대화 화면        -- AI Service 연결 (SSE 스트리밍 핵심)
5. 묵상 노트 화면      -- Journal Service 연결
```

**시연에서 강조할 2가지 핵심 기술**

(1) Sliver Sync Scroll: 한국어/영어 성경이 함께 스크롤
(2) SSE 스트리밍: AI 응답이 타이핑되듯 실시간으로 표시

---

## 1. 환경 세팅 (5/12 아침)

### Flutter 버전 확인

```bash
flutter --version
# Flutter 3.24.5  나와야 함
# 아니라면:
dart pub global activate fvm
fvm install 3.24.5
fvm use 3.24.5
```

### 프로젝트 생성

```bash
cd C:\workspace\2nd-Team-Project

flutter create flutter-app --org com.qtai --platforms android,ios
cd flutter-app

flutter run    # 기본 카운터 앱이 실행되면 성공
```

### pubspec.yaml 의존성 추가

`flutter-app/pubspec.yaml` 의 `dependencies:` 부분을 아래로 교체:

```yaml
dependencies:
  flutter:
    sdk: flutter

  # 상태 관리 (전역 상태를 쉽게 관리)
  flutter_riverpod: ^2.5.1

  # HTTP 클라이언트 (Interceptor 지원 -- 자동 토큰 갱신에 필요)
  dio: ^5.4.3

  # SSE 스트리밍 수신
  dio_sse: ^0.2.0

  # 화면 라우팅
  go_router: ^13.2.0

  # STOMP WebSocket (실시간 알림)
  stomp_dart_client: ^1.0.0

  # 안전한 로컬 저장소 (JWT 토큰 저장)
  flutter_secure_storage: ^9.0.0

  # Google 로그인
  google_sign_in: ^6.2.1

  # 날짜 포맷
  intl: ^0.19.0

dev_dependencies:
  flutter_test:
    sdk: flutter
  mocktail: ^1.0.3
  flutter_lints: ^3.0.0
```

```bash
flutter pub get
flutter analyze
# No issues found!  나와야 함
```

---

## 2. Day1~2 -- 5/12~5/13: 라우팅 + 기본 구조

### 폴더 구조 만들기

`flutter-app/lib/` 아래에 아래 폴더들을 만든다.

```
lib/
├── main.dart
├── core/
│   ├── network/
│   │   ├── dio_client.dart       DIO 설정 + JWT 자동 갱신
│   │   └── sse_client.dart       SSE 수신 클라이언트
│   ├── router/
│   │   └── app_router.dart       화면 라우팅
│   └── theme/
│       └── app_theme.dart        앱 색상/폰트
├── features/
│   ├── auth/                     로그인/회원가입
│   ├── home/                     홈 대시보드
│   ├── bible/                    성경 구절 화면
│   ├── ai_chat/                  AI 대화 화면
│   └── journal/                  묵상 노트 화면
└── shared/
    └── widgets/                  공통 위젯
```

### main.dart

```dart
// flutter-app/lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';

void main() {
  runApp(
    // ProviderScope: RiverPod 상태 관리를 앱 전체에서 쓸 수 있게 감싸주는 것
    const ProviderScope(
      child: QtAiApp(),
    ),
  );
}

class QtAiApp extends ConsumerWidget {
  const QtAiApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'QT-AI',
      routerConfig: router,
    );
  }
}
```

### app_router.dart

```dart
// flutter-app/lib/core/router/app_router.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/login',
    routes: [
      GoRoute(path: '/login',   builder: (ctx, state) => const LoginScreen()),
      GoRoute(path: '/home',    builder: (ctx, state) => const HomeScreen()),
      GoRoute(path: '/bible',   builder: (ctx, state) => const BibleScreen()),
      GoRoute(path: '/ai-chat', builder: (ctx, state) => const AiChatScreen()),
      GoRoute(path: '/journal', builder: (ctx, state) => const JournalScreen()),
    ],
  );
});
```

### dio_client.dart -- DIO 설정 + JWT 자동 갱신

**왜 DIO 를 쓰는가?**
기본 http 패키지는 Interceptor 기능이 없다.
DIO 는 모든 요청에 JWT 토큰을 자동으로 붙이고,
401 응답 시 Refresh Token 으로 자동 갱신할 수 있다.

```dart
// flutter-app/lib/core/network/dio_client.dart
import 'package:dio/dio.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

const String baseUrl = 'http://localhost:8080';    // Gateway 주소

Dio createDio() {
  final dio = Dio(BaseOptions(
    baseUrl: baseUrl,
    connectTimeout: const Duration(seconds: 10),
    receiveTimeout: const Duration(seconds: 30),
    headers: {'Content-Type': 'application/json'},
  ));

  dio.interceptors.add(JwtInterceptor(dio));
  return dio;
}

class JwtInterceptor extends Interceptor {
  final Dio dio;
  final _storage = const FlutterSecureStorage();

  JwtInterceptor(this.dio);

  // 모든 요청 전: Authorization 헤더에 Access Token 자동 추가
  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _storage.read(key: 'access_token');
    if (token != null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  // 401 응답: Access Token 만료 --> Refresh Token 으로 갱신 후 재시도
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      final refreshToken = await _storage.read(key: 'refresh_token');
      if (refreshToken != null) {
        try {
          final response = await dio.post('/auth/refresh',
            data: {'refreshToken': refreshToken},
            options: Options(headers: {'Authorization': null}),
          );
          final newToken = response.data['accessToken'];
          await _storage.write(key: 'access_token', value: newToken);

          // 원래 요청 다시 시도
          err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
          final retryResponse = await dio.request(
            err.requestOptions.path,
            options: Options(method: err.requestOptions.method),
          );
          return handler.resolve(retryResponse);
        } catch (_) {
          await _storage.deleteAll();    // 갱신 실패 --> 로그아웃
        }
      }
    }
    handler.next(err);
  }
}
```

---

## 3. Day3~5 -- 5/14~5/16: 로그인 화면 + API 연동

### 로그인 화면 (Mock 먼저, API 연동은 나중에)

**W1 에는 Auth Service 가 아직 완성 중일 수 있다.**
그래도 화면을 먼저 만들어두면 API 완성 후 연결만 하면 된다.

```dart
// flutter-app/lib/features/auth/login_screen.dart
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController    = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _login() async {
    setState(() => _isLoading = true);
    try {
      // TODO W1 후반: 실제 API 호출로 교체
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) context.go('/home');
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('QT-AI', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('성경 큐티 AI 코칭', style: TextStyle(color: Colors.grey)),
            const SizedBox(height: 48),
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(labelText: '이메일', border: OutlineInputBorder()),
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: '비밀번호', border: OutlineInputBorder()),
              obscureText: true,
            ),
            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity, height: 50,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _login,
                child: _isLoading
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('로그인', style: TextStyle(fontSize: 16)),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 4. W2 -- 핵심 화면 완성

### Sliver Sync Scroll -- 한/영 성경 동기화 스크롤

**왜 Sliver 를 쓰는가?**
일반 ListView 두 개를 나란히 놓으면 각자 따로 스크롤된다.
Sliver 와 ScrollController 를 연결하면 하나를 스크롤할 때 다른 것도 같이 움직인다.

```dart
// flutter-app/lib/features/bible/bible_screen.dart
import 'package:flutter/material.dart';

class BibleScreen extends StatefulWidget {
  const BibleScreen({super.key});

  @override
  State<BibleScreen> createState() => _BibleScreenState();
}

class _BibleScreenState extends State<BibleScreen> {
  final ScrollController _koController = ScrollController();
  final ScrollController _enController = ScrollController();
  bool _isSyncing = false;   // 무한 루프 방지용 플래그

  @override
  void initState() {
    super.initState();

    // 한국어 스크롤 변화 --> 영어에 반영
    _koController.addListener(() {
      if (!_isSyncing) {
        _isSyncing = true;
        _enController.jumpTo(_koController.offset);
        _isSyncing = false;
      }
    });

    // 영어 스크롤 변화 --> 한국어에 반영
    _enController.addListener(() {
      if (!_isSyncing) {
        _isSyncing = true;
        _koController.jumpTo(_enController.offset);
        _isSyncing = false;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    // Mock 데이터 (나중에 Bible API 로 교체)
    final List<Map<String, String>> verses = [
      {'ko': '1. 그 때에 바리새인 중에 니고데모라 하는 사람이 있으니',
       'en': '1. There was a man of the Pharisees, named Nicodemus'},
      {'ko': '3. 예수께서 대답하여 이르시되 진실로 진실로',
       'en': '3. Jesus answered and said unto him, Verily, verily'},
      {'ko': '16. 하나님이 세상을 이처럼 사랑하사 독생자를 주셨으니',
       'en': '16. For God so loved the world, that he gave his only begotten Son'},
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('요한복음 3장')),
      body: Row(
        children: [
          // 한국어 (왼쪽)
          Expanded(
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  color: Colors.blue.shade50,
                  width: double.infinity,
                  child: const Text('한국어 (개역개정)',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                Expanded(
                  child: ListView.builder(
                    controller: _koController,   // 컨트롤러 연결 (핵심!)
                    itemCount: verses.length,
                    itemBuilder: (ctx, idx) => Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(verses[idx]['ko']!, style: const TextStyle(height: 1.8)),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const VerticalDivider(width: 1, color: Colors.grey),
          // 영어 (오른쪽)
          Expanded(
            child: Column(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  color: Colors.green.shade50,
                  width: double.infinity,
                  child: const Text('English (KJV)',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                Expanded(
                  child: ListView.builder(
                    controller: _enController,   // 컨트롤러 연결 (핵심!)
                    itemCount: verses.length,
                    itemBuilder: (ctx, idx) => Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(verses[idx]['en']!, style: const TextStyle(height: 1.8)),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _koController.dispose();
    _enController.dispose();
    super.dispose();
  }
}
```

### SSE 스트리밍 AI 대화 화면

**SSE 란?**
서버가 클라이언트로 데이터를 계속 스트리밍하는 방식이다.
Claude 가 토큰 하나를 생성할 때마다 즉시 화면에 표시된다.

```dart
// flutter-app/lib/features/ai_chat/ai_chat_screen.dart
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import 'package:dio_sse/dio_sse.dart';

class AiChatScreen extends StatefulWidget {
  const AiChatScreen({super.key});

  @override
  State<AiChatScreen> createState() => _AiChatScreenState();
}

class _AiChatScreenState extends State<AiChatScreen> {
  final List<Map<String, String>> _messages = [];
  final _inputController = TextEditingController();
  String _streamingText = '';
  bool _isStreaming = false;

  Future<void> _sendMessage(String userMessage) async {
    if (userMessage.trim().isEmpty || _isStreaming) return;

    setState(() {
      _messages.add({'role': 'user', 'content': userMessage});
      _streamingText = '';
      _isStreaming = true;
    });
    _inputController.clear();

    final dio = Dio();
    final sseClient = SseClient(dio);

    try {
      sseClient
          .connect(
            'http://localhost:8080/ai/sessions/1/messages',
            method: 'POST',
            body: jsonEncode({'userMessage': userMessage}),
            headers: {'Content-Type': 'application/json', 'X-User-Id': '1'},
          )
          .listen(
            (SseEvent event) {
              if (event.data == null) return;
              try {
                final data = jsonDecode(event.data!);
                if (data['type'] == 'token') {
                  // 새 토큰이 올 때마다 화면 업데이트 (타이핑 효과)
                  setState(() => _streamingText += data['data'] ?? '');
                } else if (data['type'] == 'done') {
                  setState(() {
                    _messages.add({'role': 'assistant', 'content': _streamingText});
                    _streamingText = '';
                    _isStreaming = false;
                  });
                }
              } catch (_) {}
            },
            onError: (_) {
              if (mounted) setState(() => _isStreaming = false);
            },
          );
    } catch (_) {
      if (mounted) setState(() => _isStreaming = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('AI 큐티 코칭')),
      body: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            color: Colors.blue.shade50, width: double.infinity,
            child: const Text('A단계: 관찰 - 본문에서 무엇을 발견했나요?',
              textAlign: TextAlign.center, style: TextStyle(fontWeight: FontWeight.bold)),
          ),
          // 메시지 목록
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length + (_isStreaming ? 1 : 0),
              itemBuilder: (ctx, idx) {
                if (idx == _messages.length && _isStreaming) {
                  return _buildBubble('assistant', '$_streamingText|');
                }
                final msg = _messages[idx];
                return _buildBubble(msg['role']!, msg['content']!);
              },
            ),
          ),
          // 입력창
          Padding(
            padding: const EdgeInsets.all(8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _inputController,
                    decoration: const InputDecoration(
                      hintText: '묵상한 내용을 나눠주세요...',
                      border: OutlineInputBorder(),
                    ),
                    maxLines: null,
                    onSubmitted: _sendMessage,
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  icon: const Icon(Icons.send),
                  onPressed: _isStreaming
                      ? null
                      : () => _sendMessage(_inputController.text),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBubble(String role, String content) {
    final isUser = role == 'user';
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 4),
        padding: const EdgeInsets.all(12),
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.75,
        ),
        decoration: BoxDecoration(
          color: isUser ? Colors.blue[600] : Colors.grey[200],
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          content,
          style: TextStyle(color: isUser ? Colors.white : Colors.black87),
        ),
      ),
    );
  }
}
```

---

## 5. 자주 발생하는 오류

| 오류 | 원인 | 해결 |
|------|------|------|
| `MissingPluginException` | pubspec.yaml 변경 후 hot restart 안 함 | 앱 완전 종료 후 다시 `flutter run` |
| DIO 401 무한 루프 | 인터셉터 재귀 호출 | refresh 요청에서 인터셉터 제외 (`Authorization: null`) |
| 두 ListView 스크롤 동기화 안 됨 | controller 를 ListView 에 안 넘김 | `controller: _koController` 확인 |
| SSE 응답 없음 | CORS 문제 또는 Gateway 버퍼링 | 강태오에게 Gateway CORS, NoBufferingFilter 확인 요청 |
| `setState after dispose` | dispose 후 setState 호출 | `if (mounted) setState(...)` 로 감싸기 |
| `flutter analyze` 오류 | 코드 품질 문제 | 출력된 경고 하나씩 해결 후 커밋 |

---

## 6. Flutter 빌드 + 실행 명령어 모음

```bash
# 의존성 설치
flutter pub get

# 분석 (오류 없어야 함)
flutter analyze

# 테스트 실행
flutter test

# 안드로이드 디버그 빌드
flutter run -d android

# 릴리즈 APK 빌드 (시연용)
flutter build apk --release

# hot reload: 앱 실행 중 r 키 입력
# hot restart: 앱 실행 중 R 키 입력 (상태 초기화)
```

---

## 7. W3~W5 주간 요약

| 주차 | 김지민 핵심 작업 |
|------|----------------|
| W3 (6/1~6/5) | STOMP WebSocket 알림 배지, Google OAuth 연동, 큐티 A-D 단계 진행 UI |
| W4 (6/8~6/12) | 전체 화면 UI 완성도 polish, 시연 dry-run 화면 흐름 주도 |
| W5 (6/15~6/17) | 시연 기기 세팅, 리허설 화면 흐름 담당, 발표 데모 담당 |
