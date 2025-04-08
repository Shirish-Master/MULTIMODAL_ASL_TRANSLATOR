#!/bin/bash
# Run the ASL WLASL Converter web application in a virtual environment

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./venv_setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run web application
echo "Starting ASL WLASL Converter Web Application..."
echo "Open http://localhost:8080 in your browser"

# Run the simplified app
cd webapp
python simple_app.py

# Deactivation will happen automatically when the script exits