resource "google_cloud_run_v2_service" "ghost_brain_bot" {
  name     = var.ghost_brain_service_name
  location = var.region
  project  = var.project_id

  template {
    service_account = google_service_account.ghost_brain_bot.email

    scaling {
      min_instance_count = 0
      max_instance_count = 10
    }

    timeout = "3600s"

    containers {
      image = var.cloud_run_image

      ports {
        container_port = 8080
      }

      env {
        name  = "GHOST_BRAIN_GCP_BUCKET_NAME"
        value = google_storage_bucket.transcript_bucket.name
      }

      env {
        name  = "GHOST_BRAIN_ALLOWED_CALLER_ID"
        value = var.allowed_caller_id
      }

      env {
        name  = "GHOST_BRAIN_SYSTEM_INSTRUCTIONS"
        value = var.system_instructions
      }

      env {
        name = "GHOST_BRAIN_GROQ_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.groq_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GHOST_BRAIN_DEEPGRAM_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.deepgram_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GHOST_BRAIN_OPENAI_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.openai_api_key.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GHOST_BRAIN_TWILIO_ACCOUNT_SID"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.twilio_account_sid.secret_id
            version = "latest"
          }
        }
      }

      env {
        name = "GHOST_BRAIN_TWILIO_AUTH_TOKEN"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.twilio_auth_token.secret_id
            version = "latest"
          }
        }
      }

      resources {
        limits = {
          cpu    = "1"
          memory = "512Mi"
        }
      }
    }
  }

  traffic {
    type    = "TRAFFIC_TARGET_ALLOCATION_TYPE_LATEST"
    percent = 100
  }

  depends_on = [
    google_project_service.run,
    google_secret_manager_secret.groq_api_key,
    google_secret_manager_secret.deepgram_api_key,
    google_secret_manager_secret.openai_api_key,
    google_secret_manager_secret.twilio_account_sid,
    google_secret_manager_secret.twilio_auth_token,
  ]
}

# Allow unauthenticated invocations so Twilio can reach the WebSocket endpoint.
resource "google_cloud_run_v2_service_iam_member" "public_invoke" {
  location = google_cloud_run_v2_service.ghost_brain_bot.location
  name     = google_cloud_run_v2_service.ghost_brain_bot.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}
