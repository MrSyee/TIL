package api

import (
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"

	auth "echo-login/src/auth"
	db "echo-login/src/database"
	"echo-login/src/dto"
)

func Login(c echo.Context) error {
	// Bind the request body.
	loginReq := dto.LoginReq{}
	if err := c.Bind(&loginReq); err != nil {
		return c.String(http.StatusBadRequest, "bad request")
	}
	log.Printf("db.UserPasswordDB: %s", db.UserPasswordDB)

	// Compare the password.
	hash, exists := db.UserPasswordDB[loginReq.Username] // dummy db
	log.Printf("hash: %s", hash)
	log.Printf("exists: %t", exists)

	// Generate tokens
	role, exists := db.UserRoleDB[loginReq.Username]
	if !exists {
		return c.String(http.StatusInternalServerError, "failed to get the role of the user")
	}
	accessToken, refreshCookie, err := auth.GenerateTokens(loginReq.Username, role)
	if err != nil {
		return c.String(http.StatusInternalServerError, err.Error())
	}

	// Set cookie
	c.SetCookie(refreshCookie)

	return c.JSON(http.StatusOK, dto.LoginResp{Token: accessToken})
}
