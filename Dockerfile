FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose ports (different ports for each service)
EXPOSE 8000 8501

# Create the run.py file
COPY run.py .

# Run the application using our Python launcher
CMD ["python", "run.py"]