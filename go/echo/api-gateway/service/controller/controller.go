package controller

import (
	"fmt"
	"net/http"

	"service/client"

	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"
)

// API inputs, outputs
type IntegersInput struct {
	InputX int `json:"inputX" form:"inputX" xml:"inputX"`
	InputY int `json:"inputY" form:"inputY" xml:"inputY"`
}

type IntegerOutput struct {
	Sum int `json:"sum" form:"sum" xml:"sum"`
}

// Controller
type Controller struct {
}

func NewController() Controller {
	controller := Controller{}
	return controller
}

// @Summary     Sum integer inputs
// @Description It outputs sum of two inputs
// @Accept      x-www-form-urlencoded
// @Produce     json
// @Param       inputX  formData  integer  true  "inputX"
// @Param       inputY  formData  integer  true  "inputY"
// @Success     200 {object} integer "Integer response: int"
// @Router      /sum [post]
func (controller Controller) Sum(c echo.Context, url string) error {
	// Create client
	client := client.NewArithmeticClient(url)

	// Input
	inputs := new(IntegersInput)
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

	return fmt.Errorf("%w", c.JSON(http.StatusOK, IntegerOutput{Sum: sum}))
}
