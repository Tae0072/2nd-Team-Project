// 2026-05-14 v2.0 — Modular Monolith 전환 (ADR-0001)
// v1: 단일 qtai-server 모듈 (도메인 패키지 6개: gatewayauth · bff · bible · ai · journal · simulator)
// v2 분리 시(ADR-0016): qtai-ai-service 등 별도 모듈로 분리

rootProject.name = "qt-ai"

include(
    "qtai-server"
    // v2 분리 시 추가 모듈: "qtai-ai-service" (ADR-0016 트리거 충족 시)
)

// flutter-app은 Dart/Flutter 프로젝트라 Gradle 스코프 외
// 도메인 경계는 Spring Modulith + ArchUnit (ADR-0015)로 강제
