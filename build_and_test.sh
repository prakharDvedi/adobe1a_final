#!/bin/bash

echo "Building Docker image..."
docker build -t pdf-extractor:latest .

if [ $? -eq 0 ]; then
    echo "Docker image built successfully!"
    
    echo "Testing Docker container..."
    docker run --rm -v ${PWD}/input:/app/input -v ${PWD}/output:/app/output --network none pdf-extractor:latest
    
    if [ $? -eq 0 ]; then
        echo "Container ran successfully!"
        echo "Check the output directory for processed JSON files."
    else
        echo "Container failed to run properly."
        exit 1
    fi
else
    echo "Failed to build Docker image."
    exit 1
fi