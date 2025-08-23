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
        text: Optional[str],
        artifact_info: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Processes message input with artifact information, formats the data, and calls the agent.

        Args:
            text: Optional text message from user
            artifact_info: Dictionary containing artifact information with keys:
                - 'artifact_id': The ID of the stored artifact
                - 'mime_type': MIME type of the artifact
                - 'description': Optional description of the artifact
        """
        parts: List[types.Part] = []

        # Add text part if provided
        if text:
            parts.append(types.Part(text=text))

        # Process artifact if provided
        if artifact_info:
            try:
                # Extract artifact information
                artifact_id = artifact_info.get("artifact_id")
                mime_type = artifact_info.get("mime_type")
                description = artifact_info.get("description", "")

                if not artifact_id or not mime_type:
                    raise ValueError(
                        "artifact_id and mime_type are required in artifact_info"
                    )

                # Get the artifact from the artifact service
                artifact = await self.artifact_service.get_artifact(artifact_id)
                if not artifact:
                    raise ValueError(f"Artifact with ID {artifact_id} not found")

                # Create Part from artifact
                if hasattr(artifact, "data"):
                    # If artifact has data property, use it directly
                    parts.append(
                        types.Part.from_bytes(mime_type=mime_type, data=artifact.data)
                    )
                elif hasattr(artifact, "content"):
                    # If artifact has content property, use it
                    parts.append(
                        types.Part.from_bytes(
                            mime_type=mime_type, data=artifact.content
                        )
                    )
                else:
                    # Fallback: try to get artifact as bytes
                    artifact_bytes = bytes(artifact)
                    parts.append(
                        types.Part.from_bytes(mime_type=mime_type, data=artifact_bytes)
                    )

                # Add description as additional context if provided
                if description:
                    parts.append(types.Part(text=f"File description: {description}"))

            except Exception as e:
                raise RuntimeError(f"Error processing artifact: {e}")

        # Ensure we have at least one part (text or artifact)
        if not parts:
            raise ValueError("At least one input (text or artifact) is required")

        query_content = types.Content(role="user", parts=parts)

        # Call the core business logic of the agent system
        agent_response_text = await self.agent_system.send_message(query_content)
        return agent_response_text
