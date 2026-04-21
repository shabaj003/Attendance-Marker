@echo off
REM Attendance Management System - Setup Script for Windows

echo.
echo ========================================
echo Attendance Management System Setup
echo ========================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Note: face_recognition may require additional setup
    echo For Windows, you may need to download dlib wheels from:
    echo https://github.com/ageitgey/face_recognition/issues/175
    pause
    exit /b 1
)

echo [4/5] Running database migrations...
python manage.py migrate
if errorlevel 1 (
    echo ERROR: Database migration failed
    pause
    exit /b 1
)

echo [5/5] Creating superuser account...
echo Please enter superuser credentials:
python manage.py createsuperuser

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the development server:
echo   venv\Scripts\activate.bat
echo   python manage.py runserver
echo.
echo Then visit: http://localhost:8000
echo Admin panel: http://localhost:8000/admin/
echo.
pause
