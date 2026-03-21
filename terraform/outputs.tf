# Root module outputs for Ghost Brain deployment.

output "cloud_run_url" {
  description = "Public URL of the Ghost Brain Cloud Run service."
  value       = module.ghost_brain.cloud_run_url
}

output "bucket_name" {
  description = "Name of the GCS bucket used for transcript storage."
  value       = module.ghost_brain.bucket_name
}

output "service_account_email" {
  description = "Email of the Cloud Run service account."
  value       = module.ghost_brain.service_account_email
}
