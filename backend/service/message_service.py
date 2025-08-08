from typing import List, Optional
from fastapi import UploadFile
from google.genai import types
from backend.multi_tool_agent.agent import MultimodalAgentSystem


class MessageService:
    """
    A service class to handle message processing and interaction with the MultimodalAgentSystem.
    """

    def __init__(self, agent_system: MultimodalAgentSystem):
        self.agent_system = agent_system

    async def process_message_input(
        self, text: Optional[str], audio: Optional[UploadFile]
    ) -> str:
        """
        Processes message input, formats the data, and calls the agent.
        """
        parts: List[types.Part] = []

        if text:
            print(f"Service received text message: {text}")
            parts.append(types.Part(text=text))

        if audio:
            print(
                f"Service received audio file: {audio.filename}, Type: {audio.content_type}"
            )
            audio_content = await audio.read()
            parts.append(
                types.Part.from_bytes(mime_type=audio.content_type, data=audio_content)
            )

        query_content = types.Content(role="user", parts=parts)

        # Call the core business logic of the agent system
        agent_response_text = await self.agent_system.send_message(query_content)
        return agent_response_text
