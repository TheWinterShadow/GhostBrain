# Root module outputs for Ghost Brain deployment.

output "cloud_run_url" {
  description = "Public URL of the Ghost Brain Cloud Run service."
  value       = module.ghost_brain.cloud_run_url
}

output "bucket_name" {
  description = "Name of the GCS bucket used for transcript storage."
  value       = module.ghost_brain.bucket_name
}


output "twilio_application_sid" {
  description = "The SID of the Twilio Application created for Ghost Brain. Assign this to your phone number."
  value       = module.ghost_brain.twilio_application_sid
}
