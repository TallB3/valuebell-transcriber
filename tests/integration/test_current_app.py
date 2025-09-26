"""
Baseline integration tests for the current monolithic app.py
These tests validate the current behavior before modularization.
"""
import pytest
import os
import json
import tempfile
from unittest.mock import patch, Mock, mock_open
import sys

# Add the project root to Python path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
import app


@pytest.mark.integration
class TestFileSourceDetection:
    """Test file source detection functionality"""

    def test_detect_google_drive_urls(self):
        """Test detection of Google Drive URLs"""
        urls = [
            "https://drive.google.com/file/d/123/view",
            "https://docs.google.com/document/d/456/edit"
        ]
        for url in urls:
            assert app.detect_file_source(url) == 'drive'

    def test_detect_dropbox_urls(self):
        """Test detection of Dropbox URLs"""
        urls = [
            "https://dropbox.com/s/abc123/file.mp3",
            "https://www.dropbox.com/sh/xyz/folder"
        ]
        for url in urls:
            assert app.detect_file_source(url) == 'dropbox'

    def test_detect_dropbox_transfer_urls(self):
        """Test detection of Dropbox Transfer URLs"""
        urls = [
            "https://dropbox.com/transfer/abc123",
            "https://dropbox.com/t/xyz789"
        ]
        for url in urls:
            assert app.detect_file_source(url) == 'dropbox_transfer'

    def test_detect_wetransfer_urls(self):
        """Test detection of WeTransfer URLs"""
        urls = [
            "https://we.tl/t-abc123",
            "https://wetransfer.com/downloads/xyz789"
        ]
        for url in urls:
            assert app.detect_file_source(url) == 'wetransfer'

    def test_detect_unknown_urls(self):
        """Test detection of unknown URLs"""
        urls = [
            "https://example.com/file.mp3",
            "https://youtube.com/watch?v=123"
        ]
        for url in urls:
            assert app.detect_file_source(url) == 'unknown'


@pytest.mark.integration
class TestDropboxUrlConversion:
    """Test Dropbox URL conversion functionality"""

    def test_convert_dl_0_to_dl_1(self):
        """Test converting dl=0 to dl=1"""
        input_url = "https://dropbox.com/s/abc123/file.mp3?dl=0"
        expected = "https://dropbox.com/s/abc123/file.mp3?dl=1"
        assert app.convert_dropbox_to_direct(input_url) == expected

    def test_add_dl_1_when_missing(self):
        """Test adding dl=1 when not present"""
        input_url = "https://dropbox.com/s/abc123/file.mp3"
        expected = "https://dropbox.com/s/abc123/file.mp3?dl=1"
        assert app.convert_dropbox_to_direct(input_url) == expected

    def test_preserve_existing_dl_1(self):
        """Test preserving existing dl=1"""
        input_url = "https://dropbox.com/s/abc123/file.mp3?dl=1"
        assert app.convert_dropbox_to_direct(input_url) == input_url

    def test_non_dropbox_url_unchanged(self):
        """Test non-Dropbox URLs remain unchanged"""
        input_url = "https://example.com/file.mp3"
        assert app.convert_dropbox_to_direct(input_url) == input_url


@pytest.mark.integration
class TestUtilityFunctions:
    """Test utility functions used throughout the app"""

    def test_get_word_attr_with_dict(self):
        """Test get_word_attr with dictionary input"""
        word_dict = {"text": "hello", "start": 1.0, "end": 2.0}
        assert app.get_word_attr(word_dict, "text") == "hello"
        assert app.get_word_attr(word_dict, "start") == 1.0
        assert app.get_word_attr(word_dict, "nonexistent", "default") == "default"

    def test_get_word_attr_with_object(self):
        """Test get_word_attr with object input"""
        word_obj = Mock()
        word_obj.text = "hello"
        word_obj.start = 1.0

        assert app.get_word_attr(word_obj, "text") == "hello"
        assert app.get_word_attr(word_obj, "start") == 1.0
        assert app.get_word_attr(word_obj, "nonexistent", "default") == "default"

    def test_format_txt_timestamp(self):
        """Test TXT timestamp formatting"""
        assert app.format_txt_timestamp(0) == "00:00:00"
        assert app.format_txt_timestamp(65) == "00:01:05"
        assert app.format_txt_timestamp(3661) == "01:01:01"
        assert app.format_txt_timestamp(None) == "00:00:00"

    def test_format_srt_time(self):
        """Test SRT timestamp formatting"""
        assert app.format_srt_time(0) == "00:00:00,000"
        assert app.format_srt_time(65.5) == "00:01:05,500"
        assert app.format_srt_time(3661.123) == "01:01:01,123"
        assert app.format_srt_time(None) == "00:00:00,000"


