# Ghost Brain module outputs.

output "cloud_run_url" {
  description = "Public URL of the Cloud Run service."
  value       = google_cloud_run_v2_service.ghost_brain_bot.uri
}

output "bucket_name" {
  description = "Name of the transcript GCS bucket."
  value       = google_storage_bucket.transcript_bucket.name
}



output "twilio_application_sid" {
  description = "The SID of the Twilio Application created for Ghost Brain."
  value       = twilio_api_accounts_applications.ghost_brain_bot.sid
}
