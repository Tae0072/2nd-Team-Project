# qtai-server

QT-AI v1의 단일 Spring Boot 백엔드 애플리케이션 기준 디렉터리다.

## 패키지 기준

```text
src/main/java/com/qtai/
    gatewayauth/
    bff/
    bible/
        journal/
        songs/
    ai/
    simulator/
```

## 원칙

- 독립 서비스로 분리하지 않는다.
- 다른 도메인의 Entity, Service, Repository를 직접 import하지 않는다.
- 도메인 간 호출은 `api/` 하위 Port/DTO로 처리한다.
- 사용자 요청 경로에서 LLM을 호출하지 않는다.
