# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Valuebell Transcriber is a Hugging Face Spaces application built with Gradio that provides professional transcription services for audio and video files. It's designed for podcasts, interviews, and meetings with automatic speaker detection.

## Architecture

The application is a single-file Gradio web app (`app.py`) that:
- Accepts audio/video files via upload or URL (Google Drive, Dropbox, WeTransfer)
- Uses ElevenLabs API for transcription with speaker detection
- Provides multiple output formats: TXT, SRT subtitles, and JSON
- Includes download functionality for processed files

Key components:
- File source detection and download handlers for various cloud services
- Transcript processing with quality analysis and speaker identification
- Gradio interface with tabbed output display
- File packaging system for multi-format downloads

## Development Commands

**Run the application:**
```bash
python app.py
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Deployment:**
This is configured as a Hugging Face Space (see README.md metadata). The app runs on Gradio 5.39.0 with Python 3.11.

## Key Implementation Details

- Main processing function: `process_transcript_complete()` in app.py:310
- File download handlers: `download_file_from_source()` in app.py:158
- Quality analysis: `analyze_transcript_quality()` in app.py:206
- Interface creation: `create_interface()` in app.py:750

The application uses Git LFS for large file storage (configured in .gitattributes) and requires an ElevenLabs API key for transcription functionality.