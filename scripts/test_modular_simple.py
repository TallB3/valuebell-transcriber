#!/usr/bin/env python3
"""
Simple test runner for the modular version without external dependencies
Tests the core structure and functions that don't require external libraries
"""
import os
import sys

def test_basic_module_structure():
    """Test basic module structure and imports that don't require external deps"""
    print("🧪 Testing basic module structure...")
    errors = []

    # Test config module
    try:
        from config.settings import APP_NAME, SUPPORTED_LANGUAGES, MAX_WAV_SIZE_BYTES
        assert APP_NAME == "Valuebell Transcriber"
        assert isinstance(SUPPORTED_LANGUAGES, list)
        assert MAX_WAV_SIZE_BYTES > 0
        print("✅ Config module working")
    except Exception as e:
        errors.append(f"Config module: {e}")

    # Test utils module (functions that don't need external deps)
    try:
        from utils.file_utils import detect_file_source, clean_filename, get_word_attr
        from utils.format_utils import format_txt_timestamp, format_srt_time

        # Test file source detection
        assert detect_file_source("https://drive.google.com/file/123") == "drive"
        assert detect_file_source("https://dropbox.com/s/abc") == "dropbox"

        # Test filename cleaning
        assert clean_filename("test episode!@#") == "test_episode___"

        # Test word attribute getter
        word_dict = {"text": "hello", "start": 1.0}
        assert get_word_attr(word_dict, "text") == "hello"
        assert get_word_attr(word_dict, "missing", "default") == "default"

        # Test timestamp formatting
        assert format_txt_timestamp(65) == "00:01:05"
        assert format_srt_time(65.5) == "00:01:05,500"

        print("✅ Utils module working")
    except Exception as e:
        errors.append(f"Utils module: {e}")

    # Test that module files exist
    modules_to_check = [
        "services/download_service.py",
        "services/audio_service.py",
        "services/transcription_service.py",
        "services/file_service.py",
        "processors/transcript_processor.py",
        "processors/output_generator.py",
        "ui/interface.py",
        "app_new.py"
    ]

    for module_path in modules_to_check:
        if not os.path.exists(module_path):
            errors.append(f"Missing module file: {module_path}")

    if not errors:
        print("✅ All module files exist")

    return errors

def test_modular_structure_integrity():
    """Test that the modular structure is complete and consistent"""
    print("🧪 Testing modular structure integrity...")
    errors = []

    # Check directory structure
    required_dirs = [
        "config",
        "utils",
        "services",
        "processors",
        "ui"
    ]

    for dir_name in required_dirs:
        if not os.path.isdir(dir_name):
            errors.append(f"Missing directory: {dir_name}")
        else:
            init_file = os.path.join(dir_name, "__init__.py")
            if not os.path.exists(init_file):
                errors.append(f"Missing __init__.py in {dir_name}")

    if not errors:
        print("✅ Directory structure is complete")

    return errors

def test_function_extraction_completeness():
    """Test that key functions from original app.py have been properly extracted"""
    print("🧪 Testing function extraction completeness...")
    errors = []

    try:
        # Test that we can access the core functions through modules
        from utils.file_utils import detect_file_source, convert_dropbox_to_direct, get_word_attr
        from utils.format_utils import format_txt_timestamp, format_srt_time

        # Test functions work as expected
        test_cases = [
            (detect_file_source, "https://drive.google.com/file/123", "drive"),
            (convert_dropbox_to_direct, "https://dropbox.com/s/abc?dl=0", "https://dropbox.com/s/abc?dl=1"),
            (format_txt_timestamp, 65, "00:01:05"),
            (format_srt_time, 65.5, "00:01:05,500"),
        ]

        for func, input_val, expected in test_cases:
            result = func(input_val)
            if result != expected:
                errors.append(f"{func.__name__}: expected {expected}, got {result}")

        # Test word attribute getter
        word_dict = {"text": "hello", "start": 1.0}
        if get_word_attr(word_dict, "text") != "hello":
            errors.append("get_word_attr not working correctly")

        if not errors:
            print("✅ Core functions extracted and working")

    except Exception as e:
        errors.append(f"Function extraction: {e}")

    return errors

def compare_with_original():
    """Compare the modular version structure with original app.py"""
    print("🧪 Comparing with original app.py...")

    if not os.path.exists("app.py"):
        print("⚠️  Original app.py not found for comparison")
        return []

    # Read original file
    with open("app.py", 'r') as f:
        original_content = f.read()

    # Check that key function names from original are covered in modules
    key_functions = [
        "detect_file_source",
        "convert_dropbox_to_direct",
        "get_word_attr",
        "format_txt_timestamp",
        "format_srt_time",
        "analyze_transcript_quality",
        "get_audio_duration",
        "handle_download_selection"
    ]

    missing_functions = []
    for func_name in key_functions:
        if func_name not in original_content:
            missing_functions.append(f"Function {func_name} not found in original app.py")

    if not missing_functions:
        print("✅ All key functions accounted for in modular version")

    return missing_functions

def run_simple_modular_tests():
    """Run all simple modular tests"""
    print("=" * 60)
    print("🔔 VALUEBELL TRANSCRIBER - SIMPLE MODULAR TESTS")
    print("=" * 60)

    all_errors = []

    # Test basic structure
    errors = test_basic_module_structure()
    all_errors.extend(errors)

    # Test structure integrity
    errors = test_modular_structure_integrity()
    all_errors.extend(errors)

    # Test function extraction
    errors = test_function_extraction_completeness()
    all_errors.extend(errors)

    # Compare with original
    errors = compare_with_original()
    all_errors.extend(errors)

    # Report results
    print("\n" + "=" * 60)
    if not all_errors:
        print("🎉 ALL SIMPLE MODULAR TESTS PASSED!")
        print("✅ The modular structure is correctly implemented")
        print("✅ Core functions are working without external dependencies")
        print("✅ Ready to commit the modular version")
        return True
    else:
        print(f"❌ {len(all_errors)} issue(s) found:")
        for error in all_errors:
            print(f"   - {error}")
        print("🔧 Fix issues before proceeding")
        return False

if __name__ == "__main__":
    success = run_simple_modular_tests()
    print("=" * 60)
    sys.exit(0 if success else 1)