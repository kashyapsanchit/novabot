from pydantic import BaseModel
from typing import TypedDict, Optional


class AgentState(TypedDict):
    session_id: str
    message: str
    response: str
    image: str