rootProject.name = "qt-ai"

include(
    "gateway",
    "bff-aggregator",
    "auth-service",
    "bible-service",
    "journal-service"
)

// flutter-app은 Dart/Flutter 프로젝트라 Gradle 스코프 외
// ai-service는 Python FastAPI 프로젝트라 Gradle 스코프 외
