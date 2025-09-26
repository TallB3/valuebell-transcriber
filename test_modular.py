#!/usr/bin/env python3
"""
Test runner for the modular version of Valuebell Transcriber
Tests individual modules and integration
"""
import os
import sys
import tempfile
import json

def test_modular_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing modular imports...")
    errors = []

    try:
        from config.settings import APP_NAME, SUPPORTED_LANGUAGES
        print(f"✅ Config imported successfully - {APP_NAME}")
    except Exception as e:
        errors.append(f"Config import: {e}")

    try:
        from utils.file_utils import detect_file_source, clean_filename
        from utils.format_utils import format_txt_timestamp, format_srt_time
        print("✅ Utils imported successfully")
    except Exception as e:
        errors.append(f"Utils import: {e}")

    try:
        from services.download_service import download_file_from_source
        from services.audio_service import get_audio_duration, process_audio_file
        from services.transcription_service import TranscriptionService
        from services.file_service import handle_download_selection
        print("✅ Services imported successfully")
    except Exception as e:
        errors.append(f"Services import: {e}")

    try:
        from processors.transcript_processor import analyze_transcript_quality, count_unique_speakers
        from processors.output_generator import generate_txt_transcript, generate_srt_subtitles
        print("✅ Processors imported successfully")
    except Exception as e:
        errors.append(f"Processors import: {e}")

    return errors

def test_utility_functions():
    """Test utility functions work correctly"""
    print("🧪 Testing utility functions...")
    errors = []

    try:
        from utils.file_utils import detect_file_source, clean_filename
        from utils.format_utils import format_txt_timestamp, format_srt_time

        # Test file source detection
        assert detect_file_source("https://drive.google.com/file/123") == "drive"
        assert detect_file_source("https://dropbox.com/s/abc") == "dropbox"
        assert detect_file_source("https://we.tl/xyz") == "wetransfer"

        # Test filename cleaning
        assert clean_filename("test episode!@#") == "test_episode___"
        assert clean_filename("normal_filename-123") == "normal_filename-123"

        # Test timestamp formatting
        assert format_txt_timestamp(65) == "00:01:05"
        assert format_srt_time(65.5) == "00:01:05,500"

        print("✅ Utility functions working correctly")

    except Exception as e:
        errors.append(f"Utility functions: {e}")

    return errors

def test_transcript_processor():
    """Test transcript processing functions"""
    print("🧪 Testing transcript processor...")
    errors = []

    try:
        from processors.transcript_processor import analyze_transcript_quality, count_unique_speakers

        # Test with sample data
        sample_words = [
            {"text": "Hello", "start": 0.0, "end": 0.5, "speaker_id": "speaker_1"},
            {"text": "world", "start": 0.6, "end": 1.0, "speaker_id": "speaker_2"}
        ]

        # Test quality analysis
        warnings = analyze_transcript_quality(sample_words)
        assert isinstance(warnings, list)

        # Test speaker counting
        speaker_count = count_unique_speakers(sample_words)
        assert speaker_count == 2

        print("✅ Transcript processor working correctly")

    except Exception as e:
        errors.append(f"Transcript processor: {e}")

    return errors

def test_output_generator():
    """Test output generation functions"""
    print("🧪 Testing output generator...")
    errors = []

    try:
        from processors.output_generator import generate_txt_transcript, generate_srt_subtitles

        # Test with sample data
        sample_words = [
            {"text": "Hello", "start": 0.0, "end": 0.5, "speaker_id": "speaker_1"},
            {"text": "world", "start": 0.6, "end": 1.0, "speaker_id": "speaker_1"}
        ]

        # Test TXT generation
        txt_output = generate_txt_transcript(sample_words)
        assert "Hello world" in txt_output
        assert "speaker_1:" in txt_output
        assert "TRANSCRIPT DISCLAIMER" in txt_output

        # Test SRT generation
        srt_output = generate_srt_subtitles(sample_words)
        assert "Hello world" in srt_output
        assert "00:00:00,000" in srt_output
        assert "speaker_1:" in srt_output

        print("✅ Output generator working correctly")

    except Exception as e:
        errors.append(f"Output generator: {e}")

    return errors

def test_config_settings():
    """Test configuration settings are accessible"""
    print("🧪 Testing configuration settings...")
    errors = []

    try:
        from config.settings import (
            APP_NAME, SUPPORTED_LANGUAGES, MAX_WAV_SIZE_BYTES,
            TRANSCRIPT_DISCLAIMER, HF_SERVER_NAME, HF_SERVER_PORT
        )

        assert APP_NAME == "Valuebell Transcriber"
        assert isinstance(SUPPORTED_LANGUAGES, list)
        assert len(SUPPORTED_LANGUAGES) > 0
        assert MAX_WAV_SIZE_BYTES > 0
        assert "TRANSCRIPT DISCLAIMER" in TRANSCRIPT_DISCLAIMER
        assert HF_SERVER_NAME == "0.0.0.0"
        assert HF_SERVER_PORT == 7860

        print("✅ Configuration settings accessible")

    except Exception as e:
        errors.append(f"Configuration settings: {e}")

    return errors

def test_file_service():
    """Test file service functions"""
    print("🧪 Testing file service...")
    errors = []

    try:
        from services.file_service import handle_download_selection
        import tempfile

        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Test content")
            temp_file = f.name

        # Test single file download
        result = handle_download_selection(
            txt_selected=True, srt_selected=False, audio_selected=False, json_selected=False,
            txt_path=temp_file, srt_path=None, audio_path=None, json_path=None,
            episode_name="test_episode"
        )

        download_path, status = result
        assert download_path == temp_file
        assert "Downloading:" in status

        # Clean up
        os.unlink(temp_file)

        print("✅ File service working correctly")

    except Exception as e:
        errors.append(f"File service: {e}")

    return errors

def run_modular_tests():
    """Run all modular tests"""
    print("=" * 60)
    print("🔔 VALUEBELL TRANSCRIBER - MODULAR VERSION TESTS")
    print("=" * 60)

    all_errors = []

    # Test imports
    errors = test_modular_imports()
    all_errors.extend(errors)

    # Test utility functions
    errors = test_utility_functions()
    all_errors.extend(errors)

    # Test transcript processor
    errors = test_transcript_processor()
    all_errors.extend(errors)

    # Test output generator
    errors = test_output_generator()
    all_errors.extend(errors)

    # Test configuration
    errors = test_config_settings()
    all_errors.extend(errors)

    # Test file service
    errors = test_file_service()
    all_errors.extend(errors)

    # Report results
    print("\n" + "=" * 60)
    if not all_errors:
        print("🎉 ALL MODULAR TESTS PASSED!")
        print("✅ The modular version is working correctly")
        print("✅ Ready to replace the original app.py")
        return True
    else:
        print(f"❌ {len(all_errors)} test(s) failed:")
        for error in all_errors:
            print(f"   - {error}")
        print("🔧 Fix issues before proceeding")
        return False

    print("=" * 60)

if __name__ == "__main__":
    success = run_modular_tests()
    sys.exit(0 if success else 1)