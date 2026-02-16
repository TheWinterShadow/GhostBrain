terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run"
  type        = string
  default     = "us-central1"
}

variable "ghostbrain_image" {
  description = "Container image for GhostBrain (e.g. gcr.io/PROJECT_ID/ghostbrain:latest)"
  type        = string
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Unique suffix for bucket name
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# GCS bucket for transcript storage
resource "google_storage_bucket" "ghostbrain_memory" {
  name                        = "ghostbrain-memory-${random_id.bucket_suffix.hex}"
  location                    = upper(var.region)
  force_destroy               = false
  uniform_bucket_level_access = true
  public_access_prevention    = "enforced"
}

# Service account for Cloud Run
resource "google_service_account" "ghostbrain" {
  account_id   = "ghostbrain-bot"
  display_name = "GhostBrain Voice Bot"
}

# Grant objectCreator on the bucket to the service account
resource "google_storage_bucket_iam_member" "ghostbrain_creator" {
  bucket = google_storage_bucket.ghostbrain_memory.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.ghostbrain.email}"
}

# Cloud Run service
resource "google_cloud_run_v2_service" "ghostbrain_bot" {
  name     = "ghostbrain-bot"
  location = var.region
  ingress  = "INGRESS_TRAFFIC_ALL"

  template {
    service_account = google_service_account.ghostbrain.email

    scaling {
      min_instance_count = 1
      max_instance_count = 10
    }

    containers {
      image = var.ghostbrain_image

      ports {
        container_port = 8080
      }

      env {
        name  = "GCP_BUCKET_NAME"
        value = google_storage_bucket.ghostbrain_memory.name
      }

      # SERVICE_URL must be set at deploy time (use cloud_run_url output)
      # e.g. gcloud run services update ghostbrain-bot --update-env-vars SERVICE_URL=https://...

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

  lifecycle {
    ignore_changes = [
      template[0].containers[0].env,
    ]
  }
}

# Allow unauthenticated invocations (for Twilio webhooks)
resource "google_cloud_run_v2_service_iam_member" "ghostbrain_public" {
  location = google_cloud_run_v2_service.ghostbrain_bot.location
  name     = google_cloud_run_v2_service.ghostbrain_bot.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

output "cloud_run_url" {
  description = "Public URL of the GhostBrain Cloud Run service"
  value       = google_cloud_run_v2_service.ghostbrain_bot.uri
}

output "bucket_name" {
  description = "GCS bucket name for transcript storage"
  value       = google_storage_bucket.ghostbrain_memory.name
}
