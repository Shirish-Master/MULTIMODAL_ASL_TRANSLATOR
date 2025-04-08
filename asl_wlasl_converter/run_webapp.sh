#!/bin/bash
# Run the ASL WLASL Converter Web Application

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Create directories if they don't exist
mkdir -p data/videos
mkdir -p models

# Check if requirements are installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing requirements..."
    pip install -r requirements.txt
fi

# Run the web application
echo "Starting ASL WLASL Converter Web Application (Simple Version)..."
echo "Open http://localhost:8080 in your browser"

cd webapp
echo "Using Python: $(which python3)"
echo "Python version: $(python3 --version)"
echo "Starting simple app..."
python3 simple_app.py