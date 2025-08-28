import os
import logging
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.genai import types

logging.basicConfig(level=os.getenv("LOG_LEVEL", "DEBUG"))

# --- Model constants ---
MODEL = "gemini-2.5-flash-lite"

# --- Initialize tools list ---
# tools = [
#    WeatherTool() # Add tool instances to the list
#    # Other tools like CalculatorTool(), SearchTool() can be added here
# ]

# --- Define the agent ---
root_agent = Agent(
    name="multimodal_input_agent",
    model=MODEL,  # Initial model
    description="An agent that can handle multimodal input (text, audio or video).",
    instruction="You are a helpful assistant. Respond to user queries. If you receive audio or video, acknowledge it and try to answer based on your understanding. If you receive text, answer directly. Your final output should always be text.",
    # tools=tools # <--- Pass the tools list here
)
logging.info(f"Agent '{root_agent.name}' initialized.")
