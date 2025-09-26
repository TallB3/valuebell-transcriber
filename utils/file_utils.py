"""
File handling utilities for Valuebell Transcriber
"""
import os
import re


def clean_filename(name):
    """Clean filename by removing invalid characters"""
    return "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in name.strip())


def detect_file_source(url):
    """Detect if the URL is from Google Drive, Dropbox, WeTransfer, or unknown"""
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
    """Convert Dropbox share link to direct download link"""
    if 'dropbox.com' in url.lower():
        if 'dl=0' in url:
            return url.replace('dl=0', 'dl=1')
        elif 'dl=1' not in url:
            separator = '&' if '?' in url else '?'
            return f"{url}{separator}dl=1"
    return url


def get_file_extension(filename):
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()


def is_supported_file(filename, supported_extensions):
    """Check if file has supported extension"""
    ext = get_file_extension(filename)
    return ext in supported_extensions


def generate_output_filenames(base_name):
    """Generate output filenames for different formats"""
    return {
        'txt': f"{base_name}_transcript.txt",
        'srt': f"{base_name}_subtitles.srt",
        'json': f"{base_name}_raw_transcript.json"
    }


def handle_dropbox_transfer_with_prompt(url, output_dir):
    """Handle Dropbox Transfer with manual intervention"""
    error_msg = f"""
    🔗 DROPBOX TRANSFER DETECTED - Manual Link Required 🔗

    Dropbox Transfer links need a small extra step:

    OPTION 1 - Get Direct Download Link (Recommended):
    1. Open this URL in a new tab: {url}
    2. Click 'Download' or 'Download all'
    3. Your browser will start downloading
    4. Go to your browser's download manager (usually Ctrl+J or Cmd+Shift+J)
    5. RIGHT-CLICK on the downloading item → "Copy Download Link"
    6. Come back here and paste that direct link in the "File URL" field
    7. Try processing again - it should work!

    OPTION 2 - File Upload Instead:
    1. Let the download finish from step 2 above
    2. Switch to "File Upload" method in the form
    3. Upload the downloaded file directly

    💡 Tip: The direct download link (Option 1) is usually faster and works great with the URL method!
    """
    raise Exception(error_msg)


def get_word_attr(word_item, attr_name, default=None):
    """Helper function to access word attributes flexibly"""
    if isinstance(word_item, dict):
        return word_item.get(attr_name, default)
    elif hasattr(word_item, attr_name):
        return getattr(word_item, attr_name, default)
    return default