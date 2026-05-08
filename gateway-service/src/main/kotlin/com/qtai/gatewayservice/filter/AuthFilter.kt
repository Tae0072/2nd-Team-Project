package com.qtai.gatewayservice.filter

import io.jsonwebtoken.ExpiredJwtException
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.security.SecurityException
import org.springframework.beans.factory.annotation.Value
import org.springframework.cloud.gateway.filter.GatewayFilter
import org.springframework.cloud.gateway.filter.factory.AbstractGatewayFilterFactory
import org.springframework.core.io.Resource
import org.springframework.http.HttpStatus
import org.springframework.stereotype.Component
import org.springframework.web.server.ServerWebExchange
import reactor.core.publisher.Mono
import java.security.KeyFactory
import java.security.interfaces.RSAPublicKey
import java.security.spec.X509EncodedKeySpec
import java.util.Base64

// AuthFilter - JWT RS256 검증 후 X-User-Id 헤더 주입
//
// P1-5 보안 수정:
//   헤더 추가(.header) 대신 덮어쓰기(.headers { it.set(...) }) 사용.
//   클라이언트가 X-User-Id 를 미리 보내도 Gateway 검증값으로 완전히 교체됨.
//   -> ID spoofing 방지.
//
// 인증 제외 경로 (application.yml 에서 이 필터를 미적용):
//   /api/v1/auth/... (로그인/회원가입)
//   /ws/...          (WebSocket 핸드셰이크 - STOMP CONNECT 프레임에서 BFF가 직접 검증)
@Component
class AuthFilter(
    @Value("\${jwt.public-key-path}")
    private val publicKeyPath: Resource
) : AbstractGatewayFilterFactory<AuthFilter.Config>(Config::class.java) {

    private val publicKey: RSAPublicKey by lazy { loadPublicKey() }

    override fun apply(config: Config): GatewayFilter = GatewayFilter { exchange, chain ->
        val token = extractToken(exchange) ?: return@GatewayFilter unauthorized(exchange)
        try {
            val claims = Jwts.parser()
                .verifyWith(publicKey)
                .build()
                .parseSignedClaims(token)
            val userId = claims.payload["userId"]?.toString()
                ?: return@GatewayFilter unauthorized(exchange)

            // P1-5 fix: .headers { it.set() } 는 기존 값을 완전히 대체 (spoofing 방지)
            val mutated = exchange.request.mutate()
                .headers { headers -> headers.set("X-User-Id", userId) }
                .build()
            chain.filter(exchange.mutate().request(mutated).build())
        } catch (e: ExpiredJwtException) {
            unauthorized(exchange)
        } catch (e: SecurityException) {
            unauthorized(exchange)
        } catch (e: Exception) {
            unauthorized(exchange)
        }
    }

    private fun extractToken(exchange: ServerWebExchange): String? =
        exchange.request.headers.getFirst("Authorization")
            ?.takeIf { it.startsWith("Bearer ") }
            ?.substring(7)

    private fun unauthorized(exchange: ServerWebExchange): Mono<Void> {
        exchange.response.statusCode = HttpStatus.UNAUTHORIZED
        return exchange.response.setComplete()
    }

    private fun loadPublicKey(): RSAPublicKey {
        val pem = publicKeyPath.inputStream.bufferedReader().use { it.readText() }
            .replace("-----BEGIN PUBLIC KEY-----", "")
            .replace("-----END PUBLIC KEY-----", "")
            .replace("\n", "").trim()
        val decoded = Base64.getDecoder().decode(pem)
        return KeyFactory.getInstance("RSA")
            .generatePublic(X509EncodedKeySpec(decoded)) as RSAPublicKey
    }

    class Config
}
