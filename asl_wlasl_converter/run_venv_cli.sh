#!/bin/bash
# Run the ASL WLASL Converter CLI in a virtual environment

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run ./venv_setup.sh first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Forward all arguments to the CLI script
python simple_cli.py "$@"

# Deactivation will happen automatically when the script exits