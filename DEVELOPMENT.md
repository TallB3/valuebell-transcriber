# Development Environment Setup

## Prerequisites

### Required System Dependencies

#### FFmpeg (Required)
FFmpeg is essential for audio/video processing:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

**Windows:**
1. Download from https://ffmpeg.org/download.html
2. Extract to a folder (e.g., `C:\ffmpeg`)
3. Add `C:\ffmpeg\bin` to your PATH environment variable
4. Restart your terminal/command prompt

**Verify Installation:**
```bash
ffmpeg -version
ffprobe -version
```

### Python Dependencies

Install the required Python packages:

```bash
# Install main dependencies
pip install -r requirements.txt

# Install testing dependencies (optional)
pip install -r requirements-test.txt
```

## Running the Application

### Local Development
```bash
python app.py
```

The app will be available at: http://localhost:7860

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