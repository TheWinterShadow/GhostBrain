# Secret Manager secrets for API keys and Twilio credentials.
# Secrets are created with a placeholder version; add real values via:
#   gcloud secrets versions add SECRET_ID --data-file=-
# or via the GCP Console.

resource "google_secret_manager_secret" "groq_api_key" {
  secret_id = "ghostwriter-groq-api-key"
  project   = var.project_id

  replication {
    auto {}
  }

  depends_on = [google_project_service.secretmanager]
}

resource "google_secret_manager_secret_version" "groq_api_key_placeholder" {
  secret      = google_secret_manager_secret.groq_api_key.id
  secret_data = "replace-me"
}

resource "google_secret_manager_secret" "deepgram_api_key" {
  secret_id = "ghostwriter-deepgram-api-key"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "deepgram_api_key_placeholder" {
  secret      = google_secret_manager_secret.deepgram_api_key.id
  secret_data = "replace-me"
}

resource "google_secret_manager_secret" "openai_api_key" {
  secret_id = "ghostwriter-openai-api-key"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "openai_api_key_placeholder" {
  secret      = google_secret_manager_secret.openai_api_key.id
  secret_data = "replace-me"
}

resource "google_secret_manager_secret" "twilio_account_sid" {
  secret_id = "ghostwriter-twilio-account-sid"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "twilio_account_sid_placeholder" {
  secret      = google_secret_manager_secret.twilio_account_sid.id
  secret_data = "replace-me"
}

resource "google_secret_manager_secret" "twilio_auth_token" {
  secret_id = "ghostwriter-twilio-auth-token"
  project   = var.project_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "twilio_auth_token_placeholder" {
  secret      = google_secret_manager_secret.twilio_auth_token.id
  secret_data = "replace-me"
}

# Grant Cloud Run service account access to read secrets.
resource "google_secret_manager_secret_iam_member" "groq_api_key" {
  secret_id = google_secret_manager_secret.groq_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghostwriter_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "deepgram_api_key" {
  secret_id = google_secret_manager_secret.deepgram_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghostwriter_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "openai_api_key" {
  secret_id = google_secret_manager_secret.openai_api_key.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghostwriter_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "twilio_account_sid" {
  secret_id = google_secret_manager_secret.twilio_account_sid.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghostwriter_bot.email}"
}

resource "google_secret_manager_secret_iam_member" "twilio_auth_token" {
  secret_id = google_secret_manager_secret.twilio_auth_token.id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.ghostwriter_bot.email}"
}
