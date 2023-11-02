"""Backend server for Ricochet game."""

from fastapi import FastAPI

app = FastAPI()


# TODO(BECATRUE): This will be removed after test.
@app.get("/")
async def root():
    """Temporary function for test."""
    return "Hello, world!"
