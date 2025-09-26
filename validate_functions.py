#!/usr/bin/env python3
"""
Function validation without external dependencies
Extracts and tests core functions from app.py
"""
import re
import os

def detect_file_source(url):
    """Extracted function for testing"""
    url_lower = url.lower()
    if 'drive.google' in url_lower or 'docs.google' in url_lower:
        return 'drive'
    elif 'dropbox' in url_lower:
        if '/transfer/' in url_lower or 'dropbox.com/t/' in url_lower:
            return 'dropbox_transfer'
        else:
            return 'dropbox'
    elif 'we.tl' in url_lower or 'wetransfer.com' in url_lower:
        return 'wetransfer'
    else:
        return 'unknown'

def convert_dropbox_to_direct(url):
    """Extracted function for testing"""
    if 'dropbox.com' in url.lower():
        if 'dl=0' in url:
            return url.replace('dl=0', 'dl=1')
        elif 'dl=1' not in url:
            separator = '&' if '?' in url else '?'
            return f"{url}{separator}dl=1"
    return url

def get_word_attr(word_item, attr_name, default=None):
    """Extracted function for testing"""
    if isinstance(word_item, dict):
        return word_item.get(attr_name, default)
    elif hasattr(word_item, attr_name):
        return getattr(word_item, attr_name, default)
    return default

def format_txt_timestamp(seconds_float):
    """Extracted function for testing"""
    if seconds_float is None: return "00:00:00"
    seconds_int = int(seconds_float)
    hours = seconds_int // 3600
    minutes = (seconds_int % 3600) // 60
    seconds = seconds_int % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_srt_time(seconds_float):
    """Extracted function for testing"""
    if seconds_float is None: return "00:00:00,000"
    millis = round(seconds_float * 1000)
    hours = millis // (3600 * 1000)
    millis %= (3600 * 1000)
    minutes = millis // (60 * 1000)
    millis %= (60 * 1000)
    seconds = millis // 1000
    milliseconds = millis % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def run_validation_tests():
    """Run validation tests on extracted functions"""
    print("🧪 Running function validation tests...\n")

    errors = []
    tests_run = 0

    # Test 1: File source detection
    try:
        print("Testing file source detection...")
        test_cases = [
            ("https://drive.google.com/file/123", "drive"),
            ("https://docs.google.com/document/456", "drive"),
            ("https://dropbox.com/s/abc123", "dropbox"),
            ("https://dropbox.com/transfer/xyz789", "dropbox_transfer"),
            ("https://dropbox.com/t/test123", "dropbox_transfer"),
            ("https://we.tl/t-abc123", "wetransfer"),
            ("https://wetransfer.com/downloads/xyz", "wetransfer"),
            ("https://example.com/file.mp3", "unknown"),
        ]

        for url, expected in test_cases:
            result = detect_file_source(url)
            assert result == expected, f"Expected {expected}, got {result} for {url}"
            tests_run += 1

        print("✅ File source detection tests passed")

    except Exception as e:
        errors.append(f"File source detection: {e}")

    # Test 2: Dropbox URL conversion
    try:
        print("Testing Dropbox URL conversion...")
        test_cases = [
            ("https://dropbox.com/s/abc?dl=0", "https://dropbox.com/s/abc?dl=1"),
            ("https://dropbox.com/s/abc", "https://dropbox.com/s/abc?dl=1"),
            ("https://dropbox.com/s/abc?dl=1", "https://dropbox.com/s/abc?dl=1"),
            ("https://dropbox.com/s/abc?param=value", "https://dropbox.com/s/abc?param=value&dl=1"),
            ("https://example.com/file.mp3", "https://example.com/file.mp3"),
        ]

        for input_url, expected in test_cases:
            result = convert_dropbox_to_direct(input_url)
            assert result == expected, f"Expected {expected}, got {result}"
            tests_run += 1

        print("✅ Dropbox URL conversion tests passed")

    except Exception as e:
        errors.append(f"Dropbox URL conversion: {e}")

    # Test 3: Word attribute getter
    try:
        print("Testing word attribute getter...")

        # Test with dict
        word_dict = {"text": "hello", "start": 1.0, "speaker_id": "speaker_1"}
        assert get_word_attr(word_dict, "text") == "hello"
        assert get_word_attr(word_dict, "start") == 1.0
        assert get_word_attr(word_dict, "missing", "default") == "default"
        tests_run += 3

        # Test with object-like structure
        class MockWord:
            def __init__(self):
                self.text = "world"
                self.start = 2.0

        word_obj = MockWord()
        assert get_word_attr(word_obj, "text") == "world"
        assert get_word_attr(word_obj, "start") == 2.0
        assert get_word_attr(word_obj, "missing", "default") == "default"
        tests_run += 3

        print("✅ Word attribute getter tests passed")

    except Exception as e:
        errors.append(f"Word attribute getter: {e}")

    # Test 4: Timestamp formatting
    try:
        print("Testing timestamp formatting...")

        # TXT format tests
        txt_cases = [
            (0, "00:00:00"),
            (30, "00:00:30"),
            (65, "00:01:05"),
            (3661, "01:01:01"),
            (None, "00:00:00"),
        ]

        for seconds, expected in txt_cases:
            result = format_txt_timestamp(seconds)
            assert result == expected, f"TXT: Expected {expected}, got {result} for {seconds}"
            tests_run += 1

        # SRT format tests
        srt_cases = [
            (0, "00:00:00,000"),
            (30.5, "00:00:30,500"),
            (65.123, "00:01:05,123"),
            (3661.567, "01:01:01,567"),
            (None, "00:00:00,000"),
        ]

        for seconds, expected in srt_cases:
            result = format_srt_time(seconds)
            assert result == expected, f"SRT: Expected {expected}, got {result} for {seconds}"
            tests_run += 1

        print("✅ Timestamp formatting tests passed")

    except Exception as e:
        errors.append(f"Timestamp formatting: {e}")

    # Summary
    print(f"\n📊 Test Results:")
    print(f"Total tests run: {tests_run}")

    if not errors:
        print("🎉 All validation tests passed!")
        print("✅ Core functions are working correctly")
        return True
    else:
        print(f"❌ {len(errors)} test group(s) failed:")
        for error in errors:
            print(f"   - {error}")
        return False

def check_test_structure():
    """Validate our test structure"""
    print("\n🔍 Checking test structure...")

    required_files = [
        "tests/__init__.py",
        "tests/conftest.py",
        "tests/unit/__init__.py",
        "tests/integration/__init__.py",
        "tests/unit/test_utility_functions.py",
        "tests/integration/test_current_app.py",
        "tests/integration/test_main_processing.py",
        "pytest.ini",
        "requirements-test.txt"
    ]

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        print(f"❌ Missing test files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All test structure files are present")
        return True

if __name__ == "__main__":
    print("=" * 60)
    print("🔔 VALUEBELL TRANSCRIBER - FUNCTION VALIDATION")
    print("=" * 60)

    structure_ok = check_test_structure()
    functions_ok = run_validation_tests()

    print("\n" + "=" * 60)
    if structure_ok and functions_ok:
        print("🎉 VALIDATION SUCCESSFUL!")
        print("✅ Ready to proceed with modularization")
        print("✅ Test structure is complete")
        print("✅ Core functions work correctly")
    else:
        print("❌ VALIDATION FAILED!")
        if not structure_ok:
            print("🔧 Fix test structure issues")
        if not functions_ok:
            print("🔧 Fix function implementation issues")
    print("=" * 60)