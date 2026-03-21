# Provider configuration for Ghost Brain infrastructure.

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "random" {}

provider "twilio" {
  username = var.twilio_account_sid
  password = var.twilio_auth_token
}
