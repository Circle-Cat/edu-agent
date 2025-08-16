import base64
import binascii
from typing import List, Optional

from google.genai import types
from backend.multi_tool_agent.agent import MultimodalAgentSystem


class MessageService:
    """
    A service class to handle message processing and interaction with the MultimodalAgentSystem.
    """

    def __init__(self, agent_system: MultimodalAgentSystem):
        self.agent_system = agent_system

    async def process_message_input(
        self,
        text: Optional[str],
        base64_encoded_data: Optional[str],
        mime_type: Optional[str],
    ) -> str:
        """
        Processes message input, formats the data, and calls the agent.
        """
        parts: List[types.Part] = []

        if base64_encoded_data and not mime_type:
            raise ValueError(
                "MIME type is required when base64 encoded data is provided."
            )
        elif mime_type and not base64_encoded_data:
            raise ValueError(
                "Base64 encoded data is required when MIME type is provided."
            )

        if base64_encoded_data and mime_type:
            try:
                parts.append(
                    types.Part.from_bytes(
                        mime_type=mime_type, data=base64.b64decode(base64_encoded_data)
                    )
                )
            except binascii.Error as e:
                raise ValueError(f"Invalid Base64 string provided: {e}")
            except Exception as e:
                raise RuntimeError(f"An unexpected error occurred: {e}")

        if text:
            parts.append(types.Part(text=text))

        query_content = types.Content(role="user", parts=parts)

        # Call the core business logic of the agent system
        agent_response_text = await self.agent_system.send_message(query_content)
        return agent_response_text
