package handler

import (
	"fmt"
	"net/http"

	"service/client"

	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"
)

// Handler
type Handler struct {
}

func NewHandler() Handler {
	handler := Handler{}
	return handler
}

// @Summary     Sum integer inputs
// @Description It outputs sum of two inputs
// @Accept      x-www-form-urlencoded
// @Produce     json
// @Param       inputX formData integer true "inputX"
// @Param       inputY formData integer true "inputY"
// @Success     200    {object} integer "Integer response: int"
// @Router      /sum [post]
func (handler Handler) Sum(c echo.Context, url string) error {
	// Create client
	client := client.NewArithmeticClient(url)

	// Input
	inputs := new(sumRequest)
	if err := c.Bind(inputs); err != nil {
		log.Error(err.Error())
		return fmt.Errorf("%w", c.String(http.StatusBadRequest, "Bad request "+err.Error()))
	}
	// Request to microservice
	// client code
	sum, err := client.SumRequest(inputs.InputX, inputs.InputY)
	if err != nil {
		log.Error(err.Error())
		return fmt.Errorf("%w", c.String(http.StatusBadRequest, "Bad request "+err.Error()))
	}

	return fmt.Errorf("%w", c.JSON(http.StatusOK, sumRespons{Sum: sum}))
}

// @Summary     Send file
// @Description Send file
// @Accept      x-www-form-urlencoded
// @Produce     json
// @Param       file formData file    true "file"
// @Success     200  {object} boolean "Success"
// @Router      /file [post]
func (handler Handler) File(c echo.Context, url string) error {
	// Create client
	client := client.NewFileClient(url)

	// Input
	file, _ := c.FormFile("file")
	// Request to microservice
	// client code
	output, err := client.FileRequest(file)
	if err != nil {
		log.Error(err.Error())
		return fmt.Errorf("%w", c.String(http.StatusBadRequest, "Bad request "+err.Error()))
	}

	return fmt.Errorf("%w", c.JSON(http.StatusOK, output))
}
