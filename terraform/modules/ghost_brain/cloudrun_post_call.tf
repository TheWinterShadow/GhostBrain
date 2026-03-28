resource "google_cloud_run_v2_service" "ghost_brain_post_call" {
  name     = "${var.ghost_brain_service_name}-post-call"
  location = var.region
  project  = var.project_id

  template {
    # We can reuse the same service account or create a specific one.
    # For now, reuse the bot service account since it has GCS access to read the files.
    service_account = google_service_account.ghost_brain_bot.email

    scaling {
      min_instance_count = 0
      max_instance_count = 5
    }

    containers {
      image = var.cloud_run_image

      ports {
        container_port = 8080
      }

      env {
        name  = "GHOST_BRAIN_GCP_BUCKET_NAME"
        value = google_storage_bucket.transcript_bucket.name
      }

      # Secrets available if LLM is needed for post-call processing (e.g., summarizing)
      env {
        name = "GHOST_BRAIN_GROQ_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.groq_api_key.secret_id
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
    google_project_service.run
  ]
}

# The post-call service does not need to be public. It will be invoked by Eventarc.
# We grant the Eventarc trigger's service account permission to invoke this service in eventarc.tf.
