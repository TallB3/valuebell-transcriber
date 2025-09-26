"""
Audio processing service for conversion and duration extraction
"""
import subprocess
import os
from config.settings import (
    DEFAULT_SAMPLE_RATE,
    DEFAULT_CHANNELS,
    HIGH_QUALITY_BITRATE,
    STANDARD_MP3_SAMPLE_RATE,
    MAX_WAV_SIZE_BYTES
)


def get_audio_duration(file_path):
    """Get duration of audio/video file using ffprobe"""
    try:
        cmd = [
            'ffprobe', '-v', 'error', '-show_entries',
            'format=duration', '-of',
            'default=noprint_wrappers=1:nokey=1', file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return float(result.stdout.strip())
    except FileNotFoundError:
        raise Exception("FFmpeg is not installed or not found in PATH. Please install FFmpeg:\n"
                       "- Ubuntu/Debian: sudo apt install ffmpeg\n"
                       "- macOS: brew install ffmpeg\n"
                       "- Windows: Download from https://ffmpeg.org/download.html")
    except Exception as e:
        print(f"Could not determine audio duration: {e}")
    return None


def convert_to_wav(input_path, output_path):
    """Convert any input to a standardized high-quality WAV"""
    command = [
        "ffmpeg", "-i", input_path,
        "-acodec", "pcm_s16le",    # Optimal codec for uncompressed WAV
        "-ar", str(DEFAULT_SAMPLE_RATE),  # Optimal sample rate for speech-to-text
        "-ac", str(DEFAULT_CHANNELS),     # Mono channel
        "-y", output_path
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"✅ Converted to high-quality WAV: {output_path}")
    except FileNotFoundError:
        raise Exception("FFmpeg is not installed or not found in PATH. Please install FFmpeg:\n"
                       "- Ubuntu/Debian: sudo apt install ffmpeg\n"
                       "- macOS: brew install ffmpeg\n"
                       "- Windows: Download from https://ffmpeg.org/download.html")


def convert_to_mp3(input_path, output_path):
    """Convert WAV to high-quality MP3"""
    command = [
        "ffmpeg", "-i", input_path,
        "-acodec", "libmp3lame",
        "-b:a", HIGH_QUALITY_BITRATE,     # High-quality bitrate
        "-ar", str(STANDARD_MP3_SAMPLE_RATE),  # Standard MP3 sample rate
        "-ac", str(DEFAULT_CHANNELS),
        "-y", output_path
    ]
    try:
        subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"✅ MP3 conversion completed: {output_path}")
    except FileNotFoundError:
        raise Exception("FFmpeg is not installed or not found in PATH. Please install FFmpeg:\n"
                       "- Ubuntu/Debian: sudo apt install ffmpeg\n"
                       "- macOS: brew install ffmpeg\n"
                       "- Windows: Download from https://ffmpeg.org/download.html")


def process_audio_file(source_file_path, temp_dir, base_filename):
    """
    Process audio file with WAV-first conversion and size-based MP3 fallback

    Returns:
        str: Path to the final processed audio file
    """
    # Define target WAV path
    wav_path = os.path.join(temp_dir, f"{base_filename}.wav")

    # Convert to high-quality WAV
    print("Converting to high-quality WAV...")
    convert_to_wav(source_file_path, wav_path)

    # Check file size
    wav_file_size_bytes = os.path.getsize(wav_path)

    if wav_file_size_bytes > MAX_WAV_SIZE_BYTES:
        print(f"⚠️ WAV file is {wav_file_size_bytes / (1024*1024):.2f} MB (> 1GB). Creating MP3 fallback.")

        mp3_path = os.path.join(temp_dir, f"{base_filename}.mp3")

        # Convert the large WAV to high-quality MP3
        print("WAV file > 1GB. Converting to high-quality MP3...")
        convert_to_mp3(wav_path, mp3_path)

        # Clean up the oversized WAV file
        if os.path.exists(wav_path):
            os.remove(wav_path)

        return mp3_path
    else:
        # The WAV file is acceptable size
        return wav_path