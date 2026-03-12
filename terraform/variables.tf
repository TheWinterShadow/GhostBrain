# Root module variables for Ghostwriter deployment.

variable "project_id" {
  description = "GCP project ID where resources will be created."
  type        = string
}

variable "region" {
  description = "GCP region for Cloud Run and supporting resources."
  type        = string
  default     = "us-central1"
}

variable "cloud_run_image" {
  description = "Container image URI for the Ghostwriter bot (e.g. gcr.io/PROJECT_ID/ghostwriter-bot:latest)."
  type        = string
}

variable "ghostwriter_service_name" {
  description = "Name of the Cloud Run service."
  type        = string
  default     = "ghostwriter-bot"
}

variable "bucket_name_prefix" {
  description = "Prefix for the GCS bucket name (suffix is random for uniqueness)."
  type        = string
  default     = "ghostwriter-memory"
}
