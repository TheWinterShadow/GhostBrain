"""Webhooks and events for post-call processing."""

import logging
from typing import Any

from fastapi import APIRouter, Request, Response

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/events/post-call")
async def post_call_handler(request: Request) -> Response:
    """Handle post-call processing triggered by Eventarc/GCS."""
    logger.info("Received post-call event from GCS/Eventarc")

    # CloudEvents from Eventarc provide metadata in HTTP headers
    event_type: str = request.headers.get("ce-type", "Unknown")
    file_name: str = request.headers.get("ce-subject", "Unknown")
    bucket_name: str = request.headers.get("ce-source", "Unknown")

    logger.info("Event Type: %s", event_type)
    logger.info("Bucket Source: %s", bucket_name)
    logger.info("File Subject: %s", file_name)

    if not file_name or file_name == "Unknown":
        logger.warning("No file subject found in headers, unable to process.")
        return Response(status_code=400, content="Missing ce-subject header")

    try:
        payload: dict[str, Any] = await request.json()
        logger.info("Payload received: %s", payload)
    except Exception as e:
        logger.warning("No JSON payload or error parsing: %s", e)

    # TODO: Implement actual business logic here
    # 1. Download file_name from bucket_name
    # 2. Extract transcript
    # 3. Call LLM for summarization / follow-ups
    # 4. Save results back or trigger external system

    return Response(status_code=200, content="Post-call logic executed successfully")
