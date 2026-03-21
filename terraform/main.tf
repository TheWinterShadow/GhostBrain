# Root module: Ghost Brain bot infrastructure.

module "ghost_brain" {
  source = "./modules/ghostwriter"

  project_id               = var.project_id
  region                   = var.region
  cloud_run_image          = var.cloud_run_image
  ghost_brain_service_name = var.ghost_brain_service_name
  bucket_name_prefix       = var.bucket_name_prefix

  # Pass secrets
  groq_api_key       = var.groq_api_key
  deepgram_api_key   = var.deepgram_api_key
  openai_api_key     = var.openai_api_key
  twilio_account_sid = var.twilio_account_sid
  twilio_auth_token  = var.twilio_auth_token
}
