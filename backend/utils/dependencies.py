from typing import Dict
from fastapi import Request, HTTPException, status, Depends
from backend.multi_tool_agent.agent import MultimodalAgentSystem
from backend.service.message_service import MessageService

_user_agent_systems: Dict[str, MultimodalAgentSystem] = {}


async def get_agent_system_for_user(request: Request) -> MultimodalAgentSystem:
    """
    Dependency injection function that provides a MultimodalAgentSystem instance for each session.
    """
    user_id = request.state.user_id
    session_id = request.state.session_id

    if not session_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Session ID not found.",
        )

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
