"""Backend server for Ricochet game."""

import asyncio
import dataclasses
import enum
import logging

import websockets
from fastapi import FastAPI, WebSocket

logger = logging.getLogger(__name__)

room_list_modified = asyncio.Event()

@dataclasses.dataclass
class RoomInfo:
    """Container of room information.
    
    Fields:
        name: The room name.
        owner_id: The room owner user ID.
        player_list: The player list with each user ID.
        status: The current room status.
    """

    class Status(enum.IntEnum):
        """Room status."""
        WAITING = 0
        RUNNING = 1

    name: str
    owner_id: int
    player_list: list[int] = dataclasses.field(default_factory=list)
    status: Status = Status.WAITING

    def __post_init__(self):
        """Overridden.
        
        It adds the owner to the player list.
        """
        self.player_list.append(self.owner_id)


user_list: list[str] = []
room_list: list[RoomInfo] = []

app = FastAPI()

def notify_modified(modified: asyncio.Event):
    """Sets and clears the modified event.
    
    All the coroutines that are waiting for the modified event will be awakened.

    Args:
        modified: The event to notify a modification.
    """
    modified.set()
    modified.clear()


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
    if user_id < 0 or user_id >= len(user_list):
        logger.exception("An unregistered user (ID: %d) tries to create a room.", user_id)
        return -1
    room_list.append(RoomInfo(name=name, owner_id=user_id))
    notify_modified(room_list_modified)
    return len(room_list) - 1


@app.websocket("/room/list/")
async def get_room_list(websocket: WebSocket):
    """Sends the room list through a web socket.
    
    The room list is a list with each room info. An info is a dictionary with four keys:
      "name": The room name.
      "owner": The room owner name.
      "num_players": The number of players of the room.
      "status": The room status. See RoomInfo.Status.
    
    Args:
        websocket: The web socket object. 
    """
    await websocket.accept()
    try:
        while True:
            await room_list_modified.wait()
            data = [{
                "name": room.name,
                "owner": user_list[room.owner_id],
                "num_players": len(room.player_list),
                "status": room.status.value
            } for room in room_list]
            await websocket.send_json(data)
    except websockets.exceptions.ConnectionClosedError:
        logger.info("The connection for sending the room list is closed.")
    except websockets.exceptions.WebSocketException:
        logger.exception("Failed to send the room list.")


@app.post("/room/enter/")
async def enter_room(room_id: int, user_id: int) -> bool:
    """Enters a specific room.
    
    Args:
        room_id: The room ID.
        user_id: The user ID.

    Returns:
        False if either the room ID or the user ID is invalid or the game is already running.
        Otherwise, True.
    """
    if room_id < 0 or room_id >= len(room_list):
        logger.exception("There is no room (ID: %d).", room_id)
        return False
    if user_id < 0 or user_id >= len(user_list):
        logger.exception("An unregistered user (ID: %d) tries to enter a room.", user_id)
        return False
    room = room_list[room_id]
    if room.status == RoomInfo.Status.RUNNING:
        logger.exception("The room (ID: %d) is already running.", room_id)
        return False
    return True
