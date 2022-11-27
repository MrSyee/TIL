package main

import (
	"fmt"
	"io"
	"net"
)

func Handle(conn net.Conn) {
	recv := make([]byte, 4096)

	for {
		n, err := conn.Read(recv)
		if err != nil {
			if err == io.EOF {
				fmt.Println("connection is closed from client : ", conn.RemoteAddr().String())
			}
			fmt.Println("Failed to receive data : ", err)
			break
		}

		if n > 0 {
			fmt.Println(string(recv[:n]))
			conn.Write(recv[:n])
		}
	}
}

func main() {
	// create listener
	listener, err := net.Listen("tcp", "127.0.0.1:8000")
	if err != nil {
		fmt.Println("Failed to listen: ", err)
	}
	fmt.Printf("bound to %q", listener.Addr())
	defer listener.Close()

	for {
		// accept connection.
		// blocking until finishing to handshake between client and server
		conn, err := listener.Accept()
		if err != nil {
			fmt.Println("Failed to accept: ", err)
			continue
		}
		defer conn.Close()

		fmt.Printf("bound to %q", listener.Addr())
		go Handle(conn)
	}
}
