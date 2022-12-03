package client

import (
	"bytes"
	"encoding/json"
	"net/http"

	"github.com/labstack/gommon/log"
)

// Request input type
type IntegersInput struct {
	InputX int `json:"inputX"`
	InputY int `json:"inputY"`
}

// Request output type
type IntegerOutput struct {
	Sum int `json:"sum"`
}

// Define client
type ArithmeticClient struct {
	url string
}

func NewArithmeticClient(url string) ArithmeticClient {
	client := ArithmeticClient{url}
	return client
}

func (client ArithmeticClient) SumRequest(x int, y int) (int, error) {
	log.Info("SumRequest")
	var err error
	var sum int
	// Preprocess
	reqInput := IntegersInput{
		InputX: x,
		InputY: y,
	}
	log.Info("Sum Request Input: ", reqInput)
	reqBytes, err := json.Marshal(reqInput)
	if err != nil {
		log.Fatalf("Error processing Input to Json: %v", err)
		return sum, err
	}
	buff := bytes.NewBuffer(reqBytes)

	// Request
	resp, err := http.Post(
		client.url,
		"application/json",
		buff,
	)
	if err != nil {
		log.Fatalf("Error processing Request: %v", err)
		return sum, err
	}

	// Postprocess
	// Response.Body is io.ReadCloser
	defer resp.Body.Close()
	var output IntegerOutput
	err = json.NewDecoder(resp.Body).Decode(&output)
	if err != err {
		log.Fatalf("Error Post Response: %v", err)
		return sum, err
	}

	log.Info("Response is ", output)
	return output.Sum, err
}
