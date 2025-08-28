from typing import Dict, Annotated
from fastapi import Depends, Header

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts import InMemoryArtifactService

from backend.multi_tool_agent.agent import root_agent
from backend.service.message_service import MessageService

_user_runners: Dict[str, Runner] = {}
_session_services: Dict[str, InMemorySessionService] = {}


async def get_runner_for_user(
    user_id: Annotated[str, Header(description="The user's unique identifier.")],
    session_id: Annotated[str, Header(description="The session's unique identifier.")],
    app_name: str = "multimodal_app",
) -> Runner:
    """
    Dependency injection function that provides a Runner instance for each session.
    """
    if session_id not in _user_runners:
        print(f"Creating a new runner instance for session '{session_id}'.")

        session_service = InMemorySessionService()
        session = await session_service.get_session(
            app_name=app_name, user_id=user_id, session_id=session_id
        )
        if not session:
            await session_service.create_session(
                app_name=app_name, user_id=user_id, session_id=session_id
            )

        artifact_service = InMemoryArtifactService()
        runner = Runner(
            agent=root_agent,
            app_name=app_name,
            session_service=session_service,
            artifact_service=artifact_service,
        )
        _session_services[session_id] = session_service
        _user_runners[session_id] = runner

    return _user_runners[session_id]


def get_message_service(
    user_id: Annotated[str, Header(description="The user's unique identifier.")],
    session_id: Annotated[str, Header(description="The session's unique identifier.")],
    runner: Runner = Depends(get_runner_for_user),
) -> MessageService:
    """
    Dependency injection function that provides a MessageService instance.
    It depends on get_runner_for_user.
    """
    return MessageService(runner=runner, user_id=user_id, session_id=session_id)
