FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Create input and output directories
RUN mkdir -p /app/input /app/output

# Set the entrypoint
CMD ["python", "main.py"]
