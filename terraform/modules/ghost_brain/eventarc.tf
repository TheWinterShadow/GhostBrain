# Enable Eventarc API
resource "google_project_service" "eventarc" {
  project            = var.project_id
  service            = "eventarc.googleapis.com"
  disable_on_destroy = false
}

resource "google_project_service" "pubsub" {
  project            = var.project_id
  service            = "pubsub.googleapis.com"
  disable_on_destroy = false
}

# Service account for Eventarc trigger
resource "google_service_account" "eventarc_trigger_sa" {
  account_id   = "ghostbrain-eventarc-sa"
  display_name = "Ghost Brain Eventarc Trigger SA"
  project      = var.project_id
}

# Grant Eventarc SA permission to receive events
resource "google_project_iam_member" "eventarc_event_receiver" {
  project = var.project_id
  role    = "roles/eventarc.eventReceiver"
  member  = "serviceAccount:${google_service_account.eventarc_trigger_sa.email}"
}

# Grant Eventarc SA permission to invoke the post-call Cloud Run service
resource "google_cloud_run_v2_service_iam_member" "eventarc_invoker" {
  location = google_cloud_run_v2_service.ghost_brain_post_call.location
  name     = google_cloud_run_v2_service.ghost_brain_post_call.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.eventarc_trigger_sa.email}"
}

# Eventarc trigger for GCS object finalization (file upload)
resource "google_eventarc_trigger" "post_call_trigger" {
  name     = "${var.ghost_brain_service_name}-post-call-trigger"
  location = var.region
  project  = var.project_id

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.storage.object.v1.finalized"
  }

  matching_criteria {
    attribute = "bucket"
    value     = google_storage_bucket.transcript_bucket.name
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.ghost_brain_post_call.name
      region  = var.region
      path    = "/events/post-call"
    }
  }

  service_account = google_service_account.eventarc_trigger_sa.email

  depends_on = [
    google_project_service.eventarc,
    google_project_service.pubsub,
    google_project_iam_member.eventarc_event_receiver,
    google_cloud_run_v2_service_iam_member.eventarc_invoker
  ]
}
