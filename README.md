# Fix Bugs Agency

This project demonstrates an AI-powered bug fixing system using two components: a bugged chat server and an AI bug fixer.

## Project Overview

1. **Bugged Chat Server**: A demo chat server with an intentional nil dereference bug. It works for simple cases but breaks when clients don't send an expire value for a message. Errors are logged to an error log file.

2. **AI Bug Fixer**: An AI agent that analyzes error logs and source code to identify and fix bugs. When a fix is found, it generates a diff file for user review.

## Getting Started

### Bugged Chat Server

1. Navigate to the `bugged-chat-server` directory:

    ```
    cd bugged-chat-server
    ```

2. Run the server:

    ```
    go run main.go
    ```

3. The server will start and listen for incoming connections. Errors will be logged to `error.log`.

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

1. Start the bugged chat server.
2. Use a chat client to send messages, including some without expire values to trigger the bug.
3. Run the AI bug fixer to analyze and fix the bug.
4. Review the generated diff file to see the proposed fix.
