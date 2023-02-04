package main

import (
	"bufio"
	"flag"
	"fmt"
	"net/http"
	"time"
)

var (
	num int
)

func main() {
	// Parse args.
	flag.IntVar(&num, "n", 1, "The number of requests")
	flag.Parse()

	// Set persistent connection.
	tr := &http.Transport{
		MaxConnsPerHost:    3,
		MaxIdleConns:       5,
		IdleConnTimeout:    10 * time.Second,
		DisableCompression: true,
	}
	client := &http.Client{Transport: tr}

	// Request.
	for i := 0; i < num; i++ {
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
