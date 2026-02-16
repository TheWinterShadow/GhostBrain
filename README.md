# GhostBrain

A self-hosted, ultra-low-latency voice interviewer. Replaces Vapi with a custom Python orchestrator running on Google Cloud Run.

## Architecture

- **Orchestrator:** Pipecat (Python)
- **Compute:** Google Cloud Run (min 1 instance for 0ms cold start)
- **Telephony:** Twilio (SIP/WebSocket)
- **STT:** Deepgram Nova-2
- **LLM:** Groq Llama 3.1 70B
- **TTS:** OpenAI tts-1 (voice: alloy)
- **Memory:** GCS bucket (transcripts saved on call end)

## Prerequisites

- API keys: [Groq](https://console.groq.com), [Deepgram](https://console.deepgram.com), [OpenAI](https://platform.openai.com)
- GCP project with Cloud Run, GCS, and Artifact Registry enabled
- Twilio account with a voice-capable phone number

## Setup

### 1. Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### 2. Deploy Infrastructure

```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your project_id and ghostbrain_image
terraform init
terraform apply
```

Save the `cloud_run_url` and `bucket_name` outputs.

### 3. Build and Deploy Container

```bash
# Build
docker build -t gcr.io/YOUR_PROJECT_ID/ghostbrain:latest .

# Push (requires gcloud auth)
docker push gcr.io/YOUR_PROJECT_ID/ghostbrain:latest

# Deploy to Cloud Run with secrets
gcloud run deploy ghostbrain-bot \
  --image gcr.io/YOUR_PROJECT_ID/ghostbrain:latest \
  --region us-central1 \
  --set-env-vars "SERVICE_URL=https://ghostbrain-bot-XXXXX-uc.a.run.app" \
  --set-secrets "GROQ_API_KEY=groq-api-key:latest,DEEPGRAM_API_KEY=deepgram-api-key:latest,OPENAI_API_KEY=openai-api-key:latest,TWILIO_ACCOUNT_SID=twilio-account-sid:latest,TWILIO_AUTH_TOKEN=twilio-auth-token:latest"
```

Or set env vars directly (less secure):

```bash
gcloud run services update ghostbrain-bot \
  --region us-central1 \
  --set-env-vars "GROQ_API_KEY=...,DEEPGRAM_API_KEY=...,OPENAI_API_KEY=...,TWILIO_ACCOUNT_SID=...,TWILIO_AUTH_TOKEN=...,GCP_BUCKET_NAME=BUCKET_FROM_TERRAFORM,SERVICE_URL=YOUR_CLOUD_RUN_URL"
```

### 4. Configure Twilio

1. In Twilio Console: Phone Numbers → Manage → Active numbers → select your number
2. Voice Configuration → "A call comes in" → Webhook
3. URL: `https://YOUR_CLOUD_RUN_URL/voice`
4. HTTP: GET

When a call comes in, Twilio fetches TwiML from `/voice`, which starts a Media Stream to `wss://YOUR_CLOUD_RUN_URL/ws`.

## Local Development

```bash
cd src
pip install -r requirements.txt
SERVICE_URL=https://your-ngrok-url.ngrok.io uvicorn bot:app --reload --port 8080
```

Use ngrok to expose your local server for Twilio:

```bash
ngrok http 8080
```

Set `SERVICE_URL` to the ngrok HTTPS URL (Twilio needs wss://, so use the https URL and the code will convert).

## Transcripts

On call end, the conversation is formatted as Markdown with frontmatter and uploaded to the GCS bucket:

```
---
date: 2026-02-15
call_id: CAxxxx
---

**User:** Hello...

**Assistant:** Hi! How can I help?
```

Filename format: `YYYY-MM-DD-CAxxxx.md`
