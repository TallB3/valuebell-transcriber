"""
Integration tests for the main processing function
Tests the complete workflow with mocked external dependencies
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
class TestMainProcessingWorkflow:
    """Test the main process_transcript_complete function"""

    def test_process_json_file_upload(self, temp_dir, sample_elevenlabs_response, mock_subprocess):
        """Test processing uploaded JSON transcript file"""
        # Create a test JSON file
        json_file = os.path.join(temp_dir, "test_transcript.json")
        with open(json_file, 'w') as f:
            json.dump(sample_elevenlabs_response, f)

        # Mock gradio progress
        mock_progress = Mock()

        result = app.process_transcript_complete(
            episode_name="test_episode",
            source_type="JSON Transcript",
            delivery_method="File Upload",
            file_input=json_file,
            url_input="",
            language="en",
            api_key="test_key",
            progress=mock_progress
        )

        # Unpack results
        status, txt_content, srt_content, json_content, txt_path, srt_path, audio_path, json_path = result

        # Verify success
        assert "✅ Processing completed successfully!" in status
        assert "Hello world this is a test transcript" in txt_content
        assert "speaker_1:" in txt_content
        assert "speaker_2:" in txt_content
        assert len(srt_content) > 0
        assert len(json_content) > 0
        assert txt_path is not None
        assert srt_path is not None
        assert json_path is not None

    @patch('app.download_file_from_source')
    def test_process_json_url_download(self, mock_download, temp_dir, sample_elevenlabs_response, mock_subprocess):
        """Test processing JSON transcript from URL"""
        # Setup mock download
        json_file = os.path.join(temp_dir, "downloaded_transcript.json")
        with open(json_file, 'w') as f:
            json.dump(sample_elevenlabs_response, f)

        mock_download.return_value = json_file

        mock_progress = Mock()

        result = app.process_transcript_complete(
            episode_name="test_episode",
            source_type="JSON Transcript",
            delivery_method="URL",
            file_input=None,
            url_input="https://example.com/transcript.json",
            language="en",
            api_key="test_key",
            progress=mock_progress
        )

        status = result[0]
        assert "✅ Processing completed successfully!" in status
        mock_download.assert_called_once()

    @patch('subprocess.run')
    def test_process_audio_file_upload(self, mock_subprocess, temp_dir, sample_audio_file, mock_elevenlabs_client):
        """Test processing uploaded audio file"""
        # Mock ffmpeg conversion and duration extraction
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "5.5"

        mock_progress = Mock()

        result = app.process_transcript_complete(
            episode_name="test_episode",
            source_type="Audio File",
            delivery_method="File Upload",
            file_input=sample_audio_file,
            url_input="",
            language="en",
            api_key="test_api_key",
            progress=mock_progress
        )

        status, txt_content, srt_content, json_content, txt_path, srt_path, audio_path, json_path = result

        # Verify success
        assert "✅ Processing completed successfully!" in status
        assert "Hello world this is a test transcript" in txt_content
        assert len(srt_content) > 0
        assert audio_path is not None
        assert os.path.exists(txt_path)

        # Verify ElevenLabs API was called
        mock_elevenlabs_client.speech_to_text.convert.assert_called_once()

    def test_process_validation_errors(self):
        """Test input validation errors"""
        mock_progress = Mock()

        # Test missing episode name
        result = app.process_transcript_complete(
            episode_name="",
            source_type="Audio File",
            delivery_method="File Upload",
            file_input=None,
            url_input="",
            language="en",
            api_key="test_key",
            progress=mock_progress
        )
        assert "Episode name is required" in result[0]

        # Test missing file for upload
        result = app.process_transcript_complete(
            episode_name="test",
            source_type="Audio File",
            delivery_method="File Upload",
            file_input=None,
            url_input="",
            language="en",
            api_key="test_key",
            progress=mock_progress
        )
        assert "Please upload a file" in result[0]

        # Test missing URL for URL delivery
        result = app.process_transcript_complete(
            episode_name="test",
            source_type="Audio File",
            delivery_method="URL",
            file_input=None,
            url_input="",
            language="en",
            api_key="test_key",
            progress=mock_progress
        )
        assert "Please provide a URL" in result[0]

        # Test missing API key for transcription
        result = app.process_transcript_complete(
            episode_name="test",
            source_type="Audio File",
            delivery_method="File Upload",
            file_input="/fake/path.mp3",
            url_input="",
            language="en",
            api_key="",
            progress=mock_progress
        )
        assert "ElevenLabs API key is required" in result[0]

    def test_process_invalid_json_file(self, temp_dir):
        """Test processing invalid JSON file"""
        # Create invalid JSON file
        invalid_json_file = os.path.join(temp_dir, "invalid.json")
        with open(invalid_json_file, 'w') as f:
            f.write('{"invalid": "format"}')

        mock_progress = Mock()

        result = app.process_transcript_complete(
            episode_name="test_episode",
            source_type="JSON Transcript",
            delivery_method="File Upload",
            file_input=invalid_json_file,
            url_input="",
            language="en",
            api_key="test_key",
            progress=mock_progress
        )

        status = result[0]
        assert "doesn't appear to be in ElevenLabs format" in status

    @patch('elevenlabs.client.ElevenLabs')
    @patch('subprocess.run')
    def test_process_transcription_error(self, mock_subprocess, mock_elevenlabs, temp_dir, sample_audio_file):
        """Test handling of transcription errors"""
        # Mock successful ffmpeg
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "5.5"

        # Mock failed transcription
        mock_client = Mock()
        mock_elevenlabs.return_value = mock_client
        mock_client.speech_to_text.convert.side_effect = Exception("API Error")

        mock_progress = Mock()

        result = app.process_transcript_complete(
            episode_name="test_episode",
            source_type="Audio File",
            delivery_method="File Upload",
            file_input=sample_audio_file,
            url_input="",
            language="en",
            api_key="test_api_key",
            progress=mock_progress
        )

        status = result[0]
        assert "Transcription error" in status
        assert "API Error" in status

    @patch('subprocess.run')
    def test_large_wav_file_mp3_conversion(self, mock_subprocess, temp_dir, mock_elevenlabs_client):
        """Test conversion of large WAV files to MP3"""
        # Create a large dummy audio file
        large_audio_file = os.path.join(temp_dir, "large_audio.wav")
        with open(large_audio_file, 'wb') as f:
            # Write more than 1GB of dummy data (simulate large file)
            f.write(b'0' * 1000)  # Just a small file for testing

        # Mock ffmpeg calls
        def mock_subprocess_side_effect(cmd, **kwargs):
            mock_result = Mock()
            mock_result.returncode = 0
            if 'ffprobe' in cmd[0]:
                mock_result.stdout = "120.5"
            return mock_result

        mock_subprocess.side_effect = mock_subprocess_side_effect

        # Mock os.path.getsize to simulate large file
        with patch('os.path.getsize') as mock_getsize:
            mock_getsize.return_value = 2 * 1024 * 1024 * 1024  # 2GB

            mock_progress = Mock()

            result = app.process_transcript_complete(
                episode_name="test_episode",
                source_type="Audio File",
                delivery_method="File Upload",
                file_input=large_audio_file,
                url_input="",
                language="en",
                api_key="test_api_key",
                progress=mock_progress
            )

            status = result[0]
            assert "✅ Processing completed successfully!" in status

            # Should have called ffmpeg twice (WAV conversion + MP3 conversion)
            assert mock_subprocess.call_count >= 2


@pytest.mark.integration
class TestDownloadSelection:
    """Test file download selection functionality"""

    def test_handle_download_selection_single_file(self, temp_dir):
        """Test downloading a single file"""
        # Create test files
        txt_file = os.path.join(temp_dir, "test_transcript.txt")
        with open(txt_file, 'w') as f:
            f.write("Test transcript content")

        result = app.handle_download_selection(
            txt_selected=True,
            srt_selected=False,
            audio_selected=False,
            json_selected=False,
            txt_path=txt_file,
            srt_path=None,
            audio_path=None,
            json_path=None,
            episode_name="test_episode"
        )

        download_path, status = result
        assert download_path == txt_file
        assert "Downloading: test_transcript.txt" in status

    def test_handle_download_selection_multiple_files(self, temp_dir):
        """Test downloading multiple files (creates ZIP)"""
        # Create test files
        txt_file = os.path.join(temp_dir, "test_transcript.txt")
        srt_file = os.path.join(temp_dir, "test_subtitles.srt")

        with open(txt_file, 'w') as f:
            f.write("Test transcript")
        with open(srt_file, 'w') as f:
            f.write("Test subtitles")

        result = app.handle_download_selection(
            txt_selected=True,
            srt_selected=True,
            audio_selected=False,
            json_selected=False,
            txt_path=txt_file,
            srt_path=srt_file,
            audio_path=None,
            json_path=None,
            episode_name="test_episode"
        )

        download_path, status = result
        assert download_path.endswith('.zip')
        assert "Created ZIP with 2 files" in status
        assert os.path.exists(download_path)

    def test_handle_download_selection_no_files(self):
        """Test error when no files selected"""
        result = app.handle_download_selection(
            txt_selected=False,
            srt_selected=False,
            audio_selected=False,
            json_selected=False,
            txt_path=None,
            srt_path=None,
            audio_path=None,
            json_path=None,
            episode_name="test_episode"
        )

        download_path, status = result
        assert download_path is None
        assert "No files selected" in status

    def test_handle_download_selection_no_episode_name(self):
        """Test error when no episode name provided"""
        result = app.handle_download_selection(
            txt_selected=True,
            srt_selected=False,
            audio_selected=False,
            json_selected=False,
            txt_path="/fake/path.txt",
            srt_path=None,
            audio_path=None,
            json_path=None,
            episode_name=""
        )

        download_path, status = result
        assert download_path is None
        assert "No files processed yet" in status