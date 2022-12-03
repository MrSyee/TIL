package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"service/controller"

	_ "service/docs"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	echoSwagger "github.com/swaggo/echo-swagger"
)

// Flags contains the information to send requests to Triton inference server.
type Flags struct {
	PORT   string
	SumURL string
}

func parseFlags() Flags {
	var flags = Flags{}
	flag.StringVar(&flags.PORT, "p", "10000", "Service Port. Default: 10000")
	flag.StringVar(&flags.SumURL, "u", "http://localhost:20000/sum", "Target URL")
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
	cont := controller.NewController()

	// Logger
	e.Use(middleware.Logger())

	// APIs
	e.GET("/", getHealthCheck)
	e.POST("/sum", func(c echo.Context) error {
		return cont.Sum(c, flags.SumURL)
	},
	)

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
