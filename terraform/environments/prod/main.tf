# Root module: Ghost Brain bot infrastructure.

module "ghost_brain" {
  source                   = "../../modules/ghost_brain"
  project_id               = var.project_id
  region                   = var.region
  cloud_run_image          = var.cloud_run_image
  ghost_brain_service_name = var.ghost_brain_service_name
  bucket_name_prefix       = var.bucket_name_prefix

  groq_api_key        = var.groq_api_key
  deepgram_api_key    = var.deepgram_api_key
  openai_api_key      = var.openai_api_key
  twilio_account_sid  = var.twilio_account_sid
  twilio_auth_token   = var.twilio_auth_token
  allowed_caller_id   = var.allowed_caller_id
  system_instructions = var.system_instructions
}

check "service_health" {
  data "http" "health_check" {
    url = "${module.ghost_brain.cloud_run_url}/health"

    retry {
      attempts     = 3
      min_delay_ms = 2000
    }
  }

  assert {
    condition     = data.http.health_check.status_code == 200
    error_message = "Ghost Brain service health check failed. Expected HTTP 200."
  }
}
