package main

import (
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/rs/zerolog/log"
)

func main() {
	e := echo.New()

	e.GET("/", func(c echo.Context) error {
		log.Print("Get Hello world")
		return c.String(http.StatusOK, "Hello, World!")
	})

	e.Logger.Fatal(e.Start(":8080"))
}

// e.Server.Addr = ":8080"
// e.Server.ReadTimeout = 0
// e.Server.WriteTimeout = 0
// e.Server.IdleTimeout = 0
