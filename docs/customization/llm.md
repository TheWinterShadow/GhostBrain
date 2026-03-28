# Switching the LLM (The Brain)

GhostBrain uses Groq by default because of its lightning-fast LPU inference speeds, which is critical for natural voice conversations. However, if you want to use OpenAI, Anthropic, or Together AI, you can easily change the LLM service.

## Step 1: Update Dependencies

Install the necessary Pipecat extra for your provider. For example, to use Anthropic (Claude):

```bash
hatch run pip install "pipecat-ai[anthropic]"
```

## Step 2: Add the API Key

1.  In `.env`:
    ```bash
    GHOST_BRAIN_ANTHROPIC_API_KEY=your_key_here
    ```

2.  In `src/ghost_brain/config.py`:
    ```python
    class Settings(BaseSettings):
        # ...
        anthropic_api_key: str = Field(default="")
    ```

## Step 3: Modify the LLM Factory

Open `src/ghost_brain/services/llm.py`. Swap `GroqLLMService` for `AnthropicLLMService`.

```python
# from pipecat.services.groq.llm import GroqLLMService
from pipecat.services.anthropic import AnthropicLLMService
from ghost_brain.config import Settings

def create_llm(settings: Settings) -> AnthropicLLMService:
    """
    Create Anthropic LLM service (Claude 3.5 Sonnet).
    """
    greeting = settings.ai_greeting.format(name=settings.ai_name)
    system_prompt = (
        f"You are {settings.ai_name}. {settings.system_instructions} "
        "When greeting the user for the first time, introduce yourself "
        f"using exactly these words: '{greeting}'."
    )

    return AnthropicLLMService(
        api_key=settings.anthropic_api_key,
        model="claude-3-5-sonnet-20240620",
        system_instruction=system_prompt,
    )
```

And that's it! Because both classes inherit from Pipecat's `LLMService`, the pipeline will automatically handle the chunking, token aggregation, and tool calling required for Claude.
