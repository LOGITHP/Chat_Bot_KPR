FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend source code, configuration, and app files into image
COPY . .

# Ensure storage directories exist inside the container
RUN mkdir -p storage/data storage/minio_data storage/qdrant_storage

EXPOSE 8000

CMD ["python", "app/main.py"]
