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


@app.post("/room/")
async def create_room(name: str, user_id: int) -> int:
    """Creates a new room with the given name.
    
    Args:
        See RoomInfo.

    Returns:
        The created room ID, or -1 if failed.
    """
    if user_id not in user_list:
        logger.exception("An unregistered user (ID: %d) tries to create a room", user_id)
        return -1
    room_list.append(RoomInfo(name=name, user_id=user_id))
    return len(room_list) - 1
