@echo off
REM CivicAI - All-In-One Automated Setup & Launch Script for Windows

title CivicAI Smart Citizen Complaint Management System
echo =================================================================
echo    CivicAI: Smart Citizen Complaint Management System
echo                  All-In-One Automated Launcher
echo =================================================================

cd /d "%~dp0"

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in system PATH.
    pause
    exit /b 1
)

REM Create venv if not present
if not exist "venv" (
    echo [1/4] Creating virtual environment...
    python -m venv venv
)

REM Activate venv
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [3/4] Installing dependencies...
pip install --quiet -r requirements.txt

REM Ensure database exists
if not exist "civicai.db" (
    echo [4/4] Seeding SQLite database with 40 demo complaints...
    python database.py
)

echo =================================================================
echo [OK] Setup Complete! Launching CivicAI...
echo Server URL: http://127.0.0.1:5000
echo =================================================================

start http://127.0.0.1:5000
python app.py
pause

