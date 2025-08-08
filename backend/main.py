import os
from fastapi import FastAPI
from backend.controller.routes import APIRoutes
from backend.multi_tool_agent.agent import MultimodalAgentSystem
from backend.utils.middleware import SessionMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(
    title="Multimodal Message Processing Service (with Agent)",
    description="A FastAPI service that receives text or audio messages and processes them through a Google ADK agent.",
    version="1.0.0",
)

# Add the custom session middleware
app.add_middleware(SessionMiddleware)

# Include the API routes
api_routes_instance = APIRoutes()
app.include_router(api_routes_instance.router)


@app.get("/", summary="Service Health Check")
async def read_root():
    """
    Checks the health of the service.
    """
    return {"status": "ok", "message": "Service is running."}


# To run the application, use the command: uvicorn main:app --reload
# Then, visit http://127.0.0.1:8000/docs to see the interactive documentation.