@pytest.mark.integration
class TestTranscriptQualityAnalysis:
    """Test transcript quality analysis functionality"""

    def test_analyze_transcript_quality_empty_data(self):
        """Test quality analysis with empty data"""
        warnings = app.analyze_transcript_quality([])
        assert warnings == []

    def test_analyze_transcript_quality_normal_data(self, sample_elevenlabs_response):
        """Test quality analysis with normal data"""
        words_data = sample_elevenlabs_response["words"]
        warnings = app.analyze_transcript_quality(words_data, 5.0)

        # Should have minimal warnings for normal data
        assert len(warnings) <= 5  # Allow for some statistical warnings

    def test_analyze_transcript_quality_with_outliers(self):
        """Test quality analysis with duration outliers"""
        words_data = [
            {"text": "normal", "start": 0.0, "end": 0.5},
            {"text": "outlier", "start": 1.0, "end": 20.0},  # Abnormally long
            {"text": "normal2", "start": 21.0, "end": 21.5}
        ]
        warnings = app.analyze_transcript_quality(words_data)

        # Should detect the outlier
        assert any("outlier" in str(warning) for warning in warnings)

    def test_analyze_transcript_quality_premature_ending(self):
        """Test detection of premature transcript ending"""
        words_data = [
            {"text": "short", "start": 0.0, "end": 0.5},
            {"text": "transcript", "start": 1.0, "end": 1.5}
        ]
        warnings = app.analyze_transcript_quality(words_data, 10.0)  # 10 second audio

        # Should detect incomplete transcript
        assert any("incomplete" in str(warning).lower() for warning in warnings)


@pytest.mark.integration
class TestAudioDurationExtraction:
    """Test audio duration extraction using ffprobe"""

    @patch('subprocess.run')
    def test_get_audio_duration_success(self, mock_run):
        """Test successful audio duration extraction"""
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "120.5"

        duration = app.get_audio_duration("/fake/path.mp3")
        assert duration == 120.5
        mock_run.assert_called_once()

    @patch('subprocess.run')
    def test_get_audio_duration_failure(self, mock_run):
        """Test failed audio duration extraction"""
        mock_run.return_value.returncode = 1

        duration = app.get_audio_duration("/fake/path.mp3")
        assert duration is None

    @patch('subprocess.run')
    def test_get_audio_duration_exception(self, mock_run):
        """Test exception handling in duration extraction"""
        mock_run.side_effect = Exception("ffprobe not found")

        duration = app.get_audio_duration("/fake/path.mp3")
        assert duration is None


@pytest.mark.integration
class TestDropboxTransferHandling:
    """Test Dropbox Transfer error handling"""

    def test_handle_dropbox_transfer_with_prompt(self, temp_dir):
        """Test Dropbox Transfer error message generation"""
        url = "https://dropbox.com/transfer/abc123"

        with pytest.raises(Exception) as excinfo:
            app.handle_dropbox_transfer_with_prompt(url, temp_dir)

        error_msg = str(excinfo.value)
        assert "DROPBOX TRANSFER DETECTED" in error_msg
        assert url in error_msg
        assert "Manual Link Required" in error_msg


@pytest.mark.integration
class TestFileDownloadOrchestration:
    """Test the main file download orchestration"""

    @patch('app.gdown.download')
    def test_download_file_from_source_drive(self, mock_gdown, temp_dir):
        """Test downloading from Google Drive"""
        output_path = os.path.join(temp_dir, "test.mp3")
        mock_gdown.return_value = output_path

        result = app.download_file_from_source("https://drive.google.com/file/123", output_path, 'drive')
        assert result == output_path
        mock_gdown.assert_called_once()

    @patch('app.download_from_dropbox')
    def test_download_file_from_source_dropbox(self, mock_dropbox, temp_dir):
        """Test downloading from Dropbox"""
        output_path = os.path.join(temp_dir, "test.mp3")

        result = app.download_file_from_source("https://dropbox.com/s/123", output_path, 'dropbox')
        assert result == output_path
        mock_dropbox.assert_called_once_with("https://dropbox.com/s/123", output_path)

    def test_download_file_from_source_dropbox_transfer(self, temp_dir):
        """Test Dropbox Transfer handling"""
        output_path = os.path.join(temp_dir, "test.mp3")

        with pytest.raises(Exception) as excinfo:
            app.download_file_from_source("https://dropbox.com/transfer/123", output_path, 'dropbox_transfer')

        assert "DROPBOX TRANSFER DETECTED" in str(excinfo.value)

    def test_download_file_from_source_unsupported(self, temp_dir):
        """Test unsupported source type"""
        output_path = os.path.join(temp_dir, "test.mp3")

        with pytest.raises(ValueError) as excinfo:
            app.download_file_from_source("https://example.com/file.mp3", output_path, 'unknown')

        assert "Unsupported source type" in str(excinfo.value)