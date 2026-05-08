plugins {
    kotlin("jvm")
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter")
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin")
    implementation("org.jetbrains.kotlin:kotlin-reflect")
}

// Spring Boot 플러그인 미적용 — 라이브러리 모듈
configurations.all {
    exclude(group = "org.springframework.boot", module = "spring-boot-starter-tomcat")
}