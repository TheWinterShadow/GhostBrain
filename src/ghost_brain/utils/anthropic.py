import json
import logging

from anthropic import Anthropic

logger = logging.getLogger(__name__)


class AnthropicClient:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    def process_transcript(
        self, system_prompt: str, transcript: str, model: str = "claude-3-5-sonnet-20241022"
    ) -> list[dict[str, str]]:
        """
        Sends the transcript and templates to Claude, expecting a structured JSON list of files back.
        """
        logger.info(f"Sending transcript to Anthropic using model {model}")

        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=4000,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Here is the transcript. Please process it according to the system instructions and output strictly a JSON list.\n\n<transcript>\n{transcript}\n</transcript>",
                    }
                ],
                temperature=0.2,
            )

            # The response should be pure JSON or wrapped in a json codeblock.
            content = message.content[0].text.strip()

            # Extract JSON if it's wrapped in markdown blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            parsed_data = json.loads(content)

            if not isinstance(parsed_data, list):
                raise ValueError(f"Expected a list of dicts, got {type(parsed_data)}")

            return parsed_data

        except Exception as e:
            logger.error(f"Error processing transcript with Anthropic: {e}")
            raise
