#!/bin/bash

echo "Stopping backend (app.py)..."
pkill -f "python3 app.py" || echo "No backend process found."

echo "Stopping Streamlit app..."
pkill -f "streamlit run streamlit_app.py" || echo "No Streamlit process found."

echo "Application stopped."