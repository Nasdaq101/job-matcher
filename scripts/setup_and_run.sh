#!/bin/bash

set -e

echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate  # On Windows: use venv\Scripts\activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Downloading job postings dataset..."
python3 <<EOF
import gdown, os

file_id = "1rQ-aLkdIBa2Qv-em4KB4C4D0w3GBXStP"
output_path = "data/raw_data/postings.csv"

os.makedirs(os.path.dirname(output_path), exist_ok=True)

if os.path.exists(output_path):
    print(f"File already exists: {output_path} — skipping download.")
else:
    print("Downloading data...")
    gdown.download(id=file_id, output=output_path, quiet=False)
EOF

echo "Building vector database..."
python3 -m preprocess.clean_data
python3 -m embedding.vector_embedding
python3 -m vector_db.build_vector_db

echo "Starting backend server..."
python3 app.py &

sleep 3  # Wait a few seconds to ensure the backend is up

echo "Launching Streamlit app..."
streamlit run streamlit_app.py