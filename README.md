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

5. Try sending messages without the "expires" field:

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

7. The server listens on port 8080. It also has a shutdown port of 8081. You can shutdown the server with:

    ```
    ./shutdown.sh
    ```

### AI Bug Fixer

Now that you have errors logged to `logs/error.log`, you can run the AI bug fixer to analyze the errors and generate a diff file with the proposed fix. We will be using [Agency Swarm](https://github.com/VRSEN/agency-swarm) for this.

1. Navigate to the `ai-bug-fixer` directory:

    From the `bugged-chat-server` directory:

    ```
    cd ../ai-bug-fixer
    ```

    Or from the root of the project:

    ```
    cd ai-bug-fixer
    ```

2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Run the AI bug fixer agent:

    ```
    python main.py
    ```

4. This will start an interactive terminal. You can prompt the agent with 3 folders:

    ```
    error logs: ../bugged-chat-server/logs
    source code: ../bugged-chat-server
    agent proposed diffs: ./diffs
    ```

    So the prompt should look like this:

    > hello, i have some error logs and i want to fix the bugs that each error represents if possible. the error logs are in this dir: "../bugged-chat-server/logs" you also can access the source code here "../bugged-chat-server" the error logs will often point to a source file name and line of code, so you can look at that area of the source file, and perhaps come up with suggested bug fixes if you see something that could be fixed, or designed better, or made more resilient. the goal is to make the code resilient instead of asking the caller to pass in better data. we should be able to handle anything that is close enough to what we might expect (within reason). please put your proposed diff files in this dir: "./diffs"

5. The AI agent will analyze the error logs and source code, then generate a diff file with the proposed fix if one is found.

    ```
    cat diffs/*
    ```

Super cool right? There are many ways to extend this. You would want to make sure it handles multiple logs files, multiple types of errors, multiple source code files with in a directory structure. Hook it up to prometheus, hook it up to github so that it makes its own branches, PRs, etc. Enjoy!
