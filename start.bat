@echo off
REM WiFi SOC v7 - Quick Start Script (Windows)
REM This script installs dependencies and starts the SOC platform

echo.
echo ================================================
echo   WiFi SOC v7 - Enterprise SOC Platform
echo   Quick Start Script (Windows)
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found!
python --version
echo.

REM Install dependencies
echo [2/4] Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [3/4] Dependencies installed successfully!
echo.

REM Start backend
echo [4/4] Starting FastAPI Backend Server...
echo.
echo ================================================
echo   Backend running on: http://127.0.0.1:8000
echo   Open frontend at: frontend/index.html
echo ================================================
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

pause
