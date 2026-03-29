import logging

from anthropic import Anthropic
from anthropic.types import ToolUseBlock

logger = logging.getLogger(__name__)


class AnthropicClient:
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)

    def process_transcript(
        self, system_prompt: str, transcript: str, model: str = "claude-sonnet-4-6"
    ) -> list[dict[str, str]]:
        """
        Sends the transcript and templates to Claude,
        expecting a structured JSON list of files back.
        """
        logger.info(f"Sending transcript to Anthropic using model {model}")

        try:
            message = self.client.messages.create(
                model=model,
                max_tokens=4000,
                system=system_prompt,
                tools=[
                    {
                        "name": "output_results",
                        "description": "Output the structured results from the transcript",
                        "input_schema": {
                            "type": "object",
                            "properties": {
                                "results": {
                                    "type": "array",
                                    "items": {"type": "object"},
                                }
                            },
                            "required": ["results"],
                        },
                    }
                ],
                tool_choice={"type": "tool", "name": "output_results"},
                messages=[
                    {
                        "role": "user",
                        "content": f"Here is the transcript. Please process it according to the "
                        f"system instructions.\n\n<transcript>\n{transcript}\n</transcript>",
                    }
                ],
                temperature=0.2,
            )

            block = message.content[0]
            if not isinstance(block, ToolUseBlock):
                raise ValueError(f"Unexpected content block type: {type(block)}")

            input_data: dict[str, list[dict[str, str]]] = block.input  # type: ignore[assignment]
            results = input_data.get("results")
            if not isinstance(results, list):
                raise ValueError(f"Expected a list of dicts, got {type(results)}")

            return results

        except Exception as e:
            logger.error(f"Error processing transcript with Anthropic: {e}")
            raise
