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

func (client FileClient) FileRequest(file *multipart.FileHeader, queryParams map[string]string) (bool, error) {
	log.Info("FileRequest")
	var err error

	// Preprocess
	f, err := file.Open()
	if err != nil {
		log.Errorf("failed to get file content from form file: %v", err)
		return false, err
	}
	defer f.Close()

	buf := &bytes.Buffer{}
	mWriter := multipart.NewWriter(buf)
	fWriter, _ := mWriter.CreateFormFile("file", "sample.jpg")
	_, _ = io.Copy(fWriter, f)
	mWriter.Close()

	req, _ := http.NewRequest("POST", client.url, buf)
	req.Header.Add("Content-Type", mWriter.FormDataContentType())
	q := req.URL.Query()
	for key, val := range queryParams {
		q.Add(key, val)
	}
	req.URL.RawQuery = q.Encode()

	httpClient := &http.Client{}
	resp, err := httpClient.Do(req)
	if err != nil {
		log.Errorf("failed to request: %v", err)
		return false, err
	}

	// Postprocess
	// Response.Body: io.ReadCloser
	defer resp.Body.Close()
	var fileResp fileResponse
	err = json.NewDecoder(resp.Body).Decode(&fileResp)
	if err != err {
		log.Errorf("Error Post Response: %v", err)
		return false, err
	}

	log.Info("Response is ", fileResp.Success)
	return fileResp.Success, err
}
