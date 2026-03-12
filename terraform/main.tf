# Root module: Ghostwriter bot infrastructure.

module "ghostwriter" {
  source = "./modules/ghostwriter"

  project_id               = var.project_id
  region                   = var.region
  cloud_run_image          = var.cloud_run_image
  ghostwriter_service_name = var.ghostwriter_service_name
  bucket_name_prefix       = var.bucket_name_prefix
}
