"""Main FastAPI application assembly."""

import logging
import sys

from fastapi import FastAPI

from ghost_brain.__about__ import __version__
from ghost_brain.handlers.post_call import router as post_call_router
from ghost_brain.handlers.websocket import router as websocket_router

# Configure global logging for the application
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s:\t  %(name)s - %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ghost Brain",
    description="Voice-interviewer bot and post-call processor.",
    version=__version__,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Provide a health check endpoint for load balancers and Cloud Run."""
    return {"status": "ok"}


app.include_router(websocket_router)
app.include_router(post_call_router)
