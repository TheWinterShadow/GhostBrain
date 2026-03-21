# GhostBrain Documentation

Welcome to the GhostBrain documentation! GhostBrain is a real-time voice AI interviewer bot that conducts natural conversations through phone calls or local microphone.

## What is GhostBrain?

GhostBrain combines state-of-the-art speech recognition, language models, and voice synthesis to create a seamless conversational AI experience. Whether you're building a voice assistant, conducting automated interviews, or creating interactive voice applications, GhostBrain provides the foundation you need.

### Key Features

- 🎙️ **Real-time voice conversations** with sub-second latency
- 📞 **Phone integration** via Twilio for production deployments
- 🖥️ **Local testing** with your computer's microphone
- 🤖 **Advanced AI stack**: Deepgram STT, Llama 3.1 70B via Groq, OpenAI TTS
- ☁️ **Cloud-native architecture** on Google Cloud Platform
- 📝 **Automatic transcription** of all conversations

## Documentation

### Getting Started
- [Quick Start Guide](../README.md) - Get up and running in 5 minutes
- [Local Testing Guide](local-testing.md) - Test with your microphone
- [API Reference](/api/index.html) - Detailed API documentation

### Architecture & Design
- [Architecture Overview](architecture.md) - System design, components, and data flow
- [Voice Pipeline](architecture.md#core-components) - How audio becomes conversation
- [Model Selection](architecture.md#model-selection-rationale) - Why we chose these AI models

### Deployment & Operations
- [Deployment Guide](../deployment.md) - Deploy to Google Cloud
- [Infrastructure](architecture.md#deployment-architecture) - GCP resources and Terraform
- [Monitoring](architecture.md#monitoring--observability) - Logs, metrics, and health checks

### Development
- [Agent Guidelines](../AGENTS.md) - For AI coding assistants
- [Project Status](status.md) - Current features and roadmap
- [Contributing](../README.md#contributing) - How to contribute

## Quick Example

Test GhostBrain locally with your microphone:

```bash
# Install dependencies
pip install hatch pyaudio

# Set up API keys in .env
echo "GHOST_BRAIN_DEEPGRAM_API_KEY=your_key" >> .env
echo "GHOST_BRAIN_GROQ_API_KEY=your_key" >> .env
echo "GHOST_BRAIN_OPENAI_API_KEY=your_key" >> .env

# Run local test
hatch run python -m ghost_brain.local_mic_test
```

## Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Speech-to-Text** | Deepgram Nova-2 | Transcribe speech with high accuracy |
| **Language Model** | Llama 3.1 70B (via Groq) | Generate intelligent responses |
| **Text-to-Speech** | OpenAI TTS-1 | Natural voice synthesis |
| **Voice Pipeline** | Pipecat | Real-time audio processing |
| **Web Framework** | FastAPI | WebSocket server |
| **Deployment** | Google Cloud Run | Serverless container hosting |
| **Infrastructure** | Terraform | Infrastructure as code |

## Support

- 📖 Browse the full [documentation](.)
- 🐛 Report issues on [GitHub](https://github.com/your-org/ghost-brain/issues)
- 💬 Join the [discussion](https://github.com/your-org/ghost-brain/discussions)
