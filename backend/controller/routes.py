from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from typing import Optional, Annotated

from google.genai import types

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
        text_context: Annotated[
            Optional[str], Body(description="User's text message")
        ] = None,
        mime_type: Annotated[
            Optional[str], Body(description="Base64 encoded data type")
        ] = None,
        data: Annotated[
            Optional[str], Body(description="Base64 encoded audio or video data")
        ] = None,
    ) -> JSONResponse:
        """
        Receives a base64-encoded data from request body and passes it
        to a multimodal agent for processing.
        """
        try:
            agent_response_text = await service.process_message_input(
                text=text_context,
                base64_encoded_data=data,
                mime_type=mime_type,
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
