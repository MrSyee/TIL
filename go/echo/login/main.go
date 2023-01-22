package main

import (
	"flag"
	"fmt"
	"log"
	"net/http"
	"reflect"

	"github.com/labstack/echo-contrib/pprof"
	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

// Flags contains the information to send requests to Triton inference server.
type Flags struct {
	PORT    string
	PROFILE bool
}

// parseFlags parses the arguments and initialize the flags.
func parseFlags() Flags {
	var flags = Flags{}
	flag.StringVar(&flags.PORT, "port", "8080", "Service Port. Default: 10000")
	flag.BoolVar(&flags.PROFILE, "profile", false, "Enable profliling.")
	flag.Parse()
	return flags
}

func main() {
	// Parse the args.
	flags := parseFlags()
	val := reflect.ValueOf(flags)
	fmt.Println("[Flags]")
	for i := 0; i < val.NumField(); i++ {
		typeField := val.Type().Field(i)
		fmt.Printf("%s: %v\n", typeField.Name, val.Field(i))
	}

	// Create a server with echo.
	e := echo.New()
	if flags.PROFILE {
		pprof.Register(e)
		log.Println("Profiler On")
	}

	// Middlewares.
	e.Use(middleware.Recover())
	e.Use(middleware.Logger())
	// e.Use(echojwt.WithConfig(auth.GetJWTConfig()))
	// e.Use(auth.ACLCheck)

	// Skip JWT validation.
	e.GET("/", healthcheck)
	// e.POST("/login", api.Login)
	// e.POST("/refresh-token", api.RefreshToken)

	// Accessible with JWT validation.
	// e.GET("/users", api.GetUsers)
	// e.GET("/users/me", api.GetMe)
	// e.POST("/logout", api.Logout)

	// Start the server.
	e.Logger.Fatal(e.Start(":" + flags.PORT))
}

func healthcheck(c echo.Context) error {
	return c.JSON(http.StatusOK, true)
}
