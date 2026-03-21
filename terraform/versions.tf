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
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}
