"""Transcript formatting and GCS upload for call recordings."""

import uuid
from datetime import datetime, timezone
from typing import Any

from google.cloud import storage


def format_transcript_markdown(
    messages: list[dict[str, Any]],
    session_id: str | None = None,
    date: datetime | None = None,
) -> str:
    """
    Format conversation messages as Markdown with YAML frontmatter.

    Args:
        messages: List of dicts with 'role' ('user'|'assistant') and 'content'.
        session_id: Optional session/call ID; defaults to a new UUID.
        date: Optional date; defaults to now (UTC).

    Returns:
        Markdown string with frontmatter and message body.
    """
    sid = session_id or str(uuid.uuid4())
    dt = date or datetime.now(timezone.utc)
    date_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    frontmatter = f"""---
Date: {date_str}
ID: {sid}
---

"""
    body_lines: list[str] = []
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        if role == "user":
            body_lines.append(f"**User:** {content}\n")
        elif role == "assistant":
            body_lines.append(f"**Assistant:** {content}\n")
        else:
            body_lines.append(f"**{role}:** {content}\n")

    return frontmatter + "\n".join(body_lines)


def upload_transcript_to_gcs(
    bucket_name: str,
    content: str,
    blob_path: str,
    content_type: str = "text/markdown",
) -> None:
    """
    Upload transcript content to a GCS bucket.

    Args:
        bucket_name: Name of the GCS bucket.
        content: String content (Markdown) to upload.
        blob_path: Object path within the bucket (e.g. 'transcripts/abc.md').
        content_type: MIME type; defaults to 'text/markdown'.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.upload_from_string(
        content,
        content_type=content_type,
    )
