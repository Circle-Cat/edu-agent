from typing import Dict
from fastapi import Request, Depends, Header
from typing import Annotated
from backend.multi_tool_agent.agent import MultimodalAgentSystem
from backend.service.message_service import MessageService

_user_agent_systems: Dict[str, MultimodalAgentSystem] = {}


async def get_agent_system_for_user(
    user_id: Annotated[str, Header(description="The user's unique identifier.")],
    session_id: Annotated[str, Header(description="The session's unique identifier.")],
) -> MultimodalAgentSystem:
    """
    Dependency injection function that provides a MultimodalAgentSystem instance for each session.
    """
    if session_id not in _user_agent_systems:
        print(f"Creating a new agent system instance for session '{session_id}'.")

        agent_system = MultimodalAgentSystem(user_id=user_id, session_id=session_id)

        await agent_system.setup()
        _user_agent_systems[session_id] = agent_system

    return _user_agent_systems[session_id]


def get_message_service(
    agent_system: MultimodalAgentSystem = Depends(get_agent_system_for_user),
) -> MessageService:
    """
    Dependency injection function that provides a MessageService instance.
    It depends on get_agent_system_for_user.
    """
    return MessageService(agent_system=agent_system)
