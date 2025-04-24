#!/bin/bash

set -e

if [ -z "$IN_DOCKER" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
  source venv/bin/activate
fi

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Downloading job postings dataset..."
python3 <<EOF
import gdown, os

file_id = "1zEvQIw8YyuU7vyRJiLK5JloaxAOoioat"
output_path = "/app/chroma_db_backup.tar.gz"

if os.path.exists(output_path):
    print(f"File already exists: {output_path} — skipping download.")
else:
    print("Downloading data...")
    gdown.download(id=file_id, output=output_path, quiet=False)
EOF
