"""Unit tests for ghostwriter.transcript."""

from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from ghostwriter.transcript import format_transcript_markdown, upload_transcript_to_gcs


def test_format_transcript_markdown_basic(sample_messages: list[dict]) -> None:
    """Format should produce frontmatter and user/assistant lines."""
    out = format_transcript_markdown(sample_messages, session_id="call-123")
    assert "Date:" in out
    assert "ID: call-123" in out
    assert "**User:** Hello." in out
    assert "**Assistant:** Hi! How can I help you today?" in out
    assert "**User:** I'd like to schedule an interview." in out


def test_format_transcript_markdown_defaults_session_id(sample_messages: list[dict]) -> None:
    """When session_id is None, a UUID should be used."""
    out = format_transcript_markdown(sample_messages, session_id=None)
    assert "ID:" in out
    assert "ID: unknown" not in out
    # Should look like a UUID (contains dashes)
    line = [l for l in out.splitlines() if l.startswith("ID:")][0]
    assert len(line) > 10


def test_format_transcript_markdown_custom_date(sample_messages: list[dict]) -> None:
    """Custom date should appear in frontmatter."""
    dt = datetime(2025, 3, 1, 12, 0, 0, tzinfo=timezone.utc)
    out = format_transcript_markdown(sample_messages, session_id="x", date=dt)
    assert "2025-03-01T12:00:00Z" in out


def test_format_transcript_markdown_unknown_role() -> None:
    """Messages with unknown role should still be included."""
    messages = [{"role": "system", "content": "You are helpful."}]
    out = format_transcript_markdown(messages, session_id="s")
    assert "**system:**" in out
    assert "You are helpful." in out


@patch("ghostwriter.transcript.storage.Client")
def test_upload_transcript_to_gcs(
    mock_client_class: object,
    mock_storage_bucket: MagicMock,
) -> None:
    """Upload should call bucket.blob and upload_from_string."""
    mock_client_class.return_value.bucket.return_value = mock_storage_bucket
    upload_transcript_to_gcs(
        "my-bucket",
        "# Transcript\n\nHello.",
        "transcripts/abc.md",
    )
    mock_storage_bucket.blob.assert_called_once_with("transcripts/abc.md")
    blob = mock_storage_bucket.blob.return_value
    blob.upload_from_string.assert_called_once()
    args, kwargs = blob.upload_from_string.call_args
    assert args[0] == "# Transcript\n\nHello."
    assert kwargs.get("content_type") == "text/markdown"
