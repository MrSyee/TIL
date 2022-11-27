package main

import (
	"net/http"

	_ "quick-start/docs"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	echoSwagger "github.com/swaggo/echo-swagger"
)

// @Summary     Save user
// @Description Save user
// @Accept      x-www-form-urlencoded
// @Produce     json
// @Param       name  formData string true "name"
// @Param       email formData string true "email"
// @Success     200   {object} string "name: {name}, email: {email}"
// @Router      /users [post]
func saveUser(c echo.Context) error {
	// Get name and email
	name := c.FormValue("name")
	email := c.FormValue("email")
	return c.String(http.StatusOK, "name:"+name+", email:"+email)
}

// @Summary     Get user
// @Description Get user
// @Accept      json
// @Produce     json
// @Param       id  path     string true "name of the user"
// @Success     200 {object} string "user id"
// @Router      /users/{id} [get]
func getUser(c echo.Context) error {
	// User ID from path `users/:id`
	id := c.Param("id")
	return c.String(http.StatusOK, id)
}

// @contact.name  Annotation-AI
// @contact.email dev@annotation-ai.com
func main() {
	e := echo.New()

	e.Use(middleware.Logger())

	e.GET("/", func(c echo.Context) error {
		return c.String(http.StatusOK, "Hello, World!")
	})
	e.POST("/users", saveUser)
	e.GET("/users/:id", getUser)
	e.GET("/docs/*", echoSwagger.WrapHandler)

	e.Logger.Fatal(e.Start(":1323"))
}
