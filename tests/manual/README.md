# Manual Testing Guide

This directory contains scripts and instructions for manual testing that requires real APIs or user interaction.

## Testing with Real APIs

### ElevenLabs API Testing
Create a test script `test_real_elevenlabs.py` when you have access to a real API key:

```python
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app import process_transcript_complete

# Test with real API (requires valid API key)
def test_real_transcription():
    result = process_transcript_complete(
        episode_name="manual_test",
        source_type="Audio File",
        delivery_method="File Upload",
        file_input="path/to/test_audio.wav",
        url_input="",
        language="en",
        api_key="your_real_api_key_here"
    )

    print("Status:", result[0])
    print("TXT Preview:", result[1][:200] + "..." if len(result[1]) > 200 else result[1])

if __name__ == "__main__":
    test_real_transcription()
```

### Google Drive/Dropbox Testing
Test with real URLs to ensure download functionality works:

```python
# Test real file downloads (be careful with rate limits)
test_urls = [
    "https://drive.google.com/file/d/your_test_file_id/view",
    "https://dropbox.com/s/your_test_file/audio.mp3"
]

for url in test_urls:
    try:
        source_type = detect_file_source(url)
        print(f"URL: {url} -> Source: {source_type}")
    except Exception as e:
        print(f"Error testing {url}: {e}")
```

## UI Testing

### Gradio Interface Testing
When the environment has all dependencies installed:

1. Run `python app.py`
2. Test various input combinations:
   - File uploads with different formats
   - URL inputs from different sources
   - JSON transcript uploads
   - Error conditions (invalid files, missing API keys)
   - Download functionality

### Performance Testing
Test with large files to ensure:
- Memory usage remains reasonable
- Processing completes successfully
- Large file handling (>1GB WAV conversion)

## Integration Testing Checklist

- [ ] Upload audio file and get transcript
- [ ] Upload video file and get transcript
- [ ] Upload JSON transcript and reprocess
- [ ] Download individual files
- [ ] Download multiple files (ZIP)
- [ ] Test with different languages
- [ ] Test error handling (invalid files, network issues)
- [ ] Test file size limits and conversions

## Notes

- Always use test files, not production data
- Be mindful of API rate limits and costs
- Clean up temporary files after testing
- Document any issues or edge cases discovered