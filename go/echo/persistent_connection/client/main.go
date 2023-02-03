package main

import (
	"bufio"
	"fmt"
	"net/http"
	"time"
)

func main() {
	tr := &http.Transport{
		MaxConnsPerHost:    3,
		MaxIdleConns:       5,
		IdleConnTimeout:    30 * time.Second,
		DisableCompression: true,
	}
	client := &http.Client{Transport: tr}

	for i := 0; i < 1; i++ {
		resp, err := client.Get("http://localhost:8081")
		if err != nil {
			panic(err)
		}
		defer resp.Body.Close()

		scanner := bufio.NewScanner(resp.Body)
		for scanner.Scan() {
			fmt.Println(scanner.Text(), " + ", i)
		}
	}
}
