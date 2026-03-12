# Root module outputs for Ghostwriter deployment.

output "cloud_run_url" {
  description = "Public URL of the Ghostwriter Cloud Run service."
  value       = module.ghostwriter.cloud_run_url
}

output "bucket_name" {
  description = "Name of the GCS bucket used for transcript storage."
  value       = module.ghostwriter.bucket_name
}

output "service_account_email" {
  description = "Email of the Cloud Run service account."
  value       = module.ghostwriter.service_account_email
}
