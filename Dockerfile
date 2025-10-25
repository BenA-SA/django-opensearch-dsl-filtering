FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements/test.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Set Python path to include the package
ENV PYTHONPATH=/app:$PYTHONPATH
