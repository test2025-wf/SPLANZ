@echo off
echo Starting Splunk Dashboard Automator Desktop Application...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import tkinter, json, os, threading, asyncio" >nul 2>&1
if errorlevel 1 (
    echo Installing basic Python packages...
    pip install --upgrade pip
)

python -c "import flask, playwright, cryptography, PIL, pytz" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install flask playwright cryptography pillow pytz tkcalendar
    echo Installing browser for screenshots...
    playwright install chromium
)

REM Create necessary directories
if not exist logs mkdir logs
if not exist tmp mkdir tmp
if not exist screenshots mkdir screenshots

REM Run the application
echo.
echo Starting application...
python simple_desktop_app.py

REM If we get here, the app has closed
echo.
echo Application closed.
pause