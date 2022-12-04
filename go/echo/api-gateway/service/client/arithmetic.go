package client

import (
	"bytes"
	"encoding/json"
	"net/http"

	"github.com/labstack/gommon/log"
)

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
	sumReq := sumRequest{
		InputX: x,
		InputY: y,
	}
	log.Info("Sum Request Input: ", sumReq)
	reqBytes, err := json.Marshal(sumReq)
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
	// Response.Body: io.ReadCloser
	defer resp.Body.Close()
	var sumResp sumResponse
	err = json.NewDecoder(resp.Body).Decode(&sumResp)
	if err != err {
		log.Fatalf("Error Post Response: %v", err)
		return sum, err
	}

	log.Info("Response is ", sumResp)
	return sumResp.Sum, err
}
