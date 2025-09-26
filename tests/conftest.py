"""
Pytest configuration and shared fixtures
"""
import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch, mock_open


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_elevenlabs_response():
    """Mock ElevenLabs API response data"""
    return {
        "text": "Hello world this is a test transcript",
        "words": [
            {
                "text": "Hello",
                "start": 0.0,
                "end": 0.5,
                "speaker_id": "speaker_1"
            },
            {
                "text": "world",
                "start": 0.6,
                "end": 1.0,
                "speaker_id": "speaker_1"
            },
            {
                "text": "this",
                "start": 1.1,
                "end": 1.3,
                "speaker_id": "speaker_2"
            },
            {
                "text": "is",
                "start": 1.4,
                "end": 1.6,
                "speaker_id": "speaker_2"
            },
            {
                "text": "a",
                "start": 1.7,
                "end": 1.8,
                "speaker_id": "speaker_2"
            },
            {
                "text": "test",
                "start": 1.9,
                "end": 2.2,
                "speaker_id": "speaker_2"
            },
            {
                "text": "transcript",
                "start": 2.3,
                "end": 2.8,
                "speaker_id": "speaker_2"
            }
        ]
    }


@pytest.fixture
def mock_elevenlabs_client():
    """Mock ElevenLabs client"""
    with patch('elevenlabs.client.ElevenLabs') as mock_client:
        mock_instance = Mock()
        mock_client.return_value = mock_instance

        # Mock the transcription response
        mock_response = Mock()
        mock_response.text = "Hello world this is a test transcript"
        mock_response.words = [
            Mock(text="Hello", start=0.0, end=0.5, speaker_id="speaker_1"),
            Mock(text="world", start=0.6, end=1.0, speaker_id="speaker_1"),
            Mock(text="this", start=1.1, end=1.3, speaker_id="speaker_2"),
            Mock(text="is", start=1.4, end=1.6, speaker_id="speaker_2"),
            Mock(text="a", start=1.7, end=1.8, speaker_id="speaker_2"),
            Mock(text="test", start=1.9, end=2.2, speaker_id="speaker_2"),
            Mock(text="transcript", start=2.3, end=2.8, speaker_id="speaker_2")
        ]
        mock_response.model_dump.return_value = {
            "text": "Hello world this is a test transcript",
            "words": [
                {"text": "Hello", "start": 0.0, "end": 0.5, "speaker_id": "speaker_1"},
                {"text": "world", "start": 0.6, "end": 1.0, "speaker_id": "speaker_1"},
                {"text": "this", "start": 1.1, "end": 1.3, "speaker_id": "speaker_2"},
                {"text": "is", "start": 1.4, "end": 1.6, "speaker_id": "speaker_2"},
                {"text": "a", "start": 1.7, "end": 1.8, "speaker_id": "speaker_2"},
                {"text": "test", "start": 1.9, "end": 2.2, "speaker_id": "speaker_2"},
                {"text": "transcript", "start": 2.3, "end": 2.8, "speaker_id": "speaker_2"}
            ]
        }

        mock_instance.speech_to_text.convert.return_value = mock_response
        yield mock_instance


@pytest.fixture
def mock_subprocess():
    """Mock subprocess calls for ffmpeg"""
    with patch('subprocess.run') as mock_run:
        # Mock ffprobe duration call
        mock_run.return_value.returncode = 0
        mock_run.return_value.stdout = "5.5"  # 5.5 seconds duration
        yield mock_run


@pytest.fixture
def mock_requests():
    """Mock requests for file downloads"""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.headers = {'content-length': '1000'}
        mock_response.iter_content.return_value = [b'test audio data chunk 1', b'test audio data chunk 2']
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_gdown():
    """Mock gdown for Google Drive downloads"""
    with patch('gdown.download') as mock_download:
        mock_download.return_value = "/tmp/test_file.mp3"
        yield mock_download


@pytest.fixture
def sample_audio_file(temp_dir):
    """Create a sample audio file for testing"""
    audio_file = os.path.join(temp_dir, "test_audio.wav")
    # Create a dummy file with some content
    with open(audio_file, 'wb') as f:
        f.write(b'RIFF' + b'0' * 100)  # Minimal WAV-like structure
    return audio_file


@pytest.fixture
def sample_json_transcript(temp_dir, sample_elevenlabs_response):
    """Create a sample JSON transcript file"""
    json_file = os.path.join(temp_dir, "test_transcript.json")
    with open(json_file, 'w') as f:
        json.dump(sample_elevenlabs_response, f)
    return json_file