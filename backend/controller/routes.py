from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from fastapi.responses import JSONResponse
from typing import Optional

from google.adk.artifacts import InMemoryArtifactService
from google.genai import types

from backend.utils.dependencies import get_message_service
from backend.service.message_service import MessageService


artifact_service = InMemoryArtifactService()


class APIRoutes:
    """
    This class defines the API routes for text message, image, and audio processing.
    """

    def __init__(self):
        self.router = APIRouter(tags=["Messages, Image, and Audio"], prefix="/api")
        self.router.post(
            "/send_message",
            summary="Send text and optional file (image/audio), store file in InMemoryArtifactService",
            response_description="Returns the text response from the agent",
        )(self.send_message)

    async def send_message(
        self,
        service: MessageService = Depends(get_message_service),
        text_context: Optional[str] = Form(None, description="User text message"),
        file: Optional[UploadFile] = File(
            None, description="Optional image (jpg/png/svg/…) or audio file"
        ),
    ) -> JSONResponse:
        """
        Receives a text message and optional file (image/audio),
        stores the file in InMemoryArtifactService,
        and passes the text and file to a multimodal agent for processing.
        """
        try:
            artifact_info = None

            if file:
                content = await file.read()
                mime_type = file.content_type or "application/octet-stream"
                part = types.Part.from_bytes(content, mime_type)

                filename = file.filename or "uploaded_file"
                version = await artifact_service.save_artifact(
                    filename=filename, part=part
                )

                # Update artifact_info structure to match MessageService expected format
                artifact_info = {
                    "artifact_id": version,
                    "mime_type": mime_type,
                    "description": f"Uploaded file: {filename}",
                    "filename": filename,
                    "version": version,
                }

            agent_response_text = await service.process_message_input(
                text=text_context,
                artifact_info=artifact_info,
            )

            response_payload = {"agent_response": agent_response_text}
            if artifact_info:
                response_payload["artifact_info"] = artifact_info

            return JSONResponse(
                content=response_payload, status_code=status.HTTP_200_OK
            )

        except Exception as e:
            print(f"Failed to process message: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process message: {str(e)}",
            )
