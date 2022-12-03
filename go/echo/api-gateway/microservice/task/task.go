package task

import (
	"fmt"
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"
)

type (
	IntegersInput struct {
		InputX int `json:"inputX" form:"inputX" xml:"inputX"`
		InputY int `json:"inputY" form:"inputY" xml:"inputY"`
	}

	IntegerOutput struct {
		Sum int `json:"sum" form:"sum" xml:"sum"`
	}
)

// @Summary     Sum integer inputs
// @Description It outputs sum of two inputs
// @Accept      x-www-form-urlencoded
// @Produce     json
// @Param       inputX  formData  integer  true  "inputX"
// @Param       inputY  formData  integer  true  "inputY"
// @Success     200 {object} integer "Integer response: int"
// @Router      /sum [post]
func Sum(c echo.Context) error {
	log.Info("[POST] Sum")
	inputs := new(IntegersInput)
	if err := c.Bind(inputs); err != nil {
		log.Error(err.Error())
		return fmt.Errorf("%w", c.String(http.StatusBadRequest, "Bad request "+err.Error()))
	}
	log.Info("Inputs ", *inputs)

	// Business logic
	response := IntegerOutput{Sum: (inputs.InputX + inputs.InputY)}
	log.Info("Run Sum logic ", response)
	return fmt.Errorf("%w", c.JSON(http.StatusOK, response))
}

// func Multiply(x int, y int) error {
// 	return x * y
// }
