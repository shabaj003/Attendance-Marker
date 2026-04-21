#!/bin/bash
# Attendance Management System - Setup Script for Linux/Mac

echo ""
echo "========================================"
echo "Attendance Management System Setup"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ from https://www.python.org/"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv || { echo "ERROR: Failed to create virtual environment"; exit 1; }

echo "[2/5] Activating virtual environment..."
source venv/bin/activate || { echo "ERROR: Failed to activate virtual environment"; exit 1; }

echo "[3/5] Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt || { 
    echo "ERROR: Failed to install dependencies"
    echo "Note: face_recognition requires dlib. Install with:"
    echo "  sudo apt-get install build-essential cmake dlib-dev  (Linux)"
    echo "  brew install cmake  (Mac)"
    exit 1
}

echo "[4/5] Running database migrations..."
python manage.py migrate || { echo "ERROR: Database migration failed"; exit 1; }

echo "[5/5] Creating superuser account..."
echo "Please enter superuser credentials:"
python manage.py createsuperuser

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To run the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Then visit: http://localhost:8000"
echo "Admin panel: http://localhost:8000/admin/"
echo ""
