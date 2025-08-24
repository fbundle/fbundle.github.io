package main

import (
	"log"
	"net/http"
	"os"
)

const (
	addr = "127.0.0.1:3000"
)

func main() {
	rootDir := os.Args[1]

	fs := http.FileServer(http.Dir(rootDir))
	http.Handle("/", http.StripPrefix("/", fs))
	log.Println("Server is up:", addr)
	log.Fatal(http.ListenAndServe(addr, nil))
}
