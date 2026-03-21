# GhostBrain Agent Guidelines

This document provides essential information for AI agents working on the GhostBrain codebase.

## Project Overview

GhostBrain is a **voice-interviewer bot** built with:
- **Language**: Python 3.12 (strictly)
- **Framework**: FastAPI for WebSocket endpoints
- **Core Library**: Pipecat for real-time voice pipeline
- **Integrations**: Twilio (telephony), Deepgram (STT), Groq (LLM), OpenAI (TTS)
- **Deployment**: Google Cloud Run (containerized)
- **Infrastructure**: Terraform-managed GCP resources

## Build, Test, and Development Commands

### Environment Setup
```bash
# Install Hatch (Python package manager)
pip install hatch

# Install pre-commit hooks
pre-commit install

# Create development environment
hatch env create dev
```

### Common Development Commands
```bash
# Run all tests
hatch run test

# Run specific test file
hatch run pytest tests/unit/test_app.py -v

# Run single test function
hatch run pytest tests/unit/test_app.py::test_health -v

# Run tests with coverage
hatch run pytest tests -v --cov=src/ghost_brain --cov-report=term-missing

# Lint code
hatch run dev:lint  # or: ruff check src tests

# Format code
hatch run dev:fmt   # or: ruff format src tests

# Run pre-commit hooks manually
pre-commit run --all-files

# Build documentation
hatch run sphinx-build -M html docs/sphinx build/sphinx

# Run application locally (requires Twilio webhook)
uvicorn ghost_brain.app:app --reload --port 8000

# Test locally with microphone (no Twilio needed)
hatch run python -m ghost_brain.local_test  # Uses Daily transport
# OR
hatch run python -m ghost_brain.local_mic_test  # Uses PyAudio (simpler)
```

### Local Testing with Microphone
```bash
# Option 1: Daily transport (web-based, can share room URL)
DAILY_API_TOKEN=your_token hatch run python -m ghost_brain.local_test

# Option 2: PyAudio (direct microphone access, simpler setup)
# First install PyAudio:
pip install pyaudio  # On macOS: brew install portaudio first
# Then run:
hatch run python -m ghost_brain.local_mic_test
```

### Docker Operations
```bash
# Build container
docker build -t ghost-brain .

# Run container locally (requires .env file)
docker run --env-file .env -p 8080:8080 ghost-brain
```

## Code Style Guidelines

### Import Organization
Follow Ruff's import sorting (automatically applied):
1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
import logging
from pathlib import Path

from fastapi import FastAPI, WebSocket
from pipecat.pipeline import Pipeline

from ghost_brain.config import get_settings
from ghost_brain.core.pipeline import build_pipeline
```

### Formatting Rules
- **Line length**: 100 characters maximum
- **Quote style**: Double quotes for strings (`"string"`, not `'string'`)
- **Indentation**: 4 spaces (no tabs)
- **Trailing commas**: Use for multi-line structures
- **Blank lines**: 2 between module-level definitions, 1 between methods

### Type Hints
**Always use type hints** for function signatures:
```python
async def process_message(data: dict[str, Any], session_id: str) -> None:
    """Process incoming WebSocket message."""
    ...

def get_transcript(lines: list[str]) -> str:
    """Format transcript lines."""
    ...
```

### Naming Conventions
- **Modules/files**: `lowercase_with_underscores.py`
- **Classes**: `PascalCase` (e.g., `TranscriptManager`)
- **Functions/methods**: `lowercase_with_underscores` (e.g., `save_transcript`)
- **Constants**: `UPPERCASE_WITH_UNDERSCORES` (e.g., `MAX_RETRIES`)
- **Private items**: Leading underscore (e.g., `_internal_method`)

### Async/Await Patterns
This is an async-first codebase. Use async consistently:
```python
# Good
async def fetch_data() -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Bad - mixing sync and async
def fetch_data() -> dict:  # Should be async
    return requests.get(url).json()
```

### Error Handling
Use structured logging and proper exception handling:
```python
import logging
logger = logging.getLogger(__name__)

try:
    result = await risky_operation()
except SpecificError as e:
    logger.error("Operation failed: %s", e, exc_info=True)
    # Handle gracefully or re-raise
    raise
except Exception:
    logger.exception("Unexpected error in risky_operation")
    # Clean up resources if needed
    raise
```

### Configuration Management
Use Pydantic Settings for all configuration:
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_key: str
    timeout: int = 30

    model_config = SettingsConfigDict(env_prefix="GHOST_BRAIN_")
```

### Testing Patterns
- Use pytest fixtures for reusable test data
- Mock external services (never call real APIs in tests)
- Test async functions with `pytest-asyncio`
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result == expected

@pytest.fixture
def mock_settings():
    return Settings(api_key="test-key")
```

## Project Structure
```
src/ghost_brain/
├── app.py              # Main entry point
├── config.py           # Configuration
├── core/               # Core business logic
│   ├── pipeline.py     # Pipeline assembly logic
│   └── runner.py       # Execution logic
├── services/           # External service integrations
│   ├── stt.py          # Deepgram STT factory
│   ├── llm.py          # Groq LLM factory
│   ├── tts.py          # OpenAI TTS factory
│   └── context.py      # VAD and Context aggregators
├── transport/          # Transport layer
│   └── twilio.py       # Twilio specific logic
└── utils/              # Utilities
    └── transcript.py   # Transcript formatting/upload

tests/unit/          # Unit tests - mirror src structure
terraform/           # Infrastructure as code
docs/               # Documentation
scripts/            # Build/deploy scripts
```

## Security & Secrets
- **Never commit secrets** to the repository
- Use environment variables or GCP Secret Manager
- All sensitive config through `pydantic-settings`
- Check `.env.example` for required variables

## CI/CD & Quality Checks
All PRs must pass:
1. **Ruff linting** - No errors allowed
2. **Ruff formatting** - Must be properly formatted
3. **All tests** - 100% must pass
4. **Pre-commit hooks** - Including Terraform formatting

## Common Pitfalls to Avoid
1. **Don't use Python != 3.12** - The project strictly requires 3.12
2. **Don't skip type hints** - Always annotate function signatures
3. **Don't use single quotes** - Ruff enforces double quotes
4. **Don't ignore async** - This is an async-first codebase
5. **Don't hardcode config** - Use Settings class
6. **Don't skip tests** - Every new feature needs tests
7. **Don't bypass pre-commit** - Let it catch issues early

## Quick Reference
- **Main app**: `src/ghost_brain/app.py`
- **Settings**: `src/ghost_brain/config.py`
- **Pipeline**: `src/ghost_brain/core/pipeline.py`
- **Tests**: `tests/unit/`
- **Deploy config**: `terraform/modules/`
- **Container**: `Dockerfile`
