import base64
import binascii
from typing import List, Optional, Dict, Any

from google.adk.runners import Runner
from google.genai import types


class MessageService:
    """
    A service class to handle message processing and interaction with the agent.
    """

    def __init__(self, runner: Runner, user_id: str, session_id: str):
        self.runner = runner
        self.user_id = user_id
        self.session_id = session_id

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
        agent_response_text = await self.run_agent(
            runner=self.runner,
            user_id=self.user_id,
            session_id=self.session_id,
            query_content=query_content,
        )

        return agent_response_text

    async def run_agent(
        self,
        runner: Runner,
        user_id: str,
        session_id: str,
        query_content: types.Content,
    ) -> str:
        """
        Sends a Content object to the agent and returns the final response text.
        """
        final_response_text = "Agent did not produce a final response."
        async for event in runner.run_async(
            user_id=user_id, session_id=session_id, new_message=query_content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                break
        return final_response_text
