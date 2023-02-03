package main

import (
	"bufio"
	"fmt"
	"net/http"
	"time"

	"github.com/labstack/echo/v4"
)

func main() {
	e := echo.New()

	c := NewClient()
	e.GET("/", c.Request)

	// e.Server.Addr = ":8080"
	// e.Server.ReadTimeout = 0
	// e.Server.WriteTimeout = 0
	// e.Server.IdleTimeout = 0

	e.Logger.Fatal(e.Start(":8081"))
}

type Client struct {
	http *http.Client
}

func NewClient() Client {
	tr := &http.Transport{
		MaxConnsPerHost:    3,
		MaxIdleConns:       5,
		IdleConnTimeout:    10 * time.Second,
		DisableCompression: true,
	}
	client := &http.Client{Transport: tr}

	module := Client{client}
	return module
}

func (cli Client) Request(c echo.Context) error {

	resp, err := cli.http.Get("http://localhost:8080")
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	scanner := bufio.NewScanner(resp.Body)
	for scanner.Scan() {
		fmt.Println(scanner.Text())
	}

	return c.String(http.StatusOK, "Hello, World!")
}
