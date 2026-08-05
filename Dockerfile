FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files & buffer stdout/stderr
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .
<<<<<<< HEAD
EXPOSE 8000
=======

>>>>>>> 49672135256fd1aea9c9b17b20fad1fba6a642eb
# Ensure data and qdrant storage directories exist
RUN mkdir -p data qdrant_storage

CMD ["python", "main.py"]
