package auth

import (
	"net/http"
	"time"

	"github.com/golang-jwt/jwt/v4"
	"github.com/google/uuid"
)

func GenerateTokens(
	userName string,
	userRole string,
) (accessToken string, refreshCookie *http.Cookie, err error) {
	// Access Token.
	token := jwt.New(jwt.SigningMethodHS256)
	claims := token.Claims.(jwt.MapClaims)
	claims["name"] = userName
	claims["role"] = userRole
	claims["exp"] = time.Now().Add(time.Minute * (time.Duration)(Config.AccessTokenExpire)).Unix()
	accessToken, err = token.SignedString([]byte(Config.SecretKey))
	if err != nil {
		return accessToken, refreshCookie, err
	}

	// Refresh Token.
	refreshTokenID := uuid.New().String()
	claims["token_id"] = refreshTokenID
	claims["exp"] = time.Now().Add(time.Minute * (time.Duration)(Config.RefreshTokenExpire)).Unix()
	refreshToken, err := token.SignedString([]byte(Config.SecretKey))
	if err != nil {
		return accessToken, refreshCookie, err
	}

	// Set refreshCookie
	refreshCookie = &http.Cookie{}
	refreshCookie.Name = Config.RefreshCookieName
	refreshCookie.Value = refreshToken
	refreshCookie.Path = "/"
	refreshCookie.SameSite = http.SameSiteLaxMode
	refreshCookie.Secure = false // TODO: Set TLS later.
	refreshCookie.HttpOnly = true
	refreshCookie.MaxAge = 60 * Config.RefreshTokenExpire // Sec. to Min.

	// Store the hashed refresh token in the cache.
	hash, err := HashPassword(refreshToken)
	if err != nil {
		return accessToken, refreshCookie, err
	}
	tokenCache.Set(refreshTokenID, hash)

	return accessToken, refreshCookie, err
}
