#!/bin/bash
# WiFi SOC v7 - Quick Start Script (Linux/Mac)

echo ""
echo "================================================"
echo "  WiFi SOC v7 - Enterprise SOC Platform"
echo "  Quick Start Script (Linux/Mac)"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ first"
    exit 1
fi

echo "[1/4] Python found!"
python3 --version
echo ""

# Create virtual environment (optional but recommended)
if [ ! -d "venv" ]; then
    echo "[2/4] Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
else
    echo "[2/4] Activating existing virtual environment..."
    source venv/bin/activate
fi

echo "[3/4] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo ""
echo "[4/4] Starting FastAPI Backend Server..."
echo ""
echo "================================================"
echo "  Backend running on: http://127.0.0.1:8000"
echo "  Open frontend at: frontend/index.html"
echo "================================================"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
