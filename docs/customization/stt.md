# Switching the Speech-to-Text (STT)

GhostBrain uses Deepgram (`DeepgramSTTService`) by default because it offers ultra-low latency streaming and excellent accuracy. However, you can easily swap this out for another provider supported by Pipecat (like Gladia or Azure).

## Step 1: Update Dependencies

First, check if Pipecat requires an optional dependency for your new provider. For example, to switch to Gladia:

```bash
# Optional: Add gladia extra dependency
hatch run pip install "pipecat-ai[gladia]"
```

*Note: Update your `pyproject.toml` dependencies to make this permanent!*

## Step 2: Add the API Key

Add the new API key to your environment and `Settings` model.

1.  In `.env`:
    ```bash
    GHOST_BRAIN_GLADIA_API_KEY=your_key_here
    ```

2.  In `src/ghost_brain/config.py`:
    ```python
    class Settings(BaseSettings):
        # ... existing keys ...
        gladia_api_key: str = Field(default="")
    ```

## Step 3: Modify the STT Factory

Open `src/ghost_brain/services/stt.py`. Change the import and the returned class:

```python
# Remove Deepgram import
# from pipecat.services.deepgram import DeepgramSTTService

# Add new import
from pipecat.services.gladia import GladiaSTTService
from ghost_brain.config import Settings

def create_stt(settings: Settings, sample_rate: int = 16000):
    """
    Create STT service (swapped to Gladia).
    """
    return GladiaSTTService(
        api_key=settings.gladia_api_key,
        # Gladia-specific configurations
        audio_config={
            "sample_rate": sample_rate,
            "encoding": "linear16"
        }
    )
```

Because Pipecat standardizes the interfaces for all its components, you don't need to change `pipeline.py` or any of the WebSocket logic! The pipeline will treat the new STT service exactly like the old one.
