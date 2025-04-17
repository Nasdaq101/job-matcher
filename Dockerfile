# File: Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Expose the port
EXPOSE 8080

# Command to run the application
CMD ["python", "app.py"]