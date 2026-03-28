#!/usr/bin/env bash
set -e

echo "Generating Terraform Documentation..."
cd terraform/modules/ghost_brain
terraform-docs .
cd ../../..

echo "Building Zensical Site (API docs auto-generated via mkdocstrings)..."
hatch run zensical build
echo "Done!"
