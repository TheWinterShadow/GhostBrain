terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    twilio = {
      source  = "twilio/twilio"
      version = ">= 0.18.0"
    }
  }
}
