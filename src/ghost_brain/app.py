"""FastAPI app and WebSocket endpoint for the Ghost Brain voice bot."""

import logging

from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect

from ghost_brain.__about__ import __version__
from ghost_brain.config import get_settings
from ghost_brain.core.pipeline import build_pipeline
from ghost_brain.core.runner import register_handlers, run_pipeline
from ghost_brain.transport.twilio import create_transport, create_twilio_serializer

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ghost Brain",
    description="Voice-interviewer bot via Twilio WebSocket and Pipecat.",
    version=__version__,
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Health check for load balancers and Cloud Run."""
    return {"status": "ok"}


@app.post("/incoming-call")
async def incoming_call(request: Request) -> Response:
    """Handle incoming call and return TwiML."""
    host = request.headers.get("host", "localhost")

    # Force WSS if running on Cloud Run (or behind any HTTPS proxy)
    # X-Forwarded-Proto is set by Cloud Run load balancer
    forwarded_proto = request.headers.get("x-forwarded-proto", "")
    logger.info(
        "Incoming call headers: host=%s, proto=%s, scheme=%s",
        host,
        forwarded_proto,
        request.url.scheme,
    )

    is_secure = (
        request.url.scheme == "https"
        or "https" in forwarded_proto
        or host.endswith(".run.app")
        or host.endswith(".ngrok-free.app")
    )
    protocol = "wss" if is_secure else "ws"

    ws_url = f"{protocol}://{host}/ws"

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Connect>
        <Stream url="{ws_url}" />
    </Connect>
</Response>
"""
    return Response(content=xml, media_type="application/xml")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    Accept Twilio Media Streams WebSocket, run Pipecat pipeline, save transcript on disconnect.
    """
    await websocket.accept()
    settings = get_settings()

    try:
        from pipecat.runner.utils import parse_telephony_websocket

        transport_type, call_data = await parse_telephony_websocket(websocket)
    except Exception as e:
        logger.exception("Failed to parse telephony WebSocket: %s", e)
        await websocket.close(code=4500)
        return

    if transport_type != "twilio":
        logger.warning("Unsupported transport type: %s", transport_type)
        await websocket.close(code=4500)
        return

    session_id = call_data.get("call_id", "") or "unknown"
    serializer = create_twilio_serializer(call_data, settings)
    transport = create_transport(websocket, serializer)
    _, task, context = build_pipeline(transport, settings, sample_rate=8000)
    register_handlers(transport, task, context, settings, session_id)

    try:
        await run_pipeline(task)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for session %s", session_id)
    except Exception as e:
        logger.exception("Pipeline error for session %s: %s", session_id, e)
    finally:
        await task.cancel()
