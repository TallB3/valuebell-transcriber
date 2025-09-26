"""
Unit tests for utility functions in app.py
These tests focus on individual functions in isolation
"""
import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the project root to Python path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import app


@pytest.mark.unit
class TestFileSourceDetection:
    """Unit tests for file source detection"""

    @pytest.mark.parametrize("url,expected", [
        ("https://drive.google.com/file/d/123/view", "drive"),
        ("https://docs.google.com/document/d/456/edit", "drive"),
        ("https://DRIVE.GOOGLE.com/file/d/789/view", "drive"),  # Case insensitive
    ])
    def test_detect_google_drive_sources(self, url, expected):
        assert app.detect_file_source(url) == expected

    @pytest.mark.parametrize("url,expected", [
        ("https://dropbox.com/s/abc123/file.mp3", "dropbox"),
        ("https://www.dropbox.com/sh/xyz/folder", "dropbox"),
        ("https://DROPBOX.com/s/test/file.wav", "dropbox"),  # Case insensitive
    ])
    def test_detect_dropbox_sources(self, url, expected):
        assert app.detect_file_source(url) == expected

    @pytest.mark.parametrize("url,expected", [
        ("https://dropbox.com/transfer/abc123", "dropbox_transfer"),
        ("https://dropbox.com/t/xyz789", "dropbox_transfer"),
        ("https://DROPBOX.com/TRANSFER/test", "dropbox_transfer"),  # Case insensitive
    ])
    def test_detect_dropbox_transfer_sources(self, url, expected):
        assert app.detect_file_source(url) == expected

    @pytest.mark.parametrize("url,expected", [
        ("https://we.tl/t-abc123", "wetransfer"),
        ("https://wetransfer.com/downloads/xyz789", "wetransfer"),
        ("https://WE.TL/t-test", "wetransfer"),  # Case insensitive
    ])
    def test_detect_wetransfer_sources(self, url, expected):
        assert app.detect_file_source(url) == expected

    @pytest.mark.parametrize("url,expected", [
        ("https://example.com/file.mp3", "unknown"),
        ("https://youtube.com/watch?v=123", "unknown"),
        ("ftp://server.com/file.wav", "unknown"),
        ("", "unknown"),
    ])
    def test_detect_unknown_sources(self, url, expected):
        assert app.detect_file_source(url) == expected


@pytest.mark.unit
class TestDropboxUrlConversion:
    """Unit tests for Dropbox URL conversion"""

    def test_convert_dl_0_to_dl_1(self):
        input_url = "https://dropbox.com/s/abc123/file.mp3?dl=0"
        expected = "https://dropbox.com/s/abc123/file.mp3?dl=1"
        assert app.convert_dropbox_to_direct(input_url) == expected

    def test_convert_dl_0_with_other_params(self):
        input_url = "https://dropbox.com/s/abc123/file.mp3?param=value&dl=0&other=test"
        expected = "https://dropbox.com/s/abc123/file.mp3?param=value&dl=1&other=test"
        assert app.convert_dropbox_to_direct(input_url) == expected

    def test_add_dl_1_no_existing_params(self):
        input_url = "https://dropbox.com/s/abc123/file.mp3"
        expected = "https://dropbox.com/s/abc123/file.mp3?dl=1"
        assert app.convert_dropbox_to_direct(input_url) == expected

    def test_add_dl_1_with_existing_params(self):
        input_url = "https://dropbox.com/s/abc123/file.mp3?param=value"
        expected = "https://dropbox.com/s/abc123/file.mp3?param=value&dl=1"
        assert app.convert_dropbox_to_direct(input_url) == expected

    def test_preserve_existing_dl_1(self):
        input_url = "https://dropbox.com/s/abc123/file.mp3?dl=1"
        assert app.convert_dropbox_to_direct(input_url) == input_url

    def test_non_dropbox_url_unchanged(self):
        urls = [
            "https://example.com/file.mp3",
            "https://drive.google.com/file/123",
            "https://wetransfer.com/downloads/xyz"
        ]
        for url in urls:
            assert app.convert_dropbox_to_direct(url) == url


@pytest.mark.unit
class TestWordAttributeGetter:
    """Unit tests for get_word_attr function"""

    def test_get_word_attr_dict_existing_key(self):
        word_dict = {"text": "hello", "start": 1.5, "end": 2.0, "speaker_id": "speaker_1"}
        assert app.get_word_attr(word_dict, "text") == "hello"
        assert app.get_word_attr(word_dict, "start") == 1.5
        assert app.get_word_attr(word_dict, "speaker_id") == "speaker_1"

    def test_get_word_attr_dict_missing_key(self):
        word_dict = {"text": "hello"}
        assert app.get_word_attr(word_dict, "missing_key") is None
        assert app.get_word_attr(word_dict, "missing_key", "default") == "default"

    def test_get_word_attr_object_existing_attr(self):
        word_obj = Mock()
        word_obj.text = "hello"
        word_obj.start = 1.5
        word_obj.speaker_id = "speaker_1"

        assert app.get_word_attr(word_obj, "text") == "hello"
        assert app.get_word_attr(word_obj, "start") == 1.5
        assert app.get_word_attr(word_obj, "speaker_id") == "speaker_1"

    def test_get_word_attr_object_missing_attr(self):
        word_obj = Mock()
        word_obj.text = "hello"

        # Mock doesn't have the attribute, should return default
        assert app.get_word_attr(word_obj, "missing_attr") is None
        assert app.get_word_attr(word_obj, "missing_attr", "default") == "default"

    def test_get_word_attr_invalid_input(self):
        # Test with None
        assert app.get_word_attr(None, "text") is None
        assert app.get_word_attr(None, "text", "default") == "default"

        # Test with string (no attributes)
        assert app.get_word_attr("invalid", "text") is None
        assert app.get_word_attr("invalid", "text", "default") == "default"


