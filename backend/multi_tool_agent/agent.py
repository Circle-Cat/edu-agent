import os
import asyncio
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from typing import Optional, List, Dict, Any

import warnings

warnings.filterwarnings("ignore")
import logging

logging.basicConfig(level=logging.ERROR)


class MultimodalAgentSystem:
    """
    A multimodal agent system that dynamically selects the LLM model based on the input type (text or audio).
    """

    def __init__(self, user_id: str, session_id: str, app_name: str = "multimodal_app"):
        # --- Model constants ---
        self.MODEL_MULTIMODAL_AUDIO = "gemini-2.5-flash-lite"
        self.MODEL_TEXT_ONLY = "gemini-2.0-flash-lite"

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
        # The initial model is set to the text-only model, but it will be dynamically changed via the callback
        self.agent = Agent(
            name="multimodal_input_agent",
            model=self.MODEL_TEXT_ONLY,  # Initial model, to be overridden in the callback
            description="An agent that can handle multimodal input (text or audio) and use different LLMs based on the input type.",
            instruction="You are a helpful assistant. Respond to user queries. If you receive audio, acknowledge it and try to answer based on your understanding. If you receive text, answer directly. Your final output should always be text.",
            before_model_callback=self._dynamic_llm_selector_callback,  # Associate the dynamic model selection callback
            # tools=self.tools # <--- Pass the tools list here
        )
        print(f"Agent '{self.agent.name}' initialized.")

        # --- Initialize the runner (actual session will be created in the async setup method) ---
        self.runner: Optional[Runner] = None
        self._is_setup = False  # Flag to check if async setup is complete

    async def setup(self):
        """
        Asynchronously sets up the session and initializes the runner.
        """
        if self._is_setup:
            print("System is already set up.")
            return

        session = await self.session_service.get_session(
            app_name=self.app_name, user_id=self.user_id, session_id=self.session_id
        )
        if not session:
            session = await self.session_service.create_session(
                app_name=self.app_name, user_id=self.user_id, session_id=self.session_id
            )
            print(
                f"Session created: App='{self.app_name}', User='{self.user_id}', Session='{self.session_id}'"
            )
        else:
            print(
                f"Retrieved existing session: App='{self.app_name}', User='{self.user_id}', Session='{self.session_id}'"
            )

        self.runner = Runner(
            agent=self.agent,
            app_name=self.app_name,
            session_service=self.session_service,
        )
        print(f"Runner created for agent '{self.runner.agent.name}'.")
        self._is_setup = True

    def _dynamic_llm_selector_callback(
        self, callback_context: "CallbackContext", llm_request: "LlmRequest"
    ) -> Optional[None]:
        """
        An internal callback function that checks if the latest user input contains audio.
        If it does, it switches the LLM model to the multimodal model; otherwise, it uses the text-only model.
        """
        agent_name = callback_context.agent_name
        print(
            f"--- Callback: _dynamic_llm_selector_callback is running for agent: {agent_name} ---"
        )

        last_user_content = None
        if llm_request.contents:
            for content in reversed(llm_request.contents):
                if content.role == "user":
                    last_user_content = content
                    break

        if last_user_content and last_user_content.parts:
            is_audio_input = False
            for part in last_user_content.parts:
                if (
                    hasattr(part, "inline_data")
                    and part.inline_data
                    and hasattr(part.inline_data, "mime_type")
                    and part.inline_data.mime_type
                    and part.inline_data.mime_type.startswith("audio/")
                ):
                    is_audio_input = True
                    break

            if is_audio_input:
                print("llm_request")
                print(llm_request)
                print("---")
                llm_request.model = self.MODEL_MULTIMODAL_AUDIO
                print(
                    f"--- Callback: Audio input detected. Model switched to: {self.MODEL_MULTIMODAL_AUDIO} ---"
                )
            else:
                llm_request.model = self.MODEL_TEXT_ONLY
                print(
                    f"--- Callback: Text input detected. Model switched to: {self.MODEL_TEXT_ONLY} ---"
                )
        else:
            llm_request.model = self.MODEL_TEXT_ONLY
            print(
                f"--- Callback: No clear input type detected. Defaulting to model: {self.MODEL_TEXT_ONLY} ---"
            )

        return None

    async def send_message(self, query_content: types.Content) -> str:
        """
        Sends a Content object (which can contain text or audio) to the agent and returns the final response text.
        """
        if not self._is_setup or not self.runner:
            print("System is not fully set up. Please call the .setup() method first.")
            return "Error: Agent system not initialized."

        input_type_display = "text/plain"
        print("query_content: ")
        print(query_content)
        print("___")
        if query_content.parts:
            first_part = query_content.parts[0]
            print("first_part: ")
            print(first_part)

            if (
                hasattr(first_part, "inline_data")
                and first_part.inline_data
                and first_part.inline_data.mime_type
            ):
                input_type_display = first_part.inline_data.mime_type
            elif hasattr(first_part, "text") and first_part.text:
                input_type_display = "text/plain"
            else:
                input_type_display = "unknown/mixed"

        print(f"\n>>> User query (Content type: {input_type_display}):")
        if query_content.parts:
            for part in query_content.parts:
                if hasattr(part, "text") and part.text:
                    print(f"    Text: '{part.text[:50]}...'")
                elif hasattr(part, "inline_data") and part.inline_data:
                    print(
                        f"    Binary data MIME type: '{part.inline_data.mime_type}' (data length: {len(part.inline_data.data)} bytes)"
                    )

        final_response_text = "Agent did not produce a final response."

        async for event in self.runner.run_async(
            user_id=self.user_id, session_id=self.session_id, new_message=query_content
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    final_response_text = event.content.parts[0].text
                break
        print(f"<<< Agent response: {final_response_text}")
        return final_response_text
