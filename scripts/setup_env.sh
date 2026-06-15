#!/bin/bash
# AntiGravity Setup Environment Script
# --------------------------------------------------

set -e

echo "=== AntiGravity Environment Setup ==="

# Check Python version
python3 --version || { echo "Python 3 is required but not installed. Exiting."; exit 1; }

# Create python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Exiting."
    exit 1;
fi

# Install the package in editable mode
echo "Installing AntiGravity in development mode..."
pip install -e .

echo "=== Setup completed successfully ==="
echo "To activate the environment: source venv/bin/activate"
