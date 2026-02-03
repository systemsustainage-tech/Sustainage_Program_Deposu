# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
# PYTHONDONTWRITEBYTECODE: Prevents Python from writing pyc files to disc
# PYTHONUNBUFFERED: Prevents Python from buffering stdout and stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web_app.py

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories for logs and data if they don't exist
RUN mkdir -p /app/backend/data /var/log/sustainage

# Expose port 8000
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "-c", "gunicorn_config.py", "web_app:app"]
