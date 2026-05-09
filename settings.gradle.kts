rootProject.name = "qt-ai"

include(
    "gateway",
    "bff-aggregator",
    "auth-service",
    "bible-service",
    "ai-service",
    "journal-service"
)

// flutter-app은 Dart/Flutter 프로젝트라 Gradle 스코프 외
