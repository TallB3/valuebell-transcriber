# Development Environment Setup

## Prerequisites

### System Dependencies

#### FFmpeg (Required)
FFmpeg is essential for audio/video processing. Install system-wide:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to your PATH environment variable
4. Restart terminal

**Verify Installation:**
```bash
ffmpeg -version
ffprobe -version
```

### Python Environment Setup

#### Option 1: Using venv (Recommended)
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# For testing (optional)
pip install -r requirements-test.txt

# Deactivate when done
deactivate
```

#### Option 2: Using conda
```bash
# Create conda environment
conda create -n valuebell python=3.11
conda activate valuebell

# Install dependencies
pip install -r requirements.txt

# Deactivate when done
conda deactivate
```

#### Option 3: Using Poetry (Advanced)
```bash
# Initialize poetry (if pyproject.toml doesn't exist)
poetry init

# Install dependencies
poetry install

# Run app in poetry environment
poetry run python app.py
```

## Running the Application

### Local Development

**With virtual environment:**
```bash
# Activate your environment first
source venv/bin/activate  # or your preferred method

# Run the app
python app.py
```

**With conda:**
```bash
conda activate valuebell
python app.py
```

**With poetry:**
```bash
poetry run python app.py
```

The app will be available at: http://localhost:7860

**Environment Variables (Optional):**
```bash
# Create .env file for API keys (never commit this!)
echo "ELEVENLABS_API_KEY=your_key_here" > .env
```

### Testing the Setup

#### Quick Test (No External Dependencies)
```bash
python validate_functions.py
```

#### Full Modular Test
```bash
python test_modular_simple.py
```

#### With External Dependencies
```bash
# Requires pytest and other test dependencies
pytest tests/
```

## Common Issues

### 1. FFmpeg Not Found
**Error:** `[Errno 2] No such file or directory: 'ffmpeg'`

**Solution:** Install FFmpeg using the instructions above.

### 2. Missing Python Dependencies
**Error:** `ModuleNotFoundError: No module named 'gradio'`

**Solution:**
```bash
pip install -r requirements.txt
```

### 3. ElevenLabs API Key Required
**Error:** `ElevenLabs API key is required for transcription`

**Solution:** Get an API key from https://elevenlabs.io/ and enter it in the interface.

### 4. File Upload Issues
**Error:** Various file-related errors

**Solution:** Ensure uploaded files are in supported formats:
- Audio: `.mp3`, `.wav`, `.m4a`
- Video: `.mp4`, `.avi`, `.mov`
- JSON: `.json` (ElevenLabs format)

## Development Workflow

1. **Make Changes:** Modify modules in their respective directories
2. **Test Changes:** Run `python test_modular_simple.py`
3. **Test App:** Run `python app.py` and test functionality
4. **Commit:** Use git to commit your changes

## Production Deployment

For Hugging Face Spaces or similar platforms, ensure:
1. FFmpeg is available in the environment
2. All dependencies are in `requirements.txt`
3. The app uses the correct server settings from `config/settings.py`