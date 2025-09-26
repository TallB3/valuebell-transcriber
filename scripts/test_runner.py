#!/usr/bin/env python3
"""
Simple test runner for basic validation without pytest
This validates our test structure and core functions work
"""
import os
import sys
import tempfile

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main app
import app

def run_basic_tests():
    """Run basic tests to validate current functionality"""
    print("🧪 Running basic validation tests...\n")

    errors = []

    try:
        # Test 1: File source detection
        print("Testing file source detection...")
        assert app.detect_file_source("https://drive.google.com/file/123") == "drive"
        assert app.detect_file_source("https://dropbox.com/s/abc") == "dropbox"
        assert app.detect_file_source("https://we.tl/xyz") == "wetransfer"
        assert app.detect_file_source("https://example.com/file.mp3") == "unknown"
        print("✅ File source detection tests passed")

    except Exception as e:
        errors.append(f"File source detection: {e}")

    try:
        # Test 2: Dropbox URL conversion
        print("Testing Dropbox URL conversion...")
        assert app.convert_dropbox_to_direct("https://dropbox.com/s/abc?dl=0") == "https://dropbox.com/s/abc?dl=1"
        assert app.convert_dropbox_to_direct("https://dropbox.com/s/abc") == "https://dropbox.com/s/abc?dl=1"
        print("✅ Dropbox URL conversion tests passed")

    except Exception as e:
        errors.append(f"Dropbox URL conversion: {e}")

    try:
        # Test 3: Word attribute getter
        print("Testing word attribute getter...")
        word_dict = {"text": "hello", "start": 1.0}
        assert app.get_word_attr(word_dict, "text") == "hello"
        assert app.get_word_attr(word_dict, "start") == 1.0
        assert app.get_word_attr(word_dict, "missing", "default") == "default"
        print("✅ Word attribute getter tests passed")

    except Exception as e:
        errors.append(f"Word attribute getter: {e}")

    try:
        # Test 4: Timestamp formatting
        print("Testing timestamp formatting...")
        assert app.format_txt_timestamp(0) == "00:00:00"
        assert app.format_txt_timestamp(65) == "00:01:05"
        assert app.format_srt_time(65.5) == "00:01:05,500"
        print("✅ Timestamp formatting tests passed")

    except Exception as e:
        errors.append(f"Timestamp formatting: {e}")

    try:
        # Test 5: Quality analysis with empty data
        print("Testing transcript quality analysis...")
        warnings = app.analyze_transcript_quality([])
        assert warnings == []
        print("✅ Quality analysis tests passed")

    except Exception as e:
        errors.append(f"Quality analysis: {e}")

    try:
        # Test 6: Interface creation
        print("Testing interface creation...")
        interface = app.create_interface()
        assert interface is not None
        print("✅ Interface creation test passed")

    except Exception as e:
        errors.append(f"Interface creation: {e}")

    # Test 7: File handling functions exist
    try:
        print("Testing function availability...")
        assert callable(app.download_file_from_source)
        assert callable(app.process_transcript_complete)
        assert callable(app.handle_download_selection)
        print("✅ All required functions are available")

    except Exception as e:
        errors.append(f"Function availability: {e}")

    # Report results
    print(f"\n📊 Test Results:")
    if not errors:
        print("🎉 All basic validation tests passed!")
        print("✅ The current codebase is ready for modularization")
        return True
    else:
        print(f"❌ {len(errors)} test(s) failed:")
        for error in errors:
            print(f"   - {error}")
        return False

def test_sample_data():
    """Test processing sample data"""
    print("\n🧪 Testing with sample data...")

    sample_words = [
        {"text": "Hello", "start": 0.0, "end": 0.5, "speaker_id": "speaker_1"},
        {"text": "world", "start": 0.6, "end": 1.0, "speaker_id": "speaker_1"},
        {"text": "test", "start": 1.1, "end": 1.4, "speaker_id": "speaker_2"}
    ]

    try:
        # Test quality analysis
        warnings = app.analyze_transcript_quality(sample_words, 5.0)
        print(f"✅ Quality analysis completed with {len(warnings)} warnings")

        # Test with outlier data
        outlier_words = sample_words + [
            {"text": "outlier", "start": 2.0, "end": 20.0, "speaker_id": "speaker_2"}
        ]
        warnings = app.analyze_transcript_quality(outlier_words)
        print(f"✅ Outlier detection completed with {len(warnings)} warnings")

        return True

    except Exception as e:
        print(f"❌ Sample data testing failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔔 VALUEBELL TRANSCRIBER - BASELINE TEST VALIDATION")
    print("=" * 60)

    success1 = run_basic_tests()
    success2 = test_sample_data()

    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 BASELINE VALIDATION SUCCESSFUL!")
        print("✅ Ready to proceed with modularization")
    else:
        print("❌ BASELINE VALIDATION FAILED!")
        print("🔧 Fix issues before proceeding with modularization")
    print("=" * 60)