@echo off
REM Clean environment setup for Valuebell Transcriber (Windows)

echo 🔔 Setting up Valuebell Transcriber development environment...

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo ❌ FFmpeg not found. Please install it first:
    echo    Download from https://ffmpeg.org/download.html
    echo    Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH
    pause
    exit /b 1
)

echo ✅ FFmpeg found

REM Check Python version
python --version
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.11 or later
    pause
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo 📦 Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call venv\Scripts\activate

REM Upgrade pip
echo ⬆️  Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo 📋 Installing dependencies...
pip install -r requirements.txt

echo 🧪 Installing testing dependencies...
pip install -r requirements-test.txt

REM Verify installation
echo ✅ Verifying installation...
python -c "import gradio, elevenlabs, numpy; print('Core dependencies installed successfully')"

REM Run tests
echo 🧪 Running validation tests...
python validate_functions.py

echo.
echo 🎉 Environment setup complete!
echo.
echo To activate the environment:
echo    venv\Scripts\activate
echo.
echo To run the app:
echo    python app.py
echo.
echo To deactivate:
echo    deactivate

pause