rootProject.name = "qt-ai"

include(
    "gateway",
    "bff-aggregator",
    "bible-service",
    "ai-service"
)

// flutter-app은 Dart/Flutter 프로젝트라 Gradle 스코프 외
// Auth 기능은 gateway 내부 모듈에서 처리하고, Journal 도메인은 bible-service에 통합한다.
