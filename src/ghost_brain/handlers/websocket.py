"""WebSocket and HTTP endpoints for live call handling."""

import logging

from fastapi import APIRouter, Request, Response, WebSocket, WebSocketDisconnect

from ghost_brain.config import get_settings
from ghost_brain.modules.pipeline.pipeline import build_pipeline
from ghost_brain.modules.pipeline.runner import register_handlers, run_pipeline
from ghost_brain.transport.twilio import create_transport, create_twilio_serializer

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/incoming-call")
async def incoming_call(request: Request) -> Response:
    """Handle incoming call requests and return TwiML."""
    form_data = await request.form()
    caller_number = form_data.get("From", "Unknown")
    logger.info("Incoming call received from: %s", caller_number)

    host = request.headers.get("host", "localhost")

    # Force WSS if running on Cloud Run (or behind any HTTPS proxy)
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
        <Stream url="{ws_url}">
            <Parameter name="caller_id" value="{caller_number}" />
        </Stream>
    </Connect>
</Response>
"""
    return Response(content=xml, media_type="application/xml")


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Accept Twilio WebSocket, run Pipecat pipeline, save transcript on disconnect."""
    await websocket.accept()
    settings = get_settings()

    try:
        from pipecat.runner.utils import parse_telephony_websocket

        transport_type, call_data = await parse_telephony_websocket(websocket)
        logger.info("WebSocket connected: transport=%s, call_data=%s", transport_type, call_data)
    except Exception as e:
        logger.exception("Failed to parse telephony WebSocket: %s", e)
        await websocket.close(code=4500)
        return

    if transport_type != "twilio":
        logger.warning("Unsupported transport type: %s", transport_type)
        await websocket.close(code=4500)
        return

    custom_params = call_data.get("body", {})
    caller_id = custom_params.get("caller_id", "Unknown")
    logger.info("Call started! Caller ID: %s", caller_id)

    if settings.allowed_caller_id and not caller_id.endswith(settings.allowed_caller_id):
        logger.warning(f"Unauthorized caller ID: {caller_id}. Dropping call.")
        await websocket.close(code=4003)
        return

    session_id = call_data.get("call_id", "") or "unknown"
    serializer = create_twilio_serializer(call_data, settings)
    transport = create_transport(websocket, serializer)
    _, task, context = await build_pipeline(transport, settings, sample_rate=8000)
    register_handlers(transport, task, context, settings, session_id)

    try:
        await run_pipeline(task)
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected for session %s", session_id)
    except Exception as e:
        logger.exception("Pipeline error for session %s: %s", session_id, e)
    finally:
        await task.cancel()
