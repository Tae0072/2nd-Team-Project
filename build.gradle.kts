import org.jetbrains.kotlin.gradle.tasks.KotlinCompile

plugins {
    kotlin("jvm") version "1.9.23" apply false
    kotlin("plugin.spring") version "1.9.23" apply false
    id("org.springframework.boot") version "3.3.1" apply false
    id("io.spring.dependency-management") version "1.1.5" apply false
}

// 루트 프로젝트는 소스 없음 — 서브모듈 공통 설정만
subprojects {
    apply(plugin = "kotlin")
    apply(plugin = "io.spring.dependency-management")

    group = "com.qtai"
    version = "0.0.1-SNAPSHOT"

    repositories {
        mavenCentral()
    }

    // Spring Boot BOM — 버전 고정 (AI 환각 방지)
    dependencyManagement {
        imports {
            mavenBom("org.springframework.boot:spring-boot-dependencies:3.3.1")
        }
    }

    tasks.withType<KotlinCompile> {
        kotlinOptions {
            jvmTarget = "21"
            freeCompilerArgs = listOf("-Xjsr305=strict")
        }
    }

    tasks.withType<Test> {
        useJUnitPlatform()
    }
}
