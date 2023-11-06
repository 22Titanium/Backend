"""Backend server for Ricochet game."""

from fastapi import FastAPI

user_list: list[str] = []

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
