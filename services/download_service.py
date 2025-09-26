"""
File download service for various cloud providers
"""
import os
import requests
import gdown
import re
from bs4 import BeautifulSoup

from utils.file_utils import convert_dropbox_to_direct, handle_dropbox_transfer_with_prompt


def download_from_dropbox(url, output_path):
    """Download file from Dropbox using requests"""
    direct_url = convert_dropbox_to_direct(url)
    print(f"Converting Dropbox URL to direct download...")

    response = requests.get(direct_url, stream=True)
    response.raise_for_status()

    total_size = int(response.headers.get('content-length', 0))
    downloaded_size = 0

    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                downloaded_size += len(chunk)
                if total_size > 0:
                    percent = (downloaded_size / total_size) * 100
                    print(f"\rDownload progress: {percent:.1f}%", end='', flush=True)

    print(f"\nDownload completed: {output_path}")


def download_from_wetransfer(url, output_path):
    """Download file from WeTransfer"""
    print(f"Accessing WeTransfer download...")
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })

    try:
        response = session.get(url, allow_redirects=True)
        response.raise_for_status()

        if 'wetransfer.com' not in response.url and 'we.tl' not in response.url:
            raise ValueError("URL does not appear to be a valid WeTransfer link")

        download_url = None
        content_type = response.headers.get('content-type', '').lower()

        if any(media_type in content_type for media_type in ['video/', 'audio/', 'application/octet-stream']):
            download_url = response.url
        else:
            page_content = response.text
            download_patterns = [
                r'"(https://[^"]*\.wetransfer\.com/[^"]*download[^"]*)"',
                r'"(https://[^"]*wetransfer[^"]*\.(mp4|avi|mov|mkv|mp3|wav|m4a)[^"]*)"',
                r'href="([^"]*download[^"]*)"'
            ]

            for pattern in download_patterns:
                matches = re.findall(pattern, page_content, re.IGNORECASE)
                if matches:
                    download_url = matches[0] if isinstance(matches[0], str) else matches[0][0]
                    break

        if not download_url:
            download_url = response.url

        download_response = session.get(download_url, stream=True)
        download_response.raise_for_status()

        content_type = download_response.headers.get('content-type', '').lower()
        if 'text/html' in content_type:
            raise ValueError("WeTransfer link may have expired or requires manual access.")

        total_size = int(download_response.headers.get('content-length', 0))
        downloaded_size = 0

        with open(output_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    if total_size > 0:
                        percent = (downloaded_size / total_size) * 100
                        print(f"\rDownload progress: {percent:.1f}%", end='', flush=True)

        print(f"\nDownload completed: {output_path}")

    except Exception as e:
        raise Exception(f"WeTransfer download failed: {e}")


def download_file_from_source(url, output_path, source_type):
    """Download file based on source type"""
    if source_type == 'drive':
        print(f"📁 Downloading from Google Drive...")
        gdown.download(url, output_path, quiet=False, fuzzy=True)
        return output_path
    elif source_type == 'dropbox':
        print(f"📁 Downloading from Dropbox...")
        download_from_dropbox(url, output_path)
        return output_path
    elif source_type == 'dropbox_transfer':
        handle_dropbox_transfer_with_prompt(url, os.path.dirname(output_path))
    elif source_type == 'wetransfer':
        print(f"📁 Downloading from WeTransfer...")
        download_from_wetransfer(url, output_path)
        return output_path
    else:
        raise ValueError(f"Unsupported source type: {source_type}")