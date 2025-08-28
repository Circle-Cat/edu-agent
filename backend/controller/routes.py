from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.responses import JSONResponse
from typing import List

from google.genai.types import Part

from backend.utils.dependencies import get_message_service
from backend.service.message_service import MessageService


class APIRoutes:
    """
    This class defines the API routes for text message, image, and audio processing.
    """

    def __init__(self):
        self.router = APIRouter(tags=["Messages, Image, and Audio"], prefix="/api")
        self.router.post(
            "/send_message",
            summary="Send a list of parts (text or file) to the agent",
            response_description="Returns the text response from the agent",
        )(self.send_message)

    async def send_message(
        self,
        service: MessageService = Depends(get_message_service),
        tList: List[Part] = Body(
            ...,
            description="A list of parts, where each part can be text or a file.",
            examples=[
                {"text": "Hello, what is it?"},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": "base64-encoded-image-data",
                    }
                },
                {
                    "inline_data": {
                        "mime_type": "audio/mpeg",
                        "data": "base64-encoded-audio-data",
                    }
                },
                {
                    "inline_data": {
                        "mime_type": "video/mp4",
                        "data": "base64-encoded-video-data",
                    }
                },
            ],
        ),
    ) -> JSONResponse:
        """
        Receives a list of parts (tList), where each part can be text or a file.
        The file is represented as a dictionary with 'mime_type' and 'data' (base64 encoded).
        The list is passed to the agent for processing.
        """
        try:
            agent_response_text = await service.process_message_input(tList=tList)
            response_payload = {"agent_response": agent_response_text}

            return JSONResponse(
                content=response_payload, status_code=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Failed to process message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process message: {str(e)}",
            )
