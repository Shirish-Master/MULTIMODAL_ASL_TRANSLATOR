#!/bin/bash
# Setup and run ASL WLASL Converter in a virtual environment

# Stop on first error
set -e

# Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Ensure pip is up to date
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating data directories..."
mkdir -p data/videos
mkdir -p models

# Link from archive-3 if available
ARCHIVE3_PATH="../archive-3"
if [ -d "$ARCHIVE3_PATH" ]; then
    echo "Found archive-3 directory, linking resources..."
    
    # Link JSON file if it exists
    if [ -f "$ARCHIVE3_PATH/WLASL_v0.3.json" ] && [ ! -f "data/WLASL_v0.3.json" ]; then
        echo "Linking WLASL_v0.3.json..."
        ln -sf "$(pwd)/$ARCHIVE3_PATH/WLASL_v0.3.json" "$(pwd)/data/WLASL_v0.3.json"
    fi
    
    # Use videos from archive-3
    echo "Setting up to use videos from archive-3/videos..."
    echo "Note: We'll access videos directly from $ARCHIVE3_PATH/videos"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To run the web application:"
echo "  ./run_venv_webapp.sh"
echo ""
echo "To run the CLI tool (examples):"
echo "  ./run_venv_cli.sh word-lookup book"
echo "  ./run_venv_cli.sh random-word"
echo "  ./run_venv_cli.sh list-words"
echo "  ./run_venv_cli.sh sentence-lookup \"I want to learn sign language\""
echo ""
echo "To deactivate the virtual environment when done:"
echo "  deactivate"