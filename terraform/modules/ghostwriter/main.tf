# GCS bucket and service account for Ghostwriter.

# Random suffix for globally unique bucket name.
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# Private GCS bucket for transcript storage.
resource "google_storage_bucket" "transcript_bucket" {
  name     = "${var.bucket_name_prefix}-${random_id.bucket_suffix.hex}"
  location = var.region
  project  = var.project_id

  uniform_bucket_level_access = true
  force_destroy               = false

  depends_on = [google_project_service.storage]
}

# Service account for the Cloud Run service.
resource "google_service_account" "ghostwriter_bot" {
  account_id   = "ghostwriter-bot"
  display_name = "Ghostwriter Voice Bot"
  project      = var.project_id
}

# Grant the service account permission to create objects in the bucket.
resource "google_storage_bucket_iam_member" "ghostwriter_bucket_creator" {
  bucket = google_storage_bucket.transcript_bucket.name
  role   = "roles/storage.objectCreator"
  member = "serviceAccount:${google_service_account.ghostwriter_bot.email}"
}
