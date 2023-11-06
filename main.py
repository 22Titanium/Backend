"""Backend server for Ricochet game."""

import dataclasses
import logging
from fastapi import FastAPI

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class RoomInfo:
    """Container of room information.
    
    Fields:
        name: The room name.
        user_id: The room owner user ID.
    """
    name: str
    user_id: int


user_list: list[str] = []
room_list: list[RoomInfo] = []

app = FastAPI()

@app.get("/user/me/")
async def create_user(name: str) -> int:
    """Creates a new user with the given name.
    
    Args:
        name: The user name.

    Returns:
        The created user ID.
    """
    user_list.append(name)
    return len(user_list) - 1
