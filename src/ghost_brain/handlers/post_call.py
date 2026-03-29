"""Webhooks and events for post-call processing."""

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request, Response

from ghost_brain.config import get_settings
from ghost_brain.utils.anthropic import AnthropicClient
from ghost_brain.utils.gcs_bucket import GCSBucket

logger = logging.getLogger(__name__)

router = APIRouter()


def load_templates() -> str:
    """Load all markdown templates into a single string for the prompt."""
    templates_dir = Path(__file__).parent.parent / "utils" / "file_templates"
    templates_text = ""

    if not templates_dir.exists():
        logger.warning(f"Templates directory not found at {templates_dir}")
        return templates_text

    for template_file in templates_dir.glob("*.md"):
        try:
            content = template_file.read_text(encoding="utf-8")
            templates_text += f"\n--- Template: {template_file.name} ---\n{content}\n"
        except Exception as e:
            logger.error("Failed to read template %s: %s", template_file.name, e)

    return templates_text


@router.post("/events/post-call")
async def post_call_handler(request: Request) -> Response:
    """Handle post-call processing triggered by Eventarc/GCS."""
    logger.info("Received post-call event from GCS/Eventarc")

    # CloudEvents provide metadata in headers
    event_type: str = request.headers.get("ce-type", "Unknown")
    header_file_name: str = request.headers.get("ce-subject", "Unknown")
    header_bucket_name: str = request.headers.get("ce-source", "Unknown")

    logger.info(
        "Event Type: %s | Header Source: %s | Header Subject: %s",
        event_type,
        header_bucket_name,
        header_file_name,
    )

    bucket_name = "Unknown"
    file_name = "Unknown"

    try:
        payload: dict[str, Any] = await request.json()
        logger.info("Payload received keys: %s", list(payload.keys()))
        bucket_name = payload.get("bucket", header_bucket_name)
        file_name = payload.get("name", header_file_name)
    except Exception as e:
        logger.warning("No JSON payload or error parsing: %s. Falling back to headers.", e)
        bucket_name = header_bucket_name
        file_name = header_file_name

    # Clean up ce-source if it's the long URI
    if bucket_name and bucket_name.startswith("//storage.googleapis.com/projects/_/buckets/"):
        bucket_name = bucket_name.split("buckets/")[1]

    # Do not process files that are already processed by Anthropic
    if file_name.startswith("processed/"):
        logger.info("Ignoring file %s (processed file)", file_name)
        return Response(status_code=200, content="Ignored file")

    if file_name.startswith("objects/"):
        file_name = file_name.split("objects/")[1]

    if bucket_name == "Unknown" or file_name == "Unknown":
        logger.warning("Missing bucket or file name in payload")
        return Response(status_code=400, content="Missing bucket or file name in payload")

    settings = get_settings()

    # 1. Download Transcript
    transcript_bucket = GCSBucket(bucket_name)
    try:
        transcript_content = transcript_bucket.download_blob_as_string(file_name)
        logger.info("Transcript successfully downloaded. Length: %d", len(transcript_content))
    except Exception as e:
        logger.error("Error downloading transcript: %s", e)
        return Response(status_code=500, content="Error downloading transcript")

    # 2. Idempotency check — skip if this transcript was already processed
    sentinel = f"processed/transcripts/{Path(file_name).name}"
    if transcript_bucket.blob_exists(sentinel):
        logger.info("Transcript %s already processed (sentinel found). Skipping.", file_name)
        return Response(status_code=200, content="Already processed")

    # 3. Load Templates and Prepare Prompt
    templates_text = load_templates()
    if not templates_text:
        logger.warning("No templates found, proceeding with basic summary instructions.")
        templates_text = "No specific templates provided. Just write a summary markdown file."

    system_prompt = f"""You are an intelligent transcript analyzer and markdown generator.
You will be provided with a raw voice transcript. Your goal is to analyze the transcript
and convert the conversation into one or more beautifully formatted markdown files based
on the templates provided below.

If the user talks about a single topic, choose the best matching template.
If the user talks about multiple distinct topics (e.g., their daily journal AND a new project
idea), split the information into MULTIPLE distinct files, choosing the appropriate template
for each. Fill out the templates intelligently based on what the user said.

IMPORTANT RULES:
- Do NOT duplicate content across files. Each piece of information should appear in exactly
  one file. If a topic fits multiple templates, pick the best one.
- Every file must include relevant tags on the second line (immediately after the # Title),
  using the format: #tag1 #tag2 #tag3. Choose tags that reflect the content (e.g. #daily-log,
  #project, #idea, #knowledge, #tasks, #work, #personal). Always include at least one tag.

Available Templates:
{templates_text}

OUTPUT FORMAT:
You must output ONLY a valid JSON list containing dictionaries for each file. Do not
include any conversational text.
Example format:
[
  {{
    "file_name": "daily_log_2023-10-27.md",
    "file_content": "# Daily Log 2023-10-27\\n#daily-log #reflection\\n..."
  }},
  {{
    "file_name": "project_idea_x.md",
    "file_content": "# Project X\\n#project #idea\\n..."
  }}
]
"""

    # 4. Call Anthropic
    try:
        anthropic_client = AnthropicClient(api_key=settings.anthropic_api_key)
        generated_files = anthropic_client.process_transcript(
            system_prompt=system_prompt, transcript=transcript_content
        )
        logger.info("Anthropic processing complete. Generated %d files.", len(generated_files))
    except Exception as e:
        logger.error("Error calling Anthropic: %s", e)
        return Response(status_code=500, content="Error processing transcript via AI")

    # 5. Save results back to GCS
    for file_data in generated_files:
        out_name = file_data.get("file_name")
        out_content = file_data.get("file_content")

        if not out_name or not out_content:
            logger.warning("Skipping invalid file data: %s", file_data)
            continue

        # Prepend 'processed/' so we don't infinitely trigger the Eventarc webhook
        # Eventarc filters on the bucket, so any new file triggers this again.
        safe_name = f"processed/{out_name}"

        try:
            transcript_bucket.upload_string_to_blob(safe_name, out_content)
            logger.info("Successfully saved %s back to bucket.", safe_name)
        except Exception as e:
            logger.error("Failed to save %s: %s", safe_name, e)

    # Write sentinel so redelivered events are skipped
    try:
        transcript_bucket.upload_string_to_blob(sentinel, "")
        logger.info("Wrote processing sentinel: %s", sentinel)
    except Exception as e:
        logger.warning("Failed to write sentinel %s: %s", sentinel, e)

    return Response(status_code=200, content="Post-call logic executed successfully")
