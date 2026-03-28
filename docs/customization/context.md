# Custom Context & Prompts

Before the AI utters its first word, it needs to know who it is, who it is talking to, and the purpose of the call. This is handled by the **LLM Context**.

## Modifying the Initial System Prompt

The simplest way to change the AI's behavior is to modify its system instructions.

1.  If you are running locally, edit your `.env` file:
    ```bash
    GHOST_BRAIN_AI_NAME="Dr. Watson"
    GHOST_BRAIN_SYSTEM_INSTRUCTIONS="You are a brilliant diagnostic physician. Ask the user about their symptoms and suggest a logical diagnosis."
    GHOST_BRAIN_AI_GREETING="Hello, I am {name}. What seems to be the problem today?"
    ```
2.  If you are deploying via GitHub Actions, add these variables to your GitHub Secrets (`SYSTEM_INSTRUCTIONS`, etc.) and they will automatically inject into Cloud Run.

## Pre-loading Context (RAG)

If you need the AI to know specific things about the caller *before* the call starts (like their account history, the status of an order, or data fetched from a vector database), you can inject this into the `messages` array in `LLMContext`.

Open `src/ghost_brain/services/context.py` and modify the factory:

```python
from pipecat.processors.aggregators.llm_context import LLMContext, LLMContextMessage

def create_context_and_aggregators(
    sample_rate: int = 16000,
    user_data: dict = None  # Pass this in from your app.py WebSocket handler!
) -> tuple[LLMContext, LLMUserAggregator, LLMAssistantAggregator]:

    messages = []

    # Inject dynamic user data before the conversation begins
    if user_data:
        messages.append(
            LLMContextMessage(
                role="system",
                content=f"Context: The caller's name is {user_data['name']}. They last ordered: {user_data['last_order']}."
            )
        )

    context = LLMContext(messages=messages)

    user_agg = LLMUserAggregator(context)
    assistant_agg = LLMAssistantAggregator(context)

    return context, user_agg, assistant_agg
```

Because Pipecat handles state automatically, the LLM will remember this hidden system message throughout the entire stream and use it to personalize the conversation.
