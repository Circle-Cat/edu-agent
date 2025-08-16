import os
import logging
from typing import Optional

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

logging.basicConfig(level=os.getenv("LOG_LEVEL", "DEBUG"))


class MultimodalAgentSystem:
    """
    A multimodal agent system that dynamically selects the LLM model based on the input type (text or audio).
    """

    def __init__(self, user_id: str, session_id: str, app_name: str = "multimodal_app"):
        # --- Model constants ---
        self.MODEL = "gemini-2.5-flash-lite"

        # --- Session and runner parameters ---
        self.app_name = app_name
        self.user_id = user_id
        self.session_id = session_id

        # --- Initialize session service ---
        self.session_service = InMemorySessionService()

        # --- Initialize tools list ---
        # self.tools = [
        #    WeatherTool() # Add tool instances to the list
        #    # Other tools like CalculatorTool(), SearchTool() can be added here
        # ]

        # --- Define the agent ---
        self.agent = Agent(
            name="multimodal_input_agent",
            model=self.MODEL,  # Initial model
            description="An agent that can handle multimodal input (text, audio or video).",
            instruction="You are a helpful assistant. Respond to user queries. If you receive audio or video, acknowledge it and try to answer based on your understanding. If you receive text, answer directly. Your final output should always be text.",
            # tools=self.tools # <--- Pass the tools list here
        )
        logging.info(f"Agent '{self.agent.name}' initialized.")

        # --- Initialize the runner (actual session will be created in the async setup method) ---
        self.runner: Optional[Runner] = None
        self._is_setup = False  # Flag to check if async setup is complete

    async def setup(self):
        """
        Asynchronously sets up the session and initializes the runner.
        """
        if self._is_setup:
            logging.info("System is already set up.")
            return

        session = await self.session_service.get_session(
            app_name=self.app_name, user_id=self.user_id, session_id=self.session_id
        )
        if not session:
            session = await self.session_service.create_session(
                app_name=self.app_name, user_id=self.user_id, session_id=self.session_id
            )
            logging.debug(
                f"Session created: App='{self.app_name}', User='{self.user_id}', Session='{self.session_id}'"
            )
        else:
            logging.debug(
                f"Retrieved existing session: App='{self.app_name}', User='{self.user_id}', Session='{self.session_id}'"
            )

        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )
        logging.debug(f"Runner created for agent '{self.runner.agent.name}'.")
        self._is_setup = True

    async def send_message(self, query_content: types.Content) -> str:
        """
        Sends a Content object to the agent and returns the final response text.
        """
        if not self._is_setup or not self.runner:
            logging.debug(
                "System is not fully set up. Please call the .setup() method first."
            )
            return "Error: Agent system not initialized."

        final_response_text = "Agent did not produce a final response."

        async for event in self.runner.run_async(
            user_id=self.user_id, session_id=self.session_id, new_message=query_content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                break

        return final_response_text
