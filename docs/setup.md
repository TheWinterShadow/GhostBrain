# Self-Hosting Setup Guide

Steps to deploy the GhostBrain voice-interviewer bot on your own Google Cloud Platform (GCP) environment with Twilio. The deployment is fully automated via GitHub Actions and Terraform.

---

## 1. Prerequisites

- **GCP project** with billing enabled.
- **gcloud CLI** installed and logged in: `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`.
- **GitHub** repo with the Ghost Brain code (for CI/CD).
- **Accounts and keys:**
  - [Groq](https://console.groq.com/) — API key for `llama-3.3-70b-versatile`.
  - [Deepgram](https://console.deepgram.com/) — API key for STT (nova-2).
  - [OpenAI](https://platform.openai.com/) — API key for TTS (tts-1, alloy).
  - [Twilio](https://console.twilio.com/) — Account SID and Auth Token (and a Voice-capable phone number).

---

## 2. Create Artifact Registry repository (for Docker images)

The GitHub Actions deploy workflow pushes the Docker image to Google Artifact Registry. Create the repo before your first deploy:

```bash
# Set your project and region (e.g. us-central1)
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Enable required APIs
gcloud services enable artifactregistry.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com \
  --project="$PROJECT_ID"

# Create the repository (Docker format)
gcloud artifacts repositories create ghost-brain \
  --repository-format=docker \
  --location="$REGION" \
  --project="$PROJECT_ID" \
  --description="Ghost Brain bot images"
```

---

## 3. (Optional) Remote Terraform state

By default, the pipeline runs without a remote backend, which is generally not recommended for production. To keep state in GCS so you can reliably run Terraform from CI:

1. Create a state bucket and enable versioning:
   ```bash
   gsutil mb -p "$PROJECT_ID" -l "$REGION" gs://$PROJECT_ID-terraform-state
   gsutil versioning set on gs://$PROJECT_ID-terraform-state
   ```

2. Edit `terraform/backend.tf` (uncomment or create it):
   ```hcl
   terraform {
     backend "gcs" {
       bucket = "YOUR_PROJECT_ID-terraform-state"
       prefix = "ghost_brain/state"
     }
   }
   ```

3. If you previously ran Terraform locally, migrate the state: `terraform init -migrate-state`.
4. In `.github/workflows/deploy.yml`, remove `-backend=false` from the `terraform init` steps if you added the remote backend.

---

## 4. Configure GitHub repository secrets

The entire deployment—including securely saving your API keys to GCP Secret Manager—is handled by the GitHub Actions workflow.

1. In your GitHub repository, go to **Settings → Secrets and variables → Actions**.
2. Add the following repository secrets:

| Secret name | Description |
|---|---|
| `GCP_PROJECT_ID` | Your GCP project ID (e.g. `my-project-123`). |
| `GCP_SA_KEY` | JSON key of a GCP service account for GitHub Actions (see below). |
| `GCP_REGISTRY_REGION` | (Optional) Region for Artifact Registry; default is `us-central1`. |
| `GROQ_API_KEY` | Your Groq API key. |
| `DEEPGRAM_API_KEY` | Your Deepgram API key. |
| `OPENAI_API_KEY` | Your OpenAI API key. |
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID. |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token. |
| `ALLOWED_CALLER_ID` | (Optional) Phone number to whitelist. |
| `SYSTEM_INSTRUCTIONS` | (Optional) Custom system prompt for the AI. |

**Creating a service account for GitHub Actions:**

- Create a GCP service account (e.g. `github-actions-deploy`).
- Grant it the following roles:
  - **Artifact Registry Writer**
  - **Cloud Run Admin**
  - **Service Account User** (to attach the runtime SA to Cloud Run)
  - **Secret Manager Admin** (to create secrets)
  - **Storage Admin** (to create the transcript bucket and read/write the Terraform state bucket)
  - **Service Account Admin** & **Project IAM Admin** (to create the runtime SA and bind roles)
- Create a JSON key for this account and paste the contents into the `GCP_SA_KEY` GitHub secret.

---

## 5. Deploy via CI/CD

Push your code (and `backend.tf` changes if any) to the `main` branch.

The `.github/workflows/deploy.yml` workflow will automatically:
1. Lint and test the code.
2. Build the Docker image and push it to Artifact Registry.
3. Run `terraform apply` to provision:
   - GCS bucket for transcripts.
   - Secret Manager secrets (securely populated from your GitHub Secrets).
   - Cloud Run service pointing to the new Docker image.

---

## 6. Connect Twilio: phone number and WebSocket URL

Once the deployment completes successfully, you need to point your Twilio phone number to the newly created Cloud Run service.

1. **Get your Cloud Run URL**: Check the Terraform outputs in the GitHub Actions logs, or find it in the GCP Console under Cloud Run. It will look like `https://ghost-brain-bot-xxxxx-uc.a.run.app`.

2. **Create a TwiML Bin** (Twilio Console → Explore → TwiML Bins):
   - Name: e.g. `Ghost Brain WebSocket`.
   - Body (replace the URL with your Cloud Run URL, changing `https://` to **`wss://`**):

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Response>
     <Connect>
       <Stream url="wss://YOUR_CLOUD_RUN_URL/ws" />
     </Connect>
   </Response>
   ```

3. **Assign the TwiML Bin to a phone number**:
   - Go to Phone Numbers → Manage → Active Numbers.
   - Select your number.
   - Under "Voice configuration", set "A call comes in" to **TwiML Bin** and choose the bin you just created. Save.

---

## 7. Verification

1. **Health Check:** Open `https://YOUR_CLOUD_RUN_URL/health` in a browser. You should see `{"status":"ok"}`.
2. **Call:** Dial your Twilio number. The bot should answer and speak.
3. **Transcripts:** Hang up the call, and check your generated GCS bucket (`ghost_brain-memory-...`); the transcript should appear under `transcripts/<call_sid>.md`.
4. **Logs:** View the Cloud Run logs in the GCP Console to monitor interactions and errors.
