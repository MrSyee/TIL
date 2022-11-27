package main

import (
	"fmt"
	"net"
	"time"
)

func Send(c net.Conn) {
	send := "Hello"
	for {
		_, err := c.Write([]byte(send))
		if err != nil {
			fmt.Println("Failed to write data : ", err)
			break
		}

		time.Sleep(1 * time.Second)
	}
}

func Receive(c net.Conn) {
	recv := make([]byte, 4096)

	for {
		n, err := c.Read(recv)
		if err != nil {
			fmt.Println("Failed to Read data : ", err)
			break
		}

		fmt.Println(string(recv[:n]))
	}
}

func main() {
	conn, err := net.Dial("tcp", "127.0.0.1:8000")
	if err != nil {
		fmt.Println(err)
	}
	defer conn.Close()

	// send
	go Send(conn)

	// receive
	go Receive(conn)

}
