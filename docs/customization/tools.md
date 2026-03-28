# Adding Tools (Function Calling)

GhostBrain supports giving the AI "Tools" (or function calling). This allows the LLM to interact with external systems during the conversation—like looking up a user's account, fetching real-time weather, or booking an appointment.

Pipecat handles the execution of these tools natively using the `@tool` decorator or `register_direct_function`.

## Step 1: Create the Tool

Create a new file in `src/ghost_brain/tools/` (e.g., `weather.py`). Define an async function with standard Python type hints and a detailed docstring. Pipecat parses the docstring to tell the LLM how to use it!

```python
# src/ghost_brain/tools/weather.py
import aiohttp
from loguru import logger
from pipecat.services.ai_services import FunctionCallParams

async def get_weather(params: FunctionCallParams, **kwargs) -> None:
    """
    Get the current weather for a specific city.

    Args:
        city (str): The name of the city to get the weather for (e.g., 'San Francisco').
    """
    city = kwargs.get("city")
    logger.info(f"Looking up weather for {city}...")

    # Example API call (replace with your real logic)
    # async with aiohttp.ClientSession() as session:
    #    async with session.get(f"https://api.weather.com/v1/{city}") as resp:
    #        data = await resp.json()

    weather_data = f"The weather in {city} is currently 72 degrees and sunny."

    # Return the result back to the LLM by yielding it onto the pipeline
    await params.pipeline_task.queue_frames([
        params.llm.get_function_response_frame(
            function_name="get_weather",
            tool_call_id=params.function_call.tool_call_id,
            result=weather_data
        )
    ])
```

> **Note:** The `**kwargs` argument is strictly required by Pipecat to capture the extracted parameters from the LLM.

## Step 2: Register the Tool in Context

For the LLM to know the tool exists, you must add it to the `LLMContext` when creating the aggregators.

Modify `src/ghost_brain/services/context.py`:

```python
from ghost_brain.tools.weather import get_weather

def create_context_and_aggregators(
    sample_rate: int = 16000,
) -> tuple[LLMContext, LLMUserAggregator, LLMAssistantAggregator]:

    # Add your tool function to standard_tools
    context = LLMContext(
        messages=[],
        standard_tools=[get_weather]
    )

    # ... rest of the function ...
```

## Step 3: Bind the Tool to the LLM Service

Finally, register the direct function on the LLM instance so it executes the Python code when triggered.

Modify `src/ghost_brain/core/pipeline.py`:

```python
from ghost_brain.tools.weather import get_weather

async def build_pipeline(...):
    # ...
    llm = create_llm(settings)

    # Register the tool
    llm.register_direct_function(get_weather)

    # ...
```

Now, when a user asks "What is the weather in Paris?", the LLM will pause, trigger the `get_weather` function, await the result, and fluently speak the answer back!
