"""Twilio WebSocket transport construction for Pipecat."""

from typing import Any

from fastapi import WebSocket
from pipecat.serializers.twilio import TwilioFrameSerializer
from pipecat.transports.websocket.fastapi import (
    FastAPIWebsocketParams,
    FastAPIWebsocketTransport,
)

from ghost_brain.config import Settings


def create_twilio_serializer(
    call_data: dict[str, Any],
    settings: Settings,
) -> TwilioFrameSerializer:
    """
    Build a Twilio frame serializer from parsed call data and settings.

    Args:
        call_data: Dict with 'stream_id' and 'call_id' (from parse_telephony_websocket).
        settings: Application settings (Twilio credentials).

    Returns:
        Configured TwilioFrameSerializer for the call.
    """
    stream_sid = call_data.get("stream_id", "")
    call_sid = call_data.get("call_id", "")
    return TwilioFrameSerializer(
        stream_sid=stream_sid,
        call_sid=call_sid,
        account_sid=settings.twilio_account_sid or None,
        auth_token=settings.twilio_auth_token or None,
    )


def create_transport(
    websocket: WebSocket,
    serializer: TwilioFrameSerializer,
) -> FastAPIWebsocketTransport:
    """
    Create the FastAPI WebSocket transport for Twilio audio streaming.

    Args:
        websocket: The accepted FastAPI WebSocket.
        serializer: Twilio serializer for this call.

    Returns:
        Configured FastAPIWebsocketTransport.
    """
    params = FastAPIWebsocketParams(
        audio_in_enabled=True,
        audio_in_sample_rate=8000,
        audio_out_enabled=True,
        audio_out_sample_rate=8000,
        add_wav_header=False,
        serializer=serializer,
    )
    return FastAPIWebsocketTransport(websocket, params=params)
