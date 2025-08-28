# Multimodal Agent Service with FastAPI

This project is a FastAPI-based service that demonstrates how to build a multimodal application using the Google Agent Development Kit (ADK). The service is capable of receiving and processing both text and audio inputs from a user and routing them to an intelligent agent.

The core of the application uses a dynamic agent system that can automatically select the appropriate large language model (LLM) based on the input type. For example, it will use a text-only model for text queries and a multimodal model for audio queries.

## Features

- **Multimodal Input**: Accepts both text and audio files via a single API endpoint.
- **Dynamic Agent**: A custom callback function dynamically switches the LLM model based on whether the user's input contains audio or text.
- **Session Management**: A custom middleware handles session IDs, allowing the agent to maintain conversational context across multiple requests from the same user.
- **Dependency Injection**: The application uses FastAPI's dependency injection system to manage service and agent instances per session.
- **Interactive Documentation**: The FastAPI framework provides automatic interactive API documentation via `/docs`.

## Setup

### Prerequisites

- Python 3.8+
- An API key for the Google ADK. You will need to configure your environment variables with this key.

### Installation

1. Clone this repository to your local machine.
2. Navigate to the project directory.
3. Create a virtual environment and activate it (optional but recommended).
4. Install the required dependencies from your `requirements.txt` file:

```bash
pip install -r backend/requirements.txt
```
5. Export environments:
```bash
export GOOGLE_API_KEY="your_api_key_here"
export GOOGLE_GENAI_USE_VERTEXAI=False
```

### Running the Application

Once you have completed the setup, you can start the FastAPI server using uvicorn:

```bash
uvicorn backend.main:app --host 0.0.0.0 --reload
```

This will run the application in development mode with live reloading. You can then access the interactive API documentation at: `http://{your-workspace-ip}:8000/docs`

### Running the adk web

```bash
cd backend
adk web --host 0.0.0.0 --port 8000
```

### Code Formatting with Black

This project uses Black to enforce a consistent Python code style.
1. Install Black

```bash
sudo apt update
sudo apt install black
```

2. Format Your Code
To automatically format all Python files in the project:
```bash
black .
```