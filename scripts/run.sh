#!/bin/bash

set -e

echo "Starting backend server..."
python3 app.py &

sleep 3  # Wait a few seconds to ensure the backend is up

echo "Launching Streamlit app..."
streamlit run streamlit_app.py
