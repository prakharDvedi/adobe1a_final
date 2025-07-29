# PDF Extractor Docker Container

This application extracts titles and outlines from PDF files using a Docker container that runs with no network access for security.

## Quick Start

### Build the Docker Image
```bash
docker build -t pdf-extractor:latest .
```

### Run the Container
```bash
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none pdf-extractor:latest
```

## Command Breakdown

- `docker run` - Run a Docker container
- `--rm` - Automatically remove the container when it exits
- `-v ${PWD}/input:/app/input` - Mount the local `input` directory to `/app/input` in the container
- `-v ${PWD}/output:/app/output` - Mount the local `output` directory to `/app/output` in the container
- `--network none` - Run with no network access for security
- `pdf-extractor:latest` - The Docker image to run

## Directory Structure

```
your-project/
├── input/          # Place your PDF files here
│   ├── file1.pdf
│   ├── file2.pdf
│   └── ...
├── output/         # JSON results will be created here
│   ├── file1.json
│   ├── file2.json
│   └── ...
├── Dockerfile
├── main.py
├── process_pdfs.py
└── build_and_test.sh
```

## Usage Steps

1. **Place PDF files** in the `input/` directory
2. **Build the Docker image** (only needed once):
   ```bash
   docker build -t pdf-extractor:latest .
   ```
3. **Run the container**:
   ```bash
   docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none pdf-extractor:latest
   ```
4. **Check results** in the `output/` directory

## Output Format

Each PDF file generates a corresponding JSON file with the following structure:

```json
{
  "title": "Document Title",
  "outline": [
    {
      "level": "H1",
      "text": "Chapter 1: Introduction",
      "page": 0
    },
    {
      "level": "H2", 
      "text": "1.1 Overview",
      "page": 1
    }
  ]
}
```

## Features

- **Secure**: Runs with `--network none` for complete network isolation
- **Efficient**: Only installs necessary dependencies
- **Non-root**: Runs as a non-root user for security
- **Error Handling**: Graceful handling of corrupted or unreadable PDFs
- **Batch Processing**: Processes all PDF files in the input directory

## Build Script

For convenience, use the provided build script:

```bash
chmod +x build_and_test.sh
./build_and_test.sh
```

This script will:
1. Build the Docker image
2. Run the container with your input files
3. Display the results

## Troubleshooting

### No PDF files found
- Ensure PDF files are in the `input/` directory
- Check file extensions are `.pdf` (case-insensitive)

### Permission errors
- Ensure the `output/` directory exists and is writable
- On Linux/Mac, you may need to adjust directory permissions

### Container fails to start
- Verify Docker is running
- Check that the image was built successfully
- Ensure input and output directories exist

## Security Features

- No network access (`--network none`)
- Non-root user execution
- Minimal attack surface with only necessary dependencies
- Automatic container cleanup (`--rm`)

## Dependencies

The container includes:
- Python 3.9
- pdfplumber 0.10.3
- PyPDF2 3.0.1
- poppler-utils (system dependency)