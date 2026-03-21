# Ghost Brain module variables.

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

variable "ghost_brain_service_name" {
  description = "Name of the Cloud Run service."
  type        = string
}

variable "bucket_name_prefix" {
  description = "Prefix for the GCS bucket name."
  type        = string
}

# Sensitive variables passed from root
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
