import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import MutableHeaders
from typing import Optional


def get_user_id_from_request(request: Request) -> str:
    """
    This is a placeholder function to get a user ID from the request.
    In a production application, this would typically be retrieved from a JWT or other authentication method.
    """
    # WARNING: This is an example only! Do not use a hardcoded ID in a production environment.
    # This logic should be replaced with a real authentication process.
    return "demo_user"


class SessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to manage session IDs for API requests.

    It checks for an 'X-Session-ID' header in the incoming request. If one is not
    present, it generates a new UUID and attaches it to the request state and the
    response header.
    """

    async def dispatch(self, request: Request, call_next):
        # 1. Execute before the request reaches the API endpoint
        user_id = get_user_id_from_request(request)
        session_id = request.headers.get("X-Session-ID")

        if not session_id:
            # If the request doesn't have a session ID, generate a new one
            session_id = str(uuid.uuid4())
            print(f"Generated new session_id for a new request: {session_id}")

        # 2. Store user_id and session_id in the request state
        request.state.user_id = user_id
        request.state.session_id = session_id

        # 3. Continue processing the request by calling the next middleware or API endpoint
        response = await call_next(request)

        # 4. Execute before sending the response back to the client
        # If a new session ID was generated, add it to the response header
        if session_id and not request.headers.get("X-Session-ID"):
            response.headers["X-Session-ID"] = session_id

        return response
