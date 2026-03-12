# Ghostwriter deployment guide

Steps to get the Ghostwriter voice-interviewer bot running on Google Cloud Run with Twilio.

---

## 1. Prerequisites

- **GCP project** with billing enabled.
- **gcloud CLI** installed and logged in: `gcloud auth login` and `gcloud config set project YOUR_PROJECT_ID`.
- **Terraform** 1.5+ installed locally (for first-time infra or manual apply).
- **GitHub** repo with the Ghostwriter code (for CI/CD).
- **Accounts and keys:**
  - [Groq](https://console.groq.com/) — API key for `llama-3.1-70b-versatile`.
  - [Deepgram](https://console.deepgram.com/) — API key for STT (nova-2).
  - [OpenAI](https://platform.openai.com/) — API key for TTS (tts-1, alloy).
  - [Twilio](https://console.twilio.com/) — Account SID and Auth Token (and a Voice-capable phone number).

---

## 2. Create Artifact Registry repository (for Docker images)

The deploy workflow pushes the image to Artifact Registry. Create the repo if it does not exist:

```bash
# Set your project and region (e.g. us-central1)
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"

# Enable Artifact Registry API
gcloud services enable artifactregistry.googleapis.com --project="$PROJECT_ID"

# Create the repository (Docker format)
gcloud artifacts repositories create ghostwriter \
  --repository-format=docker \
  --location="$REGION" \
  --project="$PROJECT_ID" \
  --description="Ghostwriter bot images"
```

The workflow expects the image at:  
`$REGION-docker.pkg.dev/$PROJECT_ID/ghostwriter/ghostwriter-bot:latest`.

---

## 3. First-time Terraform apply (local)

Bootstrap infrastructure once so the bucket, service account, secrets, and Cloud Run service exist. Use a placeholder image for the first apply; CI will replace it on first deploy.

```bash
cd terraform

# Initialize (no backend, or uncomment backend.tf and set bucket/prefix)
terraform init

# Plan with a placeholder image (replace with your project ID)
export TF_VAR_project_id="$PROJECT_ID"
export TF_VAR_cloud_run_image="$REGION-docker.pkg.dev/$PROJECT_ID/ghostwriter/ghostwriter-bot:latest"

terraform plan -out=tfplan

# Apply
terraform apply tfplan
```

Note the outputs: `cloud_run_url`, `bucket_name`, `service_account_email`. You will need the **Cloud Run URL** for Twilio.

---

## 4. Populate Secret Manager with real values

Terraform creates secrets with placeholder versions. Add real values (no quotes, no newlines):

```bash
# Groq API key
echo -n "YOUR_GROQ_API_KEY" | gcloud secrets versions add ghostwriter-groq-api-key --data-file=- --project="$PROJECT_ID"

# Deepgram API key
echo -n "YOUR_DEEPGRAM_API_KEY" | gcloud secrets versions add ghostwriter-deepgram-api-key --data-file=- --project="$PROJECT_ID"

# OpenAI API key
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets versions add ghostwriter-openai-api-key --data-file=- --project="$PROJECT_ID"

# Twilio Account SID
echo -n "YOUR_TWILIO_ACCOUNT_SID" | gcloud secrets versions add ghostwriter-twilio-account-sid --data-file=- --project="$PROJECT_ID"

# Twilio Auth Token
echo -n "YOUR_TWILIO_AUTH_TOKEN" | gcloud secrets versions add ghostwriter-twilio-auth-token --data-file=- --project="$PROJECT_ID"
```

Cloud Run will use the **latest** version of each secret. To rotate a key, add a new version; the next revision will pick it up.

---

## 5. Configure GitHub repository secrets

For the **Deploy** workflow to build the image and run Terraform:

1. In GitHub: **Settings → Secrets and variables → Actions**.
2. Add these repository secrets:

| Secret name            | Description |
|------------------------|-------------|
| `GCP_SA_KEY`           | JSON key of a GCP service account that can push to Artifact Registry, run Cloud Run, and run Terraform (see below). |
| `GCP_PROJECT_ID`       | Your GCP project ID (e.g. `my-project-123`). |
| `GCP_REGISTRY_REGION`  | (Optional) Region for Artifact Registry; default is `us-central1` if unset. |

**Creating a service account for GitHub Actions:**

- Create a GCP service account (e.g. `github-actions-deploy`).
- Grant it at least:
  - **Artifact Registry:** Artifact Registry Writer (or equivalent) on the `ghostwriter` repo.
  - **Cloud Run:** Cloud Run Admin, Service Account User (for the Ghostwriter SA).
  - **Terraform resources:** Secret Manager Admin (or enough to reference secrets), Storage Admin (if using GCS backend), and any roles needed to create/update the resources in `terraform/modules/ghostwriter` (e.g. Service Account Admin, Storage Admin for the bucket).
- Create a JSON key and paste the entire contents into the `GCP_SA_KEY` secret.

---

## 6. Twilio: phone number and WebSocket URL

1. **Get your Cloud Run URL**  
   From Terraform output:  
   `terraform -chdir=terraform output -raw cloud_run_url`  
   Example: `https://ghostwriter-bot-xxxxx-uc.a.run.app`.

2. **Create a TwiML Bin** (Twilio Console → Explore → TwiML Bins):
   - Name: e.g. `Ghostwriter WebSocket`.
   - Body (replace the URL with your Cloud Run URL, **wss** for secure WebSocket):

   ```xml
   <?xml version="1.0" encoding="UTF-8"?>
   <Response>
     <Connect>
       <Stream url="wss://YOUR_CLOUD_RUN_URL/ws" />
     </Connect>
   </Response>
   ```

3. **Assign the TwiML Bin to a phone number**  
   Phone Numbers → Manage → Active Numbers → select your number → under "Voice configuration", set "A call comes in" to **TwiML Bin** and choose the bin above. Save.

Calls to that number will connect to your bot’s `/ws` endpoint.

---

## 7. (Optional) Remote Terraform state

To keep state in GCS and optionally run Terraform from CI with a shared state:

1. Create a bucket and enable versioning:
   ```bash
   gsutil mb -p "$PROJECT_ID" -l "$REGION" gs://$PROJECT_ID-terraform-state
   gsutil versioning set on gs://$PROJECT_ID-terraform-state
   ```

2. Uncomment and edit `terraform/backend.tf`:
   ```hcl
   terraform {
     backend "gcs" {
       bucket = "YOUR_PROJECT_ID-terraform-state"
       prefix = "ghostwriter/state"
     }
   }
   ```

3. Run `terraform init` again (and `terraform migrate` if you had local state).

4. In the deploy workflow, change `terraform init -backend=false` to `terraform init` and ensure the GitHub Actions service account has **Storage Object Admin** (or equivalent) on the state bucket.

---

## 8. Deploy and verify

- **Via GitHub:** Push to `main`. The **Deploy** workflow will build the image, push to Artifact Registry, and run `terraform apply` with the new image.

- **Manual deploy (image only):** Build and push the image, then either run Terraform apply with the new image tag or use `gcloud run deploy`:
  ```bash
  docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/ghostwriter/ghostwriter-bot:latest .
  docker push $REGION-docker.pkg.dev/$PROJECT_ID/ghostwriter/ghostwriter-bot:latest
  gcloud run services update ghostwriter-bot --image=$REGION-docker.pkg.dev/$PROJECT_ID/ghostwriter/ghostwriter-bot:latest --region=$REGION --project=$PROJECT_ID
  ```

**Verification:**

1. **Health:** Open `https://YOUR_CLOUD_RUN_URL/health` in a browser; expect `{"status":"ok"}`.
2. **Call:** Dial your Twilio number; the bot should answer and speak (Ghostwriter greeting). Hang up; the transcript should appear in the GCS bucket under `transcripts/<call_sid>.md`.
3. **Logs:** `gcloud run services logs read ghostwriter-bot --region=$REGION --project=$PROJECT_ID`.

---

## 9. Troubleshooting

| Issue | What to check |
|-------|----------------|
| 502 / WebSocket fails | Cloud Run URL must use **https**; TwiML must use **wss**. Ensure the service allows unauthenticated invocations (Terraform: `google_cloud_run_v2_service_iam_member.public_invoke`). |
| No audio / bot doesn’t speak | Confirm all five secrets have a non-placeholder version. Check Cloud Run logs for missing env or API errors. |
| Transcript not in GCS | Check that `GCP_BUCKET_NAME` is set on the Cloud Run service (Terraform sets it from the bucket name). Ensure the Cloud Run service account has `roles/storage.objectCreator` on the bucket. |
| GitHub Deploy fails on push | Verify `GCP_SA_KEY` and `GCP_PROJECT_ID`. Ensure the Artifact Registry repo exists and the SA can push images and run Terraform (and use the state bucket if applicable). |
| Terraform apply fails (e.g. secret not found) | Run the `gcloud secrets versions add` commands in step 4. If the secret resource was just created, wait a few seconds and retry. |

---

## 10. Summary checklist

- [ ] GCP project and gcloud CLI configured
- [ ] Artifact Registry repo `ghostwriter` created in the chosen region
- [ ] Terraform applied once (bucket, SA, secrets, Cloud Run) with correct `project_id` and `cloud_run_image`
- [ ] All five Secret Manager secrets updated with real values (Groq, Deepgram, OpenAI, Twilio SID, Twilio token)
- [ ] GitHub repo secrets set: `GCP_SA_KEY`, `GCP_PROJECT_ID` (and optionally `GCP_REGISTRY_REGION`)
- [ ] TwiML Bin created with `wss://YOUR_CLOUD_RUN_URL/ws` and assigned to a Twilio phone number
- [ ] (Optional) GCS backend configured for Terraform and deploy workflow updated
- [ ] Push to `main` and confirm Deploy workflow succeeds; call the number and confirm transcript in GCS
