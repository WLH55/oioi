#!/bin/bash
# Linux/Mac startup script for huobao-drama backend

echo "==================================="
echo " Huobao Drama Backend - Python"
echo "==================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
if [ ! -d "venv/lib/python*/site-packages/fastapi" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    echo ""
fi

# Create necessary directories
mkdir -p data uploads logs

# Check if .env exists, if not copy example
if [ ! -f ".env" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env file with your configuration!"
    echo ""
fi

# Start the application
echo "Starting application..."
echo ""
python main.py
