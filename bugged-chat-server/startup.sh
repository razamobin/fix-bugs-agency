#!/bin/bash

# Remove the old binary if it exists
rm -f chat_server

# Build the Go application
go build -o chat_server main.go

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Build failed. Please check the errors above."
    exit 1
fi

# Start the server
./chat_server &

echo "Server started. PID: $!"