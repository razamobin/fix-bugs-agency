package main

import (
	"context"
	"encoding/json"
	"log"
	"net"
	"net/http"
	"os"
	"runtime"
	"time"
)

type Message struct {
	From    string    `json:"from"`
	To      string    `json:"to"`
	Content string    `json:"content"`
	SentAt  time.Time `json:"sent_at"`
	Expires *int      `json:"expires,omitempty"` // New field, pointer to allow null
}

type ChatServer struct {
	messages map[string][]Message
}

func NewChatServer() *ChatServer {
	return &ChatServer{
		messages: make(map[string][]Message),
	}
}

func (cs *ChatServer) sendMessage(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var msg Message
	err := json.NewDecoder(r.Body).Decode(&msg)
	if err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	msg.SentAt = time.Now()

	cs.messages[msg.To] = append(cs.messages[msg.To], msg)

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(msg)
}

func (cs *ChatServer) getMessages(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "Method not allowed", http.StatusMethodNotAllowed)
		return
	}

	user := r.URL.Query().Get("user")
	if user == "" {
		http.Error(w, "User parameter is required", http.StatusBadRequest)
		return
	}

	var validMessages []Message

	messages := cs.messages[user]
	now := time.Now()
	for _, msg := range messages {
		// Intentional bug: This will panic if msg.Expires is nil
		if now.Sub(msg.SentAt).Seconds() < float64(*msg.Expires) {
			validMessages = append(validMessages, msg)
		}
	}

	cs.messages[user] = nil

	json.NewEncoder(w).Encode(validMessages)
}

func recoveryMiddleware(next http.HandlerFunc, errorLogger *log.Logger) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		defer func() {
			if err := recover(); err != nil {
				// Create a stack trace
				stack := make([]byte, 4096)
				stack = stack[:runtime.Stack(stack, false)]

				// Log the error and stack trace
				errorLogger.Printf("Panic: %v\n%s", err, stack)

				// Return an internal server error to the client
				http.Error(w, "Internal Server Error", http.StatusInternalServerError)
			}
		}()
		next.ServeHTTP(w, r)
	}
}

func main() {
	// Set up error logging to error.log
	errorLog, err := os.OpenFile("error.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to open error log file: %v", err)
	}
	defer errorLog.Close()

	// Set up info logging to info.log
	infoLog, err := os.OpenFile("info.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to open info log file: %v", err)
	}
	defer infoLog.Close()

	// Create loggers
	errorLogger := log.New(errorLog, "ERROR: ", log.Ldate|log.Ltime|log.Lshortfile)
	//infoLogger := log.New(infoLog, "INFO: ", log.Ldate|log.Ltime|log.Lshortfile)

	// Replace the default logger
	log.SetOutput(infoLog)
	log.SetFlags(log.Ldate | log.Ltime | log.Lshortfile)

	chatServer := NewChatServer()

	mainServer := &http.Server{
		Addr:    ":8080",
		Handler: http.DefaultServeMux,
	}

	// Set up routes
	http.HandleFunc("/send", recoveryMiddleware(chatServer.sendMessage, errorLogger))
	http.HandleFunc("/messages", recoveryMiddleware(chatServer.getMessages, errorLogger))

	// Channel to signal shutdown
	shutdown := make(chan struct{})

	// Start the main server
	go func() {
		log.Println("Chat server starting on :8080")
		if err := mainServer.ListenAndServe(); err != http.ErrServerClosed {
			log.Fatalf("Error starting server: %v", err)
		}
	}()

	// Start the shutdown listener
	go func() {
		listener, err := net.Listen("tcp", ":8081")
		if err != nil {
			log.Fatalf("Failed to start shutdown listener: %v", err)
		}
		defer listener.Close()

		log.Println("Shutdown listener started on :8081")
		conn, err := listener.Accept()
		if err != nil {
			log.Printf("Error accepting shutdown connection: %v", err)
			return
		}
		conn.Close()
		log.Println("Shutdown signal received")
		close(shutdown)
	}()

	// Wait for shutdown signal
	<-shutdown

	log.Println("Starting shutdown...")

	// Give outstanding requests a deadline for completion
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	// Shutdown the server
	if err := mainServer.Shutdown(ctx); err != nil {
		log.Printf("Server shutdown error: %v", err)
	}

	log.Println("Server stopped")
}