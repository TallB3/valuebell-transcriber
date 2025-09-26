"""
Transcription service using ElevenLabs API
"""
import httpx
from elevenlabs.client import ElevenLabs


class TranscriptionService:
    """Service for handling ElevenLabs transcription"""

    def __init__(self, api_key):
        """Initialize the transcription service with API key"""
        self.api_key = api_key
        custom_timeout = httpx.Timeout(60.0, read=900.0, connect=10.0)
        self.client = ElevenLabs(api_key=api_key, timeout=custom_timeout)

    def transcribe_audio(self, audio_file_path, language_code="en", diarize=True):
        """
        Transcribe audio file using ElevenLabs API

        Args:
            audio_file_path: Path to the audio file
            language_code: Language code for transcription
            diarize: Whether to perform speaker diarization

        Returns:
            Transcription response object with text and words
        """
        with open(audio_file_path, "rb") as audio_file_object:
            response = self.client.speech_to_text.convert(
                file=audio_file_object,
                model_id="scribe_v1_experimental",
                language_code=language_code,
                diarize=diarize,
                tag_audio_events=False,
                timestamps_granularity="word"
            )

        return response

    def extract_transcription_data(self, response):
        """
        Extract text and words data from transcription response

        Args:
            response: ElevenLabs transcription response

        Returns:
            tuple: (full_transcript_text, words_data, response_dict)
        """
        full_transcript_text = ""
        words_data = []

        if hasattr(response, 'text'):
            full_transcript_text = response.text
        if hasattr(response, 'words'):
            words_data = response.words

        # Convert to dictionary for caching
        response_dict = response.model_dump()

        return full_transcript_text, words_data, response_dict