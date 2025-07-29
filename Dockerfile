FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

RUN pip install --no-cache-dir pdfplumber==0.10.3 PyPDF2==3.0.1

COPY main.py .
COPY process_pdfs.py .
COPY utils.py .

# Create input and output directories with proper permissions
RUN mkdir -p /app/input /app/output && \
    chmod 755 /app/input /app/output

# Create a non-root user for security
RUN useradd -m -u 1000 pdfuser && \
    chown -R pdfuser:pdfuser /app

USER pdfuser

# Set the entrypoint
CMD ["python", "main.py"]
