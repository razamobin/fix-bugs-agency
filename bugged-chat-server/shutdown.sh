#!/bin/bash

# Function to check if the server is listening on port 8081
is_server_listening() {
    nc -z localhost 8081 >/dev/null 2>&1
    return $?
}

# Check if the server is listening
if ! is_server_listening; then
    echo "No server running on port 8081. Nothing to do."
    exit 0
fi

echo "Server detected. Sending shutdown signal..."
nc -z localhost 8081

echo "Shutdown signal sent. Waiting for server to stop..."
sleep 2

if is_server_listening; then
    echo "Server is still running after 5 seconds. This is unexpected."
else
    echo "Server stopped gracefully."
fi
