# Root module variables for Ghost Brain deployment.

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
  description = "Container image URI for the Ghost Brain bot (e.g. gcr.io/PROJECT_ID/ghost_brain-bot:latest)."
  type        = string
}

variable "ghost_brain_service_name" {
  description = "Name of the Cloud Run service."
  type        = string
  default     = "ghost_brain-bot"
}

variable "bucket_name_prefix" {
  description = "Prefix for the GCS bucket name (suffix is random for uniqueness)."
  type        = string
  default     = "ghost_brain-memory"
}

# Sensitive variables for secrets
variable "groq_api_key" {
  description = "Groq API Key"
  type        = string
  sensitive   = true
}

variable "deepgram_api_key" {
  description = "Deepgram API Key"
  type        = string
  sensitive   = true
}

variable "openai_api_key" {
  description = "OpenAI API Key"
  type        = string
  sensitive   = true
}

variable "twilio_account_sid" {
  description = "Twilio Account SID"
  type        = string
  sensitive   = true
}

variable "twilio_auth_token" {
  description = "Twilio Auth Token"
  type        = string
  sensitive   = true
}
