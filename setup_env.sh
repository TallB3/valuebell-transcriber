#!/bin/bash
# Clean environment setup for Valuebell Transcriber

set -e  # Exit on error

echo "🔔 Setting up Valuebell Transcriber development environment..."

# Check if FFmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not found. Please install it first:"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    echo "   Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

echo "✅ FFmpeg found: $(ffmpeg -version | head -n1)"

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python found: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "📦 Virtual environment already exists"
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

echo "🧪 Installing testing dependencies..."
pip install -r requirements-test.txt

# Verify installation
echo "✅ Verifying installation..."
python3 -c "import gradio, elevenlabs, numpy; print('Core dependencies installed successfully')"

# Run tests
echo "🧪 Running validation tests..."
python3 validate_functions.py

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "To activate the environment:"
echo "   source venv/bin/activate"
echo ""
echo "To run the app:"
echo "   python app.py"
echo ""
echo "To deactivate:"
echo "   deactivate"