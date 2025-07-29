# Adobe India Hackathon 2025 - Challenge 1A: PDF Outline Extractor

## 🚀 Quick Start

### Build Docker Image

```bash
docker build --platform linux/amd64 -t pdf-extractor:latest .
```

### Run PDF Extraction

**Linux/macOS:**

```bash
docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output --network none pdf-extractor:latest
```

**Windows PowerShell:**

```powershell
docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none pdf-extractor:latest
```

## 📋 Overview

Extracts structured outlines from PDFs, detecting hierarchical headings (H1-H4) and returning a clean JSON output. Works offline and optimized for speed.

## ✨ Features

* 📄 **Document Classification**: Forms, Manuals, Reports, STEM Docs, Invitations
* 🨍 **Heading Detection**: Extracts H1-H4 with classification
* 🔥 **Fast Processing**: ≤ 10 seconds for 50-page PDFs
* 🔐 **Offline & Secure**: No internet dependency
* 🐳 **Dockerized**: Lightweight, AMD64-compatible container

## 🏗️ Project Structure

```
adobe1a_final/
├── Dockerfile
├── main.py
├── process_pdfs.py
├── utils.py
├── requirements.txt
├── input/        # PDFs to process
├── output/       # JSON output
└── README.md
```

## 🧠 Logic and Architecture

### Document Type Handling

| Type         | Outline Output       |
| ------------ | -------------------- |
| Forms        | Empty array `[]`     |
| Manuals      | H1, H2               |
| Reports/RFPs | H1-H4 hierarchy      |
| STEM Docs    | H1-H3                |
| Invitations  | Event-based headings |

### Pipeline Flow

```
PDF Input → Classification → Text Extraction
        ↓
Pattern Matching → Heading Extraction → Deduplication
        ↓
Hierarchy Tagging → JSON Output
```

### Heading Classification Patterns

```
H1: "Chapter 1", "1. Introduction to..."
H2: "1.1 Subsection", "2.2 Learning Objectives"
H3: "Phase I: Planning"
H4: "For each X it could mean:"
```

## 🔧 Core Components

* `main.py` - Manages I/O and pipeline execution
* `process_pdfs.py` - Document classification and heading parsing
* `utils.py` - Text cleaning, heading detection, level tagging

## 📊 Input/Output

### Input

* PDFs placed in `/app/input`
* Max 50 pages per file

### Output

```json
{
  "title": "Document Title",
  "outline": [
    { "level": "H1", "text": "Chapter 1", "page": 1 },
    { "level": "H2", "text": "Section 1.1", "page": 2 }
  ]
}
```

## 🎯 Performance & Requirements

* **Execution Time**: ≤ 10s / 50-page PDF
* **Memory**: ≤ 200MB
* **Architecture**: AMD64 (x86\_64)
* **Network**: Offline
* **Dependencies**: pdfplumber, PyPDF2

## 🚀 Deployment Notes

### Docker Environment

* Base: `python:3.9-slim`
* Volumes: `/input` and `/output`
* No network access

### Hardware

* 8 CPU cores, 16 GB RAM (as per hackathon specs)

## 👨‍💼 Author

**Prakhar Dvedi** - Adobe India Hackathon 2025
GitHub: [prakharDvedi/adobe1a\_final](https://github.com/prakharDvedi/adobe1a_final)

## 📄 License

Developed for Adobe India Hackathon 2025 - Challenge 1A.
