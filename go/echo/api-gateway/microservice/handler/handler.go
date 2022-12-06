package handler

import (
	"fmt"
	"io"
	"net/http"

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
func (handler Handler) Sum(c echo.Context) error {
	log.Info("[POST] Sum")
	inputs := new(sumRequest)
	if err := c.Bind(inputs); err != nil {
		log.Error(err.Error())
		return fmt.Errorf("%w", c.String(http.StatusBadRequest, "Bad request "+err.Error()))
	}
	log.Info("Inputs ", *inputs)

	// Business logic
	sumOutput := sum(inputs.InputX, inputs.InputY)
	response := sumResponse{Sum: sumOutput}
	log.Info("Run Sum logic ", response)
	return fmt.Errorf("%w", c.JSON(http.StatusOK, response))
}

// @Summary     Receive file
// @Description Receive file
// @Accept      x-www-form-urlencoded
// @Produce     json
// @Param       file formData file    true "input"
// @Success     200  {object} boolean "Success"
// @Router      /file [post]
func (handler Handler) ReceiveFile(c echo.Context) error {
	log.Info("[POST] ReceiveFile")
	inputs := new(fileRequest)
	inputs.File, _ = c.FormFile("file")
	file := inputs.File
	f, err := file.Open()
	if err != nil {
		log.Info("open ", file.Filename, "error: ", err.Error())
		return fmt.Errorf("%w", err)
	}
	_, err = io.ReadAll(f)
	log.Info("read file ", file.Filename, "error: ", err)

	response := fileResponse{Success: true}
	return fmt.Errorf("%w", c.JSON(http.StatusOK, response))
}
