#!/usr/bin/env bash
# Build combined docs: Sphinx API reference + Zensical site.
# Sphinx output is copied into site/api/ so one deployment serves both.

set -euo pipefail
cd "$(dirname "$0")/.."

echo "Building Sphinx API docs..."
sphinx-build -b html docs/sphinx docs/sphinx/_build/html

echo "Building Zensical site..."
zensical build

echo "Copying API docs into site/api/..."
mkdir -p site/api
cp -r docs/sphinx/_build/html/* site/api/

echo "Done. Combined site is in site/"
