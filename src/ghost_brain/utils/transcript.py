"""Transcript formatting and Google Cloud Storage upload utilities."""

import contextlib
import uuid
from datetime import UTC, datetime
from typing import Any, cast

from google.cloud import storage
from pipecat.processors.aggregators.llm_context import LLMContext


def format_transcript_markdown(
    messages: list[dict[str, Any]],
    session_id: str | None = None,
    date: datetime | None = None,
) -> str:
    """
    Format a list of conversation messages into a Markdown document.

    Includes YAML frontmatter with session and temporal metadata.

    Args:
        messages: A list of message dictionaries containing 'role' and 'content' keys.
        session_id: An optional unique identifier for the conversation session.
        date: An optional timestamp for the conversation.

    Returns:
        str: The formatted Markdown string containing the transcript.
    """
    sid: str = session_id or str(uuid.uuid4())
    dt: datetime = date or datetime.now(UTC)
    date_str: str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    frontmatter: str = f"---\nDate: {date_str}\nID: {sid}\n---\n\n"

    body_lines: list[str] = []
    for msg in messages:
        role: str = msg.get("role", "unknown")
        content: Any = msg.get("content", "")

        if isinstance(content, list):
            text_parts: list[str] = [c.get("text", "") for c in content if c.get("type") == "text"]
            content = " ".join(text_parts)

        if role == "user":
            body_lines.append(f"**User:** {content}\n")
        elif role == "assistant":
            body_lines.append(f"**Assistant:** {content}\n")
        else:
            body_lines.append(f"**{role}:** {content}\n")

    return frontmatter + "\n".join(body_lines)


def format_transcript(context: LLMContext) -> str:
    """
    Extract and format transcript messages from an LLMContext instance.

    Args:
        context: The language model context containing the conversation history.

    Returns:
        str: The formatted Markdown string of the conversation.
    """
    messages: list[dict[str, Any]] = []

    for msg in context.messages:
        if isinstance(msg, dict):
            messages.append(cast(dict[str, Any], msg))
        elif hasattr(msg, "message"):
            if isinstance(msg.message, dict):
                messages.append(cast(dict[str, Any], msg.message))
            else:
                with contextlib.suppress(AttributeError):
                    messages.append(msg.message.model_dump())

    return format_transcript_markdown(messages)


def upload_transcript_to_gcs(
    bucket_name: str,
    content: str,
    blob_path: str,
    content_type: str = "text/markdown",
) -> None:
    """
    Upload a text payload to a specified Google Cloud Storage bucket.

    Args:
        bucket_name: The destination GCS bucket name.
        content: The text content to upload.
        blob_path: The destination path and filename within the bucket.
        content_type: The MIME type of the uploaded content.
    """
    client: storage.Client = storage.Client()
    bucket: storage.Bucket = client.bucket(bucket_name)
    blob: storage.Blob = bucket.blob(blob_path)

    blob.upload_from_string(
        content,
        content_type=content_type,
    )
