@echo off
setlocal
title Habit Tracker Launcher

:: ====================================================================================
::  Habit Tracker - Professional Launcher
:: ====================================================================================

:: Ensure we are in the script directory
cd /d "%~dp0"

echo.
echo  ================================================================
echo   Habit Tracker - Automatic Launcher
echo  ================================================================
echo.

:: 1. Check for Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo         Please install Python 3.10+ from https://python.org/
    pause
    exit /b 1
)

:: 2. Check Python Version (Quick check)
python -c "import sys; exit(0) if sys.version_info >= (3, 10) else exit(1)"
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python 3.10 or higher is required.
    pause
    exit /b 1
)
echo [OK] Python 3.10+ found.

:: 3. Check for .env (Optional warning)
if not exist ".env" (
    echo [INFO] No .env file found. Using default development settings.
) else (
    echo [OK] .env file detected.
)

:: 4. Check Global Dependencies
echo [INFO] Checking for installed dependencies...
python -c "import flask" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Dependencies found globally. Using global Python.
    goto :LaunchApp
)

:: 5. Virtual Environment Setup (Fallback)
echo [INFO] Dependencies not found globally. Using virtual environment...
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
)

:: 6. Activate & Install Dependencies
echo [INFO] Activating virtual environment...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [ERROR] Cannot find venv activation script.
    pause
    exit /b 1
)

echo [INFO] Installing/Checking dependencies in venv...
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.

:LaunchApp
:: 7. Launch Application
echo.
echo [INFO] Starting Habit Tracker...
echo        Press Ctrl+C to stop the server.
echo.
python run.py

if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Application crashed with exit code %ERRORLEVEL%
    pause
)

:: Deactivate on exit (rarely reached if window closes)
if defined VIRTUAL_ENV deactivate
endlocal
