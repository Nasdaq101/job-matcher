import os
import subprocess
import threading

def start_fastapi():
    subprocess.run(["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"])

def start_streamlit():
    # Get port from environment variable or default to 8501
    port = os.environ.get("PORT", "8501")
    subprocess.run(["streamlit", "run", "streamlit_app.py", "--server.port", port, "--server.address", "0.0.0.0"])

if __name__ == "__main__":
    # Start FastAPI in a separate thread
    fastapi_thread = threading.Thread(target=start_fastapi)
    fastapi_thread.daemon = True
    fastapi_thread.start()
    
    # Start Streamlit in the main thread
    start_streamlit()