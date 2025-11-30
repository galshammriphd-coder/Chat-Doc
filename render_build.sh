#!/usr/bin/env bash
# Exit on error
set -o errexit

echo "Current directory: $(pwd)"
ls -la

if [ -d "backend" ]; then
  echo "Found backend directory, entering..."
  cd backend
else
  echo "Backend directory not found in root!"
  # Fallback: maybe we are already in backend?
  if [ -f "requirements.txt" ]; then
    echo "requirements.txt found in current directory."
  else
    echo "ERROR: Cannot find backend directory or requirements.txt"
    exit 1
  fi
fi

echo "Installing dependencies..."
pip install -r requirements.txt
