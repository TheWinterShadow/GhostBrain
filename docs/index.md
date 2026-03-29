---
title: Ghost Brain
description: AI-powered real-time voice virtual assistant. State-of-the-art speech recognition, language models, and voice synthesis.
icon: fontawesome/solid/ghost
hide:
  - navigation
  - toc
---

# Ghost Brain :fontawesome-solid-ghost:

**AI-powered real-time voice virtual assistant** — conduct natural, sub-second latency conversations through phone calls or your local microphone.

[![Deploy](https://img.shields.io/github/actions/workflow/status/TheWinterShadow/GhostBrain/deploy.yml?branch=main&logo=googlecloud&label=Deploy)](https://github.com/TheWinterShadow/GhostBrain/actions/workflows/deploy.yml)
[![Docs](https://img.shields.io/github/actions/workflow/status/TheWinterShadow/GhostBrain/docs.yml?branch=main&logo=markdown&label=Docs)](https://github.com/TheWinterShadow/GhostBrain/actions/workflows/docs.yml)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/TheWinterShadow/GhostBrain/blob/main/LICENSE)
[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Terraform](https://img.shields.io/badge/terraform-%235835CC.svg?style=flat&logo=terraform&logoColor=white)](https://www.terraform.io/)

---

<div class="grid cards" markdown>

-   :material-microphone-message: **Real-time voice**

    ---

    Achieve sub-second latency for natural conversations using the Pipecat real-time audio processing pipeline.

-   :fontawesome-solid-phone-volume: **Phone integration**

    ---

    Native support for Twilio telephony. Connect a phone number and let callers interact directly with the AI via WebSockets.

-   :simple-googlecloud: **Cloud-native**

    ---

    Deploy instantly to Google Cloud Run with zero-downtime scalability. Includes complete Terraform infrastructure-as-code setup.

-   :material-brain: **Advanced AI stack**

    ---

    Powered by **Deepgram Nova-2** (STT), **Llama 3.1 70B** via Groq (LLM), and **OpenAI TTS-1** for the most intelligent and natural voice synthesis.

</div>

---

## Quick start

Test GhostBrain locally with your microphone — no Twilio setup required.

=== ":fontawesome-brands-python: hatch"

    ```bash title="Run locally"
    # 1. Install dependencies
    pip install hatch pyaudio

    # 2. Set up API keys in .env
    cat > .env << 'EOF'
    GHOST_BRAIN_DEEPGRAM_API_KEY="your-deepgram-key"
    GHOST_BRAIN_GROQ_API_KEY="your-groq-key"
    GHOST_BRAIN_OPENAI_API_KEY="your-openai-key"
    GHOST_BRAIN_ANTHROPIC_API_KEY="your-anthropic-key"
    EOF

    # 3. Run local microphone test
    hatch run python -m ghost_brain.local_mic_test
    ```

=== ":simple-googlecloud: Cloud Run (Deploy)"

    ```bash title="Provision infrastructure"
    # Deploy the entire stack using Terraform
    cd terraform/environments/prod
    terraform init
    terraform apply -var="project_id=your-gcp-project"
    ```

---

## Features at a glance

<div class="grid cards" markdown>

-   :material-text-recognition: **Automatic transcription**

    ---

    Every conversation is automatically transcribed and uploaded to a secure Google Cloud Storage bucket when the call ends.

-   :material-file-document-multiple-outline: **Intelligent File Splitting**

    ---

    Post-call processing uses **Anthropic Claude 3.5 Sonnet** to intelligently parse your transcripts, split them by topic, and format them into beautiful Markdown templates (e.g. Daily Logs, Project Ideas) that are saved back to your cloud storage.

-   :material-lightning-bolt: **Decoupled Architecture**

    ---

    Eventarc triggers a secondary serverless Cloud Run processor to analyze transcripts without stealing CPU or causing latency for live voice callers.

-   :material-laptop: **Local testing**

    ---

    Develop and test completely locally using PyAudio or Daily WebRTC before ever deploying to the cloud.

</div>

---

## Where to go next

<div class="grid cards" markdown>

-   [**:material-information-outline: Architecture**](architecture/index.md){ .md-button }

    Learn how the pipeline flows from audio capture to LLM response and TTS generation.

-   [**:material-rocket-launch: Setup Guide**](self-hosting/index.md){ .md-button .md-button--primary }

    Deploy your own production Ghost Brain instance using Google Cloud and Twilio.

-   [**:material-laptop: Local Testing**](local-testing/index.md){ .md-button }

    Detailed guide on testing with your microphone and debugging the AI pipeline.

-   [**:material-code-tags: API Reference**](api/app.md){ .md-button }

    MkDocs-generated code documentation for all modules and pipeline runners.

</div>
