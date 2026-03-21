# Provider configuration for Ghost Brain infrastructure.

provider "google" {
  project = var.project_id
  region  = var.region
}

provider "random" {}
