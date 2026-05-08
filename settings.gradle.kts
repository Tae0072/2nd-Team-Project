rootProject.name = "qt-ai"

// ─── Spring Boot 서비스 모듈 (5개) ───────────────────────────────
include("gateway-service")
include("auth-service")
include("bible-service")
include("bff-service")
include("journal-service")

// ─── 공유 라이브러리 ─────────────────────────────────────────────
include("shared-kernel")

// ─── AI Service (Python FastAPI) : 별도 ai-service/ 디렉토리 ─────
// Python 서비스는 Gradle 외부 관리. ai-service/ 폴더 구조 참조.

pluginManagement {
    repositories {
        gradlePluginPortal()
        mavenCentral()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
    }
}