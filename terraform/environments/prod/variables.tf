# Root module variables for Ghost Brain deployment.

variable "project_id" {
  description = "GCP project ID where resources will be created."
  type        = string

  validation {
    condition     = length(var.project_id) > 0
    error_message = "Project ID must not be empty."
  }
}

variable "region" {
  description = "GCP region for Cloud Run and supporting resources."
  type        = string
  default     = "us-central1"

  validation {
    condition     = can(regex("^[a-z]+-[a-z]+\\d+$", var.region))
    error_message = "Region must be a valid GCP region name (e.g., us-central1)."
  }
}

variable "cloud_run_image" {
  description = "Container image URI for the Ghost Brain bot (e.g. gcr.io/PROJECT_ID/ghost_brain-bot:latest)."
  type        = string
}

variable "ghost_brain_service_name" {
  description = "Name of the Cloud Run service."
  type        = string
  default     = "ghost-brain-bot"
}

variable "bucket_name_prefix" {
  description = "Prefix for the GCS bucket name (suffix is random for uniqueness)."
  type        = string
  default     = "ghost_brain-memory"

  validation {
    condition     = length(var.bucket_name_prefix) > 0 && length(var.bucket_name_prefix) <= 50
    error_message = "Bucket name prefix must be between 1 and 50 characters."
  }
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

variable "allowed_caller_id" {
  description = "Allowed caller ID to whitelist"
  type        = string
  sensitive   = true
  default     = ""
}

variable "system_instructions" {
  description = "System instructions for the AI personality"
  type        = string
  sensitive   = true
  default     = ""
}

variable "anthropic_api_key" {
  description = "Anthropic API Key"
  type        = string
  sensitive   = true
}
