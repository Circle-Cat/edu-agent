from fastapi import (
    APIRouter,
    UploadFile,
    File,
    Form,
    Depends,
    HTTPException,
    status,
    Depends,
)
from fastapi.responses import JSONResponse
from typing import Optional, Annotated, List

from google.genai import types

from backend.multi_tool_agent.agent import MultimodalAgentSystem
from backend.utils.dependencies import get_message_service
from backend.service.message_service import MessageService


class APIRoutes:
    """
    This class defines the API routes for message and audio processing.
    """

    def __init__(self):
        self.router = APIRouter(tags=["Messages and Audio"], prefix="/api")
        self.router.post(
            "/send_message",
            summary="Send a text message or upload audio for processing (via agent)",
            response_description="Returns the text response from the agent",
        )(self.send_message)

    async def send_message(
        self,
        service: Annotated[MessageService, Depends(get_message_service)],
        text: Annotated[Optional[str], Form(description="User's text message")] = None,
        audio: Annotated[
            Optional[UploadFile], File(description="User's uploaded audio file")
        ] = None,
    ) -> JSONResponse:
        """
        This API endpoint receives a user's message and passes it to a multimodal agent for processing.
        """
        if text is None and audio is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide at least one of either a text message or an audio file.",
            )

        try:
            agent_response_text = await service.process_message_input(
                text=text, audio=audio
            )
            return JSONResponse(
                content={"agent_response": agent_response_text},
                status_code=status.HTTP_200_OK,
            )
        except Exception as e:
            print(f"Failed to process message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process message: {str(e)}",
            )
