/*
Simple HTTP File Server for Personal Website Development

This Go program creates a simple HTTP file server for serving static files
during website development. It serves files from a specified directory
and listens on localhost:3000.

Usage:
    go run fileserver.go <directory_path>

Example:
    go run fileserver.go docs/

The server will serve files from the specified directory at:
    http://127.0.0.1:3000

Author: Khanh
Repository: fbundle.github.io
*/

package main

import (
	"log"
	"net/http"
	"os"
)

const (
	// Server address - listens on localhost port 3000
	addr = "127.0.0.1:3000"
)

func main() {
	// Get the root directory from command line arguments
	// The first argument should be the path to the directory to serve
	if len(os.Args) < 2 {
		log.Fatal("Usage: go run fileserver.go <directory_path>")
	}
	rootDir := os.Args[1]

	// Create a file server that serves files from the specified directory
	fs := http.FileServer(http.Dir(rootDir))

	// Handle all requests by serving files from the root directory
	// StripPrefix removes the "/" prefix from requests before serving files
	http.Handle("/", http.StripPrefix("/", fs))

	// Log that the server is starting and listen for connections
	log.Println("Server is up:", addr)
	log.Println("Serving files from:", rootDir)
	log.Println("Access your website at: http://" + addr)

	// Start the HTTP server and log any fatal errors
	log.Fatal(http.ListenAndServe(addr, nil))
}
