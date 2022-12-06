package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"

	_ "microservice/docs"
	"microservice/handler"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	echoSwagger "github.com/swaggo/echo-swagger"
)

// Flags contains the information to send requests to Triton inference server.
type Flags struct {
	PORT string
}

func parseFlags() Flags {
	var flags = Flags{}
	flag.StringVar(&flags.PORT, "p", "20000", "Service Port. Default: 20000")
	return flags
}

// @contact.name  Kyunghwan Kim
// @contact.email khsyee@gmail.com
func main() {
	// Flag
	flags := parseFlags()
	log.Println("Flags:", flags)

	// Create a server with echo.
	e := echo.New()
	h := handler.NewHandler()

	// Logger
	e.Use(middleware.Logger())

	// APIs
	e.GET("/", getHealthCheck)
	e.POST("/sum", h.Sum)
	e.POST("/file", h.ReceiveFile)

	// Swagger
	e.GET("/docs/*", echoSwagger.WrapHandler)

	e.Logger.Fatal(e.Start(":" + flags.PORT))
}

// @Summary     Healthcheck
// @Description It returns true if the api server is alive.
// @Accept      json
// @Produce     json
// @Success     200 {object} bool "API server's liveness"
// @Router      / [get]
func getHealthCheck(c echo.Context) error {
	return fmt.Errorf("%w", c.JSON(http.StatusOK, true))
}
