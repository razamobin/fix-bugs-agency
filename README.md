# Fix Bugs Agency

This project demonstrates an AI-powered bug fixing system using two components: a bugged chat server and an AI bug fixer.

## Project Overview

1. **Bugged Chat Server**: A demo chat server with an intentional nil dereference bug. It works for simple cases but breaks when clients try to read a message that is missing the "expires" field. Errors are logged to an error log file.

2. **AI Bug Fixer**: An AI agent that analyzes error logs and source code to identify and fix bugs. When a fix is found, it generates a diff file on disk for the to user review.

## Getting Started

### Bugged Chat Server

1. Navigate to the `bugged-chat-server` directory:

    ```
    cd bugged-chat-server
    ```

2. Download dependencies:

    ```
    go mod download
    ```

3. Run the server:

    ```
    ./startup.sh
    ```

4. Use curl commands to interact with the server:

    To send a message:

    ```
    curl -X POST http://localhost:8080/send \
      -H "Content-Type: application/json" \
      -d '{
        "from": "alice",
        "to": "raza",
        "content": "omg, AI agents are so cool right?",
        "expires": 20
      }'
    ```

    To get messages for a user:

    ```
    curl -X GET http://localhost:8080/messages?user=raza
    ```

5. Try sending messages without the "expires" field to trigger the bug:

    ```
    curl -X POST http://localhost:8080/send \
      -H "Content-Type: application/json" \
      -d '{
        "from": "alice",
        "to": "raza",
        "content": "no expires on this one, can you handle it?"
      }'
    ```

    Try getting messages and you'll see the error:

    ```
    curl -X GET http://localhost:8080/messages?user=raza
    ```

6. Errors are logged to `logs/error.log`:

    ```
    cat logs/error.log
    ```

7. The server listens on port 8080. You can stop the server with:

    ```
    ./shutdown.sh
    ```

### AI Bug Fixer

1. Navigate to the `ai-bug-fixer` directory:

    ```
    cd ai-bug-fixer
    ```

2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Run the AI bug fixer:

    ```
    python main.py
    ```

4. The AI agent will analyze the error logs and source code, then generate a diff file with the proposed fix if one is found.

## Testing the System

1. Start the bugged chat server:

    ```
    cd bugged-chat-server
    ./startup.sh
    ```
