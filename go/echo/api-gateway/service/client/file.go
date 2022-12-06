package client

import (
	"bytes"
	"encoding/json"
	"io"
	"mime/multipart"
	"net/http"

	"github.com/labstack/gommon/log"
)

// Define client
type FileClient struct {
	url string
}

func NewFileClient(url string) FileClient {
	client := FileClient{url}
	return client
}

func (client FileClient) FileRequest(file *multipart.FileHeader) (bool, error) {
	log.Info("FileRequest")
	var err error

	// Preprocess
	f, err := file.Open()
	if err != nil {
		log.Fatalf("failed to get file content from form file: %v", err)
	}
	defer f.Close()
	imgByte, err := io.ReadAll(f)
	if err != nil {
		log.Fatalf("failed to get raw input from file content: %v", err)
	}

	body := bytes.NewBuffer(imgByte)
	resp, err := http.Post(
		client.url,
		"multipart/form-data",
		body,
	)
	if err != nil {
		log.Fatalf("%v", err)
	}

	// Postprocess
	// Response.Body: io.ReadCloser
	defer resp.Body.Close()
	var fileResp fileResponse
	err = json.NewDecoder(resp.Body).Decode(&fileResp)
	if err != err {
		log.Fatalf("Error Post Response: %v", err)
		return false, err
	}

	log.Info("Response is ", resp)
	return fileResp.Success, err
}