@pytest.mark.unit
class TestTimestampFormatting:
    """Unit tests for timestamp formatting functions"""

    @pytest.mark.parametrize("seconds,expected", [
        (0, "00:00:00"),
        (30, "00:00:30"),
        (60, "00:01:00"),
        (90, "00:01:30"),
        (3600, "01:00:00"),
        (3661, "01:01:01"),
        (7323, "02:02:03"),
        (None, "00:00:00"),
    ])
    def test_format_txt_timestamp(self, seconds, expected):
        assert app.format_txt_timestamp(seconds) == expected

    def test_format_txt_timestamp_float_input(self):
        # Should handle float input by converting to int
        assert app.format_txt_timestamp(65.7) == "00:01:05"
        assert app.format_txt_timestamp(3661.9) == "01:01:01"

    @pytest.mark.parametrize("seconds,expected", [
        (0, "00:00:00,000"),
        (30.5, "00:00:30,500"),
        (60.123, "00:01:00,123"),
        (90.999, "00:01:30,999"),
        (3600.001, "01:00:00,001"),
        (3661.567, "01:01:01,567"),
        (None, "00:00:00,000"),
    ])
    def test_format_srt_time(self, seconds, expected):
        assert app.format_srt_time(seconds) == expected

    def test_format_srt_time_rounding(self):
        # Test millisecond rounding
        assert app.format_srt_time(1.0004) == "00:00:01,000"  # Rounds down
        assert app.format_srt_time(1.0005) == "00:00:01,001"  # Rounds up


@pytest.mark.unit
class TestTranscriptQualityAnalysis:
    """Unit tests for transcript quality analysis"""

    def test_analyze_empty_words_data(self):
        warnings = app.analyze_transcript_quality([])
        assert warnings == []

    def test_analyze_none_words_data(self):
        warnings = app.analyze_transcript_quality(None)
        assert warnings == []

    def test_analyze_normal_transcript(self):
        words_data = [
            {"text": "Hello", "start": 0.0, "end": 0.5},
            {"text": "world", "start": 0.6, "end": 1.0},
            {"text": "test", "start": 1.1, "end": 1.4}
        ]
        warnings = app.analyze_transcript_quality(words_data)
        # Normal data should produce minimal warnings
        assert len(warnings) <= 1

    def test_analyze_transcript_with_long_final_token(self):
        words_data = [
            {"text": "Hello", "start": 0.0, "end": 0.5},
            {"text": "world", "start": 0.6, "end": 1.0},
            {"text": "very_long_final", "start": 1.1, "end": 15.0}  # 13.9 seconds long
        ]
        warnings = app.analyze_transcript_quality(words_data)

        # Should detect abnormal final token
        assert any("Final token has abnormal duration" in str(w) for w in warnings)
        assert any("very_long_final" in str(w) for w in warnings)

    def test_analyze_transcript_with_outliers(self):
        # Create data with clear outliers
        normal_words = [
            {"text": f"word{i}", "start": i * 0.5, "end": i * 0.5 + 0.4}
            for i in range(10)
        ]
        outlier_word = {"text": "outlier", "start": 5.0, "end": 20.0}  # Very long

        words_data = normal_words + [outlier_word]
        warnings = app.analyze_transcript_quality(words_data)

        # Should detect the outlier
        assert any("outlier" in str(w) for w in warnings)
        assert any("unusual duration" in str(w) for w in warnings)

    def test_analyze_transcript_incomplete(self):
        words_data = [
            {"text": "Short", "start": 0.0, "end": 0.5},
            {"text": "transcript", "start": 1.0, "end": 2.0}
        ]
        audio_duration = 60.0  # 60 seconds of audio

        warnings = app.analyze_transcript_quality(words_data, audio_duration)

        # Should detect incomplete transcript
        assert any("incomplete" in str(w).lower() for w in warnings)

    def test_analyze_transcript_missing_timestamps(self):
        words_data = [
            {"text": "Hello", "start": 0.0, "end": 0.5},
            {"text": "missing", "start": None, "end": None},  # Missing timestamps
            {"text": "world", "start": 1.0, "end": 1.5}
        ]
        warnings = app.analyze_transcript_quality(words_data)

        # Should handle missing timestamps gracefully
        assert isinstance(warnings, list)


@pytest.mark.unit
class TestAudioDurationExtraction:
    """Unit tests for audio duration extraction"""

    @patch('subprocess.run')
    def test_get_audio_duration_success(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "123.45"

        duration = app.get_audio_duration("/fake/path.mp3")
        assert duration == 123.45

        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        assert args[0] == 'ffprobe'
        assert '/fake/path.mp3' in args

    @patch('subprocess.run')
    def test_get_audio_duration_failure(self, mock_run):
        mock_run.return_value.returncode = 1  # Non-zero return code

        duration = app.get_audio_duration("/fake/path.mp3")
        assert duration is None

    @patch('subprocess.run')
    def test_get_audio_duration_exception(self, mock_run):
        mock_run.side_effect = FileNotFoundError("ffprobe not found")

        duration = app.get_audio_duration("/fake/path.mp3")
        assert duration is None

    @patch('subprocess.run')
    def test_get_audio_duration_invalid_output(self, mock_run):
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "not_a_number"

        duration = app.get_audio_duration("/fake/path.mp3")
        assert duration is None