# Ghostwriter

Voice-interviewer bot using Pipecat, Twilio, Deepgram, Groq, and OpenAI TTS. Runs on Google Cloud Run and stores call transcripts in GCS.

## Setup

- Python 3.12+, Hatch
- See `docs/` for full documentation and `terraform/` for infrastructure.

## Run locally

```bash
hatch run uvicorn ghostwriter.app:app --host 0.0.0.0 --port 8080
```

## License

MIT
