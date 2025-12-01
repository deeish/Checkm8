#!/bin/bash
# Quick run script for CheckM8 Chess Game

echo "Setting up CheckM8 Chess Game..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if tkinter is available
echo "Checking for tkinter..."
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "WARNING: tkinter not found!"
    echo "Try one of these solutions:"
    echo "1. Install python-tk: brew install python-tk"
    echo "2. Use system Python: /usr/bin/python3 -m venv venv"
    echo "3. The GUI won't work, but you can test the backend with: pytest tests/"
    exit 1
fi

# Run the game
echo "Starting CheckM8 Chess Game..."
python main.py "$@"

