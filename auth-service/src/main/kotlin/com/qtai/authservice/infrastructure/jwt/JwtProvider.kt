package com.qtai.authservice.infrastructure.jwt

import io.jsonwebtoken.ExpiredJwtException
import io.jsonwebtoken.Jwts
import io.jsonwebtoken.security.SecurityException
import org.springframework.beans.factory.annotation.Value
import org.springframework.core.io.Resource
import org.springframework.stereotype.Component
import java.security.KeyFactory
import java.security.interfaces.RSAPrivateKey
import java.security.interfaces.RSAPublicKey
import java.security.spec.PKCS8EncodedKeySpec
import java.security.spec.X509EncodedKeySpec
import java.util.Base64
import java.util.Date

@Component
class JwtProvider(
    @Value("\${jwt.private-key-path}") private val privateKeyRes: Resource,
    @Value("\${jwt.public-key-path}")  private val publicKeyRes: Resource
) {
    private val ACCESS_EXPIRY  = 15 * 60 * 1000L
    private val REFRESH_EXPIRY = 7 * 24 * 60 * 60 * 1000L

    private val privateKey: RSAPrivateKey by lazy { loadPrivateKey() }
    private val publicKey: RSAPublicKey   by lazy { loadPublicKey() }

    fun issueAccessToken(userId: Long): String = Jwts.builder()
        .claim("userId", userId)
        .issuedAt(Date())
        .expiration(Date(System.currentTimeMillis() + ACCESS_EXPIRY))
        .signWith(privateKey, Jwts.SIG.RS256)
        .compact()

    fun issueRefreshToken(userId: Long): String = Jwts.builder()
        .claim("userId", userId)
        .issuedAt(Date())
        .expiration(Date(System.currentTimeMillis() + REFRESH_EXPIRY))
        .signWith(privateKey, Jwts.SIG.RS256)
        .compact()

    fun getUserId(token: String): Long {
        val claims = Jwts.parser()
            .verifyWith(publicKey)
            .build()
            .parseSignedClaims(token)
        return (claims.payload["userId"] as Int).toLong()
    }

    fun isExpired(token: String): Boolean = try {
        Jwts.parser().verifyWith(publicKey).build().parseSignedClaims(token)
        false
    } catch (_: ExpiredJwtException) { true }
      catch (_: SecurityException)   { true }

    private fun stripPem(pem: String, header: String, footer: String) =
        pem.replace(header, "").replace(footer, "")
            .replace("\r", "").replace("\n", "").trim()  // \r\n 모두 제거

    private fun loadPrivateKey(): RSAPrivateKey {
        val raw = privateKeyRes.inputStream.bufferedReader().use { it.readText() }
        val b64 = stripPem(raw, "-----BEGIN PRIVATE KEY-----", "-----END PRIVATE KEY-----")
        return KeyFactory.getInstance("RSA")
            .generatePrivate(PKCS8EncodedKeySpec(Base64.getDecoder().decode(b64))) as RSAPrivateKey
    }

    private fun loadPublicKey(): RSAPublicKey {
        val raw = publicKeyRes.inputStream.bufferedReader().use { it.readText() }
        val b64 = stripPem(raw, "-----BEGIN PUBLIC KEY-----", "-----END PUBLIC KEY-----")
        return KeyFactory.getInstance("RSA")
            .generatePublic(X509EncodedKeySpec(Base64.getDecoder().decode(b64))) as RSAPublicKey
    }
}
