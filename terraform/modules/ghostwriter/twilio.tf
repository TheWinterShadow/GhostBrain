resource "twilio_api_accounts_applications" "ghost_brain_bot" {
  friendly_name = "Ghost Brain Bot (${var.project_id})"
  voice_url     = "${google_cloud_run_v2_service.ghost_brain_bot.uri}/incoming-call"
  voice_method  = "POST"
}
