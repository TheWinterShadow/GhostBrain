# Secret Manager secrets for API keys and Twilio credentials.
# Secrets are created with the provided variable values.

resource "google_secret_manager_secret" "groq_api_key" {
  secret_id = "ghost_brain-groq-api-key"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret_version" "groq_api_key" {
  secret      = google_secret_manager_secret.groq_api_key.id
  secret_data = var.groq_api_key
}

resource "google_secret_manager_secret" "deepgram_api_key" {
  secret_id = "ghost_brain-deepgram-api-key"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "deepgram_api_key" {
  secret      = google_secret_manager_secret.deepgram_api_key.id
  secret_data = var.deepgram_api_key
}

resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "ghost_brain-openai-api-key"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "openai_api_key" {
  secret      = google_secret_manager_secret.openai_api_key.id
  secret_data = var.openai_api_key
}

resource "google_secret_manager_secret" "twilio_account_sid" {
  secret_id = "ghost_brain-twilio-account-sid"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "twilio_account_sid" {
  secret      = google_secret_manager_secret.twilio_account_sid.id
  secret_data = var.twilio_account_sid
}

resource "google_secret_manager_secret" "twilio_auth_token" {
  secret_id = "ghost_brain-twilio-auth-token"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "twilio_auth_token" {
  secret      = google_secret_manager_secret.twilio_auth_token.id
  secret_data = var.twilio_auth_token
}

# Grant Cloud Run service account access to read secrets.
resource "google_secret_manager_secret_iam_member" "groq_api_key" {
  secret_id = google_secret_manager_secret.groq_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghost_brain_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "deepgram_api_key" {
  secret_id = google_secret_manager_secret.deepgram_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghost_brain_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "openai_api_key" {
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghost_brain_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "twilio_account_sid" {
  secret_id = google_secret_manager_secret.twilio_account_sid.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghost_brain_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "twilio_auth_token" {
  secret_id = google_secret_manager_secret.twilio_auth_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghost_brain_bot.email}"
}
