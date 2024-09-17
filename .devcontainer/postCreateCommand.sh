#!/usr/bin/env bash

set -e

echo "Removing cache..."
rm -rf .venv
echo "Cache removed."
poetry config virtualenvs.in-project true
poetry install -vv
poetry shell

echo "Setting up ownership at repository root..."
git config --global --add safe.directory /workspaces/rag-experiments