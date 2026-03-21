# Project status

## Overview

| Item        | Status |
| ----------- | ------ |
| Build       | Passing (see CI) |
| Deploy      | Cloud Run via GitHub Actions |
| Docs        | Zensical + Sphinx (this site) |
| Tests       | pytest in `tests/` |

## Components

- **Application:** `src/ghost_brain/` — FastAPI WebSocket at `/ws`, Pipecat pipeline (Deepgram STT, Groq LLM, OpenAI TTS), transcript upload to GCS on disconnect.
- **Infrastructure:** `terraform/` — GCS bucket, Secret Manager secrets, Cloud Run service.
- **CI/CD:** `.github/workflows/` — Lint, test, Terraform plan/apply, Docker build and deploy.

## Local development

```bash
hatch run test
hatch run uvicorn ghost_brain.app:app --host 0.0.0.0 --port 8080
```
