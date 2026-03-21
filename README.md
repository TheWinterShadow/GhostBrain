# GhostBrain 🧠

A real-time voice AI interviewer bot that conducts natural conversations through phone calls or local microphone. Built with FastAPI, Pipecat, and state-of-the-art AI models.

## Features

- 🎙️ **Real-time voice conversations** - Natural, low-latency dialogue
- 📞 **Phone integration** - Call via Twilio phone numbers
- 🖥️ **Local testing** - Test with your microphone, no phone needed
- 🤖 **Advanced AI stack** - Deepgram STT, Llama 3.1 70B, OpenAI TTS
- ☁️ **Cloud-native** - Runs on Google Cloud Run, scales to zero
- 📝 **Automatic transcripts** - Saves all conversations

## Quick Start

### Prerequisites

- Python 3.12 (exactly - not 3.11 or 3.13)
- [Hatch](https://hatch.pypa.io/) package manager
- API keys from [Deepgram](https://console.deepgram.com/), [Groq](https://console.groq.com/), and [OpenAI](https://platform.openai.com/)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/ghost-brain.git
cd ghost-brain

# Install Hatch if you haven't already
pip install hatch

# Create development environment
hatch env create dev

# Install pre-commit hooks
pre-commit install
```

### Configuration

Create a `.env` file with your API keys:

```bash
# Required API Keys
GHOST_BRAIN_DEEPGRAM_API_KEY=your_deepgram_key
GHOST_BRAIN_GROQ_API_KEY=your_groq_key
GHOST_BRAIN_OPENAI_API_KEY=your_openai_key

# Optional: For production with Twilio
GHOST_BRAIN_TWILIO_ACCOUNT_SID=your_sid
GHOST_BRAIN_TWILIO_AUTH_TOKEN=your_token

# Optional: For Daily.co testing
DAILY_API_TOKEN=your_daily_token
```

### Test Locally with Your Microphone

The fastest way to test GhostBrain:

```bash
# Install PyAudio (for microphone access)
# macOS: brew install portaudio
# Linux: sudo apt-get install portaudio19-dev
pip install pyaudio

# Run the local test
hatch run python -m ghost_brain.local_mic_test
```

Speak into your microphone and have a conversation with the AI! Press `Ctrl+C` to end and save the transcript.

### Run the Server

For production deployment with Twilio:

```bash
# Start the FastAPI server
hatch run uvicorn ghost_brain.app:app --host 0.0.0.0 --port 8080

# Or with auto-reload for development
hatch run uvicorn ghost_brain.app:app --reload --port 8080
```

## Architecture Overview

```
Phone/Mic → Audio Input → Speech-to-Text → LLM → Text-to-Speech → Audio Output → Speaker
             (Twilio)      (Deepgram)    (Groq)    (OpenAI)
```

**Core Components:**
- **FastAPI** - WebSocket server for real-time communication
- **Pipecat** - Orchestrates the voice pipeline
- **Deepgram Nova-2** - Converts speech to text with high accuracy
- **Llama 3.1 70B on Groq** - Generates intelligent responses
- **OpenAI TTS** - Converts responses to natural speech
- **Silero VAD** - Detects when users start/stop talking

## Documentation

- 📘 [Architecture Guide](docs/architecture.md) - System design and data flow
- 🧪 [Local Testing Guide](docs/local-testing.md) - Test without phone setup
- 🚀 [Deployment Guide](deployment.md) - Deploy to Google Cloud
- 🤖 [Agent Guidelines](AGENTS.md) - For AI coding assistants

## Development

### Commands

```bash
# Run tests
hatch run test

# Run specific test
hatch run pytest tests/unit/test_app.py::test_health -v

# Lint code
hatch run dev:lint

# Format code
hatch run dev:fmt

# Run with coverage
hatch run pytest tests -v --cov=src/ghost_brain

# Build documentation
hatch run sphinx-build -M html docs/sphinx build/sphinx
```

### Project Structure

```
ghost_brain/
├── src/ghost_brain/      # Main application code
│   ├── app.py           # FastAPI WebSocket endpoint
│   ├── pipeline.py      # Pipecat voice pipeline
│   ├── config.py        # Settings management
│   └── local_mic_test.py # Local testing script
├── tests/               # Unit tests
├── terraform/           # Infrastructure as code
├── docs/               # Documentation
└── .github/            # CI/CD workflows
```

## Deployment

GhostBrain runs on Google Cloud Platform:

1. **Cloud Run** - Serverless container hosting
2. **Cloud Storage** - Transcript storage
3. **Secret Manager** - Secure API key storage
4. **Cloud Build** - Automated CI/CD

Deploy with:
```bash
# Build and push Docker image
docker build -t gcr.io/your-project/ghost-brain .
docker push gcr.io/your-project/ghost-brain

# Deploy with Terraform
cd terraform
terraform init
terraform apply
```

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GHOST_BRAIN_DEEPGRAM_API_KEY` | Deepgram API key for STT | Yes |
| `GHOST_BRAIN_GROQ_API_KEY` | Groq API key for LLM | Yes |
| `GHOST_BRAIN_OPENAI_API_KEY` | OpenAI API key for TTS | Yes |
| `GHOST_BRAIN_TWILIO_ACCOUNT_SID` | Twilio account SID | For phone calls |
| `GHOST_BRAIN_TWILIO_AUTH_TOKEN` | Twilio auth token | For phone calls |
| `GHOST_BRAIN_GCS_BUCKET` | GCS bucket for transcripts | For cloud storage |
| `DAILY_API_TOKEN` | Daily.co API token | For Daily testing |

### Customization

Modify the system prompt in `pipeline.py`:
```python
system_instruction=(
    "You are Ghost Brain, a friendly voice interviewer. "
    "Keep responses concise and natural for spoken conversation."
)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

All contributions must pass:
- Ruff linting and formatting
- All unit tests
- Pre-commit hooks

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/your-org/ghost-brain/issues)
- 💬 [Discussions](https://github.com/your-org/ghost-brain/discussions)

## Acknowledgments

Built with:
- [Pipecat](https://github.com/pipecat-ai/pipecat) - Real-time voice pipeline framework
- [Deepgram](https://deepgram.com/) - Speech recognition
- [Groq](https://groq.com/) - Fast LLM inference
- [OpenAI](https://openai.com/) - Text-to-speech
