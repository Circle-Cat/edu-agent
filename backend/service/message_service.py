import base64
import binascii
from typing import List, Optional, Dict, Any

from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from backend.multi_tool_agent.agent import MultimodalAgentSystem


class MessageService:
    """
    A service class to handle message processing and interaction with the MultimodalAgentSystem.
    """

    def __init__(self, agent_system: MultimodalAgentSystem):
        self.agent_system = agent_system
        self.artifact_service = InMemoryArtifactService()

    async def process_message_input(
        self,
        tList: List[types.Part],
    ) -> str:
        """
        Processes message input, formats the data, and calls the agent.

        Args:
            tList: A list of types.Part, can be text or file.
        """
        # Ensure we have at least one part (text or artifact)
        if not tList:
            raise ValueError("At least one input is required")

        query_content = types.Content(role="user", parts=tList)

        # Call the core business logic of the agent system
        agent_response_text = await self.agent_system.send_message(query_content)
        return agent_response_text
