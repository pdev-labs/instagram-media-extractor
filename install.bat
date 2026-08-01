@echo off
echo === Instagram Media Extractor Installer ===

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in your PATH.
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Python is installed.

:: Setup virtual environment
echo Setting up virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Failed to create virtual environment.
    pause
    exit /b 1
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Installation complete!
echo To run the script interactively, use:
echo   python ig_media_extractor.py
echo.
pause
