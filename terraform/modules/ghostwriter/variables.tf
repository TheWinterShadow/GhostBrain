# Ghostwriter module variables.

variable "project_id" {
  description = "GCP project ID."
  type        = string
}

variable "region" {
  description = "GCP region."
  type        = string
}

variable "cloud_run_image" {
  description = "Container image URI for the Cloud Run service."
  type        = string
}

variable "ghostwriter_service_name" {
  description = "Name of the Cloud Run service."
  type        = string
}

variable "bucket_name_prefix" {
  description = "Prefix for the GCS bucket name."
  type        = string
}
