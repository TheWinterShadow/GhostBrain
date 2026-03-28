# Terraform and provider version constraints for Ghost Brain infrastructure.

terraform {
  required_version = ">= 1.5.0"

  cloud {
    organization = "TheWinterShadow"

    workspaces {
      name = "ghost-brain"
    }
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
    twilio = {
      source  = "twilio/twilio"
      version = ">= 0.18.0"
    }
    http = {
      source  = "hashicorp/http"
      version = "~> 3.4.0"
    }
  }
}
