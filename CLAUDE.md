# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Valuebell Transcriber is a Hugging Face Spaces application built with Gradio that provides professional transcription services for audio and video files. It's designed for podcasts, interviews, and meetings with automatic speaker detection.

## Architecture

The application uses a **modular architecture** with clear separation of concerns:

```
valuebell-transcriber/
├── config/settings.py          # Configuration constants
├── utils/                      # Utilities
│   ├── file_utils.py          # File handling, source detection
│   └── format_utils.py        # Timestamp formatting
├── services/                   # Core services
│   ├── download_service.py    # Cloud file downloads
│   ├── audio_service.py       # Audio processing & conversion
│   ├── transcription_service.py # ElevenLabs API integration
│   └── file_service.py        # Download packaging
├── processors/                 # Data processing
│   ├── transcript_processor.py # Quality analysis & speaker grouping
│   └── output_generator.py   # TXT/SRT/JSON generation
├── ui/interface.py            # Gradio interface
└── app.py                     # Main orchestration (284 lines)
```

**Key Features:**
- Accepts audio/video files via upload or URL (Google Drive, Dropbox, WeTransfer)
- Uses ElevenLabs API for transcription with speaker detection
- Provides multiple output formats: TXT, SRT subtitles, and JSON
- Quality analysis with outlier detection and completeness checking
- Automatic audio format optimization (WAV/MP3 based on size)

## Development Commands

**Clean Environment Setup:**
```bash
# Automated setup (Linux/macOS)
./setup_env.sh

# Or manual setup with virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

**Run the application:**
```bash
# Activate environment first
source venv/bin/activate  # or your preferred method
python app.py
```

**Testing:**
```bash
# Quick validation (no external dependencies)
python validate_functions.py

# Test modular structure
python test_modular_simple.py

# Full test suite (requires pytest)
pip install -r requirements-test.txt
pytest tests/
```

**Development:**
See `DEVELOPMENT.md` for detailed setup instructions and troubleshooting.

## Key Implementation Details

**Modular Components:**
- Main orchestration: `process_transcript_complete()` in app.py
- File downloads: `services/download_service.py`
- Audio processing: `services/audio_service.py` (requires FFmpeg)
- Transcription: `services/transcription_service.py` (ElevenLabs API)
- Quality analysis: `processors/transcript_processor.py`
- Output generation: `processors/output_generator.py`
- UI interface: `ui/interface.py`

**Configuration:**
- Settings: `config/settings.py`
- File types: Audio (.mp3, .wav, .m4a), Video (.mp4, .avi, .mov), JSON (.json)
- APIs: ElevenLabs API key required for transcription

**Deployment:**
This is configured as a Hugging Face Space (see README.md metadata). The app runs on Gradio with Python 3.11 and requires FFmpeg to be available in the environment.