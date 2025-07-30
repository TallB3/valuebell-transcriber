#!/usr/bin/env python3
"""
Valuebell Transcriber - Hugging Face Spaces Deployment
Professional transcription tool for podcasts, interviews, and meetings
"""

import gradio as gr
import os
import subprocess
import gdown
import requests
import json
import httpx
import gc
import zipfile
import re
import shutil
import tempfile
from elevenlabs.client import ElevenLabs
from collections import defaultdict
from bs4 import BeautifulSoup

# Helper functions for file downloading
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

def get_word_attr(word_item, attr_name, default=None):
    """Helper function to access word attributes flexibly"""
    if isinstance(word_item, dict):
        return word_item.get(attr_name, default)
    elif hasattr(word_item, attr_name):
        return getattr(word_item, attr_name, default)
    return default

def format_txt_timestamp(seconds_float):
    """Format timestamp for TXT files"""
    if seconds_float is None: return "00:00:00"
    seconds_int = int(seconds_float)
    hours = seconds_int // 3600
    minutes = (seconds_int % 3600) // 60
    seconds = seconds_int % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def format_srt_time(seconds_float):
    """Format timestamp for SRT files"""
    if seconds_float is None: return "00:00:00,000"
    millis = round(seconds_float * 1000)
    hours = millis // (3600 * 1000)
    millis %= (3600 * 1000)
    minutes = millis // (60 * 1000)
    millis %= (60 * 1000)
    seconds = millis // 1000
    milliseconds = millis % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def process_transcript_complete(episode_name, source_type, delivery_method, file_input, url_input, language, api_key, progress=gr.Progress()):
    """Complete processing function that does everything"""
    
    try:
        # Step 1: Validate inputs
        progress(0.05, desc="Validating inputs...")
        
        if not episode_name.strip():
            return "❌ Error: Episode name is required", "", "", None, None, None, None
        
        if delivery_method == "File Upload" and not file_input:
            return "❌ Error: Please upload a file", "", "", None, None, None, None
        
        if delivery_method == "URL" and not url_input.strip():
            return "❌ Error: Please provide a URL", "", "", None, None, None, None
        
        if source_type in ["Video File", "Audio File"] and not api_key.strip():
            return "❌ Error: ElevenLabs API key is required for transcription", "", "", None, None, None, None
        
        # Step 2: Setup
        progress(0.1, desc="Setting up processing...")
        
        # Clean episode name
        clean_episode_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in episode_name.strip())
        
        # Create temp directory for this session
        temp_dir = tempfile.mkdtemp()
        
        # File paths
        base_filename = clean_episode_name
        target_mp3_path = os.path.join(temp_dir, f"{base_filename}.mp3")
        downloaded_source_path = os.path.join(temp_dir, f"{base_filename}_source")
        raw_json_cache_path = os.path.join(temp_dir, f"{base_filename}_raw_transcript.json")
        
        # Variables
        words_data = []
        full_transcript_text = ""
        loaded_from_cache = False
        audio_file_ready = False
        source_file_path = None
        
        # Step 3: Handle file input
        progress(0.15, desc="Processing file input...")
        
        if source_type == "JSON Transcript":
            # Handle JSON file
            if delivery_method == "File Upload":
                if file_input is None:
                    return "❌ Error: No JSON file uploaded", "", "", None, None, None, None
                
                # Save uploaded file - file_input is now a file path string in Gradio
                json_path = os.path.join(temp_dir, f"{base_filename}_uploaded.json")
                shutil.copy2(file_input, json_path)
                
                # Load and validate JSON
                with open(json_path, 'r', encoding='utf-8') as f:
                    uploaded_json = json.load(f)
                
                if 'text' in uploaded_json or 'words' in uploaded_json:
                    full_transcript_text = uploaded_json.get("text", "")
                    words_data = uploaded_json.get("words", [])
                    
                    # Save to cache
                    with open(raw_json_cache_path, 'w', encoding='utf-8') as f:
                        json.dump(uploaded_json, f, ensure_ascii=False, indent=4)
                    
                    loaded_from_cache = True
                    progress(0.3, desc="JSON transcript loaded successfully!")
                else:
                    return "❌ Error: JSON doesn't appear to be in ElevenLabs format", "", "", None, None, None, None
            
            else:  # URL delivery for JSON
                json_url = url_input.strip()
                detected_source = detect_file_source(json_url)
                
                json_download_path = downloaded_source_path + ".json"
                download_file_from_source(json_url, json_download_path, detected_source)
                
                with open(json_download_path, 'r', encoding='utf-8') as f:
                    downloaded_json = json.load(f)
                
                if 'text' in downloaded_json or 'words' in downloaded_json:
                    full_transcript_text = downloaded_json.get("text", "")
                    words_data = downloaded_json.get("words", [])
                    
                    # Save to cache
                    with open(raw_json_cache_path, 'w', encoding='utf-8') as f:
                        json.dump(downloaded_json, f, ensure_ascii=False, indent=4)
                    
                    loaded_from_cache = True
                    progress(0.3, desc="JSON transcript downloaded and loaded!")
                else:
                    return "❌ Error: Downloaded JSON doesn't appear to be in ElevenLabs format", "", "", None, None, None, None
        
        else:
            # Handle video/audio files
            progress(0.2, desc="Processing media file...")
            
            if delivery_method == "File Upload":
                if file_input is None:
                    return "❌ Error: No media file uploaded", "", "", None, None, None, None
                
                # Save uploaded file - file_input is now a file path string in Gradio
                file_ext = os.path.splitext(file_input)[1]
                source_file_path = downloaded_source_path + file_ext
                
                shutil.copy2(file_input, source_file_path)
                
                print(f"✅ File saved: {source_file_path}")
            
            else:  # URL delivery
                file_url = url_input.strip()
                detected_source = detect_file_source(file_url)
                
                # Download with appropriate extension
                if source_type == "Video File":
                    source_file_path = downloaded_source_path + ".mp4"
                else:
                    source_file_path = downloaded_source_path + ".mp3"
                
                source_file_path = download_file_from_source(file_url, source_file_path, detected_source)
                print(f"✅ File downloaded: {source_file_path}")
            
            # Convert video to audio if needed
            if source_type == "Video File":
                progress(0.3, desc="Converting video to audio...")
                
                command = [
                    "ffmpeg", "-i", source_file_path,
                    "-acodec", "libmp3lame", "-ar", "44100", "-ac", "1",
                    "-b:a", "128k", "-y", target_mp3_path
                ]
                subprocess.run(command, capture_output=True, text=True, check=True)
                audio_file_ready = True
                
                # Clean up video file
                if os.path.exists(source_file_path):
                    os.remove(source_file_path)
                
                print(f"✅ Video converted to audio: {target_mp3_path}")
            
            else:  # Audio file
                progress(0.3, desc="Processing audio file...")
                
                if source_file_path != target_mp3_path:
                    file_ext = os.path.splitext(source_file_path)[1].lower()
                    if file_ext != '.mp3':
                        # Convert to MP3
                        command = [
                            "ffmpeg", "-i", source_file_path,
                            "-acodec", "libmp3lame", "-ar", "44100", "-ac", "1",
                            "-b:a", "128k", "-y", target_mp3_path
                        ]
                        subprocess.run(command, capture_output=True, text=True, check=True)
                    else:
                        # Just copy MP3
                        shutil.copy2(source_file_path, target_mp3_path)
                    
                    # Clean up source file
                    if source_file_path != target_mp3_path and os.path.exists(source_file_path):
                        os.remove(source_file_path)
                
                audio_file_ready = True
                print(f"✅ Audio file ready: {target_mp3_path}")
            
            # Check file size
            if audio_file_ready and os.path.exists(target_mp3_path):
                mp3_file_size_bytes = os.path.getsize(target_mp3_path)
                mp3_file_size_mb = mp3_file_size_bytes / (1024 * 1024)
                print(f"Audio file size: {mp3_file_size_mb:.2f} MB")
                
                if mp3_file_size_bytes > 1024 * 1024 * 1024:  # 1GB
                    return "❌ Error: Audio file is larger than 1GB limit", "", "", None, None, None, None
            
            # Transcribe
            if not loaded_from_cache and audio_file_ready:
                progress(0.5, desc="Starting transcription...")
                
                try:
                    custom_timeout = httpx.Timeout(60.0, read=900.0, connect=10.0)
                    client = ElevenLabs(api_key=api_key, timeout=custom_timeout)
                    
                    with open(target_mp3_path, "rb") as audio_file_object:
                        transcription_response_obj = client.speech_to_text.convert(
                            file=audio_file_object,
                            model_id="scribe_v1_experimental",
                            language_code=language,
                            diarize=True,
                            tag_audio_events=False,
                            timestamps_granularity="word"
                        )
                    
                    if transcription_response_obj:
                        if hasattr(transcription_response_obj, 'text'):
                            full_transcript_text = transcription_response_obj.text
                        if hasattr(transcription_response_obj, 'words'):
                            words_data = transcription_response_obj.words
                        
                        # Save to cache
                        response_dict = transcription_response_obj.model_dump()
                        with open(raw_json_cache_path, 'w', encoding='utf-8') as f:
                            json.dump(response_dict, f, ensure_ascii=False, indent=4)
                        
                        progress(0.7, desc="Transcription completed!")
                        print("✅ Transcription successful!")
                    
                except Exception as e:
                    return f"❌ Transcription error: {str(e)}", "", "", None, None, None, None
        
        # Step 4: Generate outputs (NO speaker identification/mapping)
        progress(0.75, desc="Generating transcript...")
        
        # Generate TXT transcript
        txt_content = ""
        if words_data:
            speaker_segments = []
            current_segment = None
            
            for word_obj in words_data:
                word_text_val = get_word_attr(word_obj, 'text')
                word_start_val = get_word_attr(word_obj, 'start')
                speaker_id_val = get_word_attr(word_obj, 'speaker_id', "speaker_unknown")
                
                if not (word_text_val and word_start_val is not None):
                    continue
                
                if current_segment is None or current_segment['speaker'] != speaker_id_val:
                    if current_segment:
                        speaker_segments.append(current_segment)
                    current_segment = {
                        'speaker': speaker_id_val,
                        'start_time': word_start_val,
                        'text_parts': [word_text_val]
                    }
                else:
                    current_segment['text_parts'].append(word_text_val)
            
            if current_segment:
                speaker_segments.append(current_segment)
            
            # Build TXT content - keeping original speaker IDs
            for segment in speaker_segments:
                txt_content += f"[{format_txt_timestamp(segment['start_time'])}] {segment['speaker']}:\n"
                txt_content += f"{' '.join(segment['text_parts'])}\n\n"
        else:
            txt_content = full_transcript_text
        
        # Generate SRT subtitles
        srt_content = ""
        if words_data:
            srt_cues = []
            cue_number = 1
            MAX_CUE_DURATION_SECONDS = 7
            MAX_CUE_CHARACTERS = 120
            current_cue_words_info = []
            current_cue_speaker = None
            current_cue_start_time = None
            
            for word_obj in words_data:
                word_text_val = get_word_attr(word_obj, 'text')
                word_start_val = get_word_attr(word_obj, 'start')
                word_end_val = get_word_attr(word_obj, 'end')
                speaker_id_val = get_word_attr(word_obj, 'speaker_id', "speaker_unknown")
                
                if not (word_text_val and word_start_val is not None and word_end_val is not None):
                    continue
                
                finalize_current_cue = False
                
                if not current_cue_words_info:
                    current_cue_speaker = speaker_id_val
                    current_cue_start_time = word_start_val
                elif (speaker_id_val != current_cue_speaker or
                      (word_end_val - current_cue_start_time) > MAX_CUE_DURATION_SECONDS or
                      len(" ".join([w['text'] for w in current_cue_words_info] + [word_text_val])) > MAX_CUE_CHARACTERS):
                    finalize_current_cue = True
                
                if finalize_current_cue and current_cue_words_info:
                    cue_text_str = " ".join([w['text'] for w in current_cue_words_info])
                    srt_cues.append(f"{cue_number}\n{format_srt_time(current_cue_start_time)} --> {format_srt_time(current_cue_words_info[-1]['end_time'])}\n{current_cue_speaker}: {cue_text_str}\n")
                    cue_number += 1
                    current_cue_words_info = []
                    current_cue_speaker = speaker_id_val
                    current_cue_start_time = word_start_val
                
                current_cue_words_info.append({'text': word_text_val, 'end_time': word_end_val})
            
            if current_cue_words_info:
                cue_text_str = " ".join([w['text'] for w in current_cue_words_info])
                srt_cues.append(f"{cue_number}\n{format_srt_time(current_cue_start_time)} --> {format_srt_time(current_cue_words_info[-1]['end_time'])}\n{current_cue_speaker}: {cue_text_str}\n")
            
            srt_content = "\n".join(srt_cues)
        
        # Step 5: Create and save files
        progress(0.95, desc="Creating files...")
        
        # Save files with new naming convention
        txt_filename = f"{base_filename}_transcript.txt"
        srt_filename = f"{base_filename}_subtitles.srt"
        mp3_filename = f"{base_filename}.mp3"
        json_filename = f"{base_filename}_raw_transcript.json"
        
        txt_path = os.path.join(temp_dir, txt_filename)
        srt_path = os.path.join(temp_dir, srt_filename)
        mp3_path = target_mp3_path
        json_path = raw_json_cache_path
        
        # Write files
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        if srt_content:
            with open(srt_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
        
        progress(1.0, desc="Processing completed!")
        
        # Count speakers
        unique_speakers = set()
        if words_data:
            for word_obj in words_data:
                speaker_id = get_word_attr(word_obj, 'speaker_id', "speaker_unknown")
                unique_speakers.add(speaker_id)
        
        # Final status
        status_message = f"""✅ Processing completed successfully!

📊 Summary:
• Episode: {clean_episode_name}
• Source: {source_type}
• Method: {delivery_method}
• Language: {language}
• Speakers found: {len(unique_speakers) if words_data else 'N/A'}

📁 Generated files:
• TXT transcript: {txt_filename}
• SRT subtitles: {srt_filename}
• Audio file: {mp3_filename}
• JSON cache: {json_filename}

🎉 Select which files to download below!"""
        
        # Return file paths for download options
        file_paths = {
            'txt': txt_path if os.path.exists(txt_path) else None,
            'srt': srt_path if os.path.exists(srt_path) and srt_content else None,
            'mp3': mp3_path if os.path.exists(mp3_path) else None,
            'json': json_path if os.path.exists(json_path) else None
        }
        
        return status_message, txt_content, srt_content, file_paths['txt'], file_paths['srt'], file_paths['mp3'], file_paths['json']
        
    except Exception as e:
        return f"❌ Error during processing: {str(e)}", "", "", None, None, None, None

def handle_download_selection(txt_selected, srt_selected, mp3_selected, json_selected, txt_path, srt_path, mp3_path, json_path, episode_name):
    """Handle the download based on checkbox selection"""
    
    if not episode_name:
        return None, "❌ No files processed yet"
    
    # Count selected files
    selected_files = []
    selected_paths = []
    
    if txt_selected and txt_path and os.path.exists(txt_path):
        selected_files.append(os.path.basename(txt_path))
        selected_paths.append(txt_path)
    
    if srt_selected and srt_path and os.path.exists(srt_path):
        selected_files.append(os.path.basename(srt_path))
        selected_paths.append(srt_path)
    
    if mp3_selected and mp3_path and os.path.exists(mp3_path):
        selected_files.append(os.path.basename(mp3_path))
        selected_paths.append(mp3_path)
    
    if json_selected and json_path and os.path.exists(json_path):
        selected_files.append(os.path.basename(json_path))
        selected_paths.append(json_path)
    
    if not selected_files:
        return None, "❌ No files selected for download"
    
    # Clean episode name for file naming
    clean_episode_name = "".join(c if c.isalnum() or c in ('_', '-') else '_' for c in episode_name.strip())
    
    if len(selected_files) == 1:
        # Single file - return it directly
        return selected_paths[0], f"✅ Downloading: {selected_files[0]}"
    else:
        # Multiple files - create ZIP
        temp_dir = tempfile.mkdtemp()
        zip_filename = f"{clean_episode_name}_selected_files.zip"
        zip_path = os.path.join(temp_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in selected_paths:
                zf.write(file_path, os.path.basename(file_path))
        
        file_list = ", ".join(selected_files)
        return zip_path, f"✅ Created ZIP with {len(selected_files)} files: {file_list}"

# Create the Gradio interface
def create_interface():
    with gr.Blocks(title="Valuebell Transcriber", theme=gr.themes.Soft()) as interface:
        gr.Markdown("# 🔔 Valuebell Transcriber")
        gr.Markdown("*Upload your audio or video files to get accurate transcripts with automatic speaker detection. Perfect for podcasts, interviews, and meetings.*")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## ⚙️ Settings")
                
                episode_name = gr.Textbox(
                    label="Episode Name",
                    placeholder="e.g., episode_01_interview_tech",
                    info="Use only letters, numbers, underscore, and dash"
                )
                
                source_type = gr.Radio(
                    choices=["Video File", "Audio File", "JSON Transcript"],
                    label="Source File Type",
                    value="Audio File",
                    info="What type of file are you uploading?"
                )
                
                delivery_method = gr.Radio(
                    choices=["File Upload", "URL"],
                    label="How to provide your file?",
                    value="File Upload"
                )
                
            with gr.Column(scale=1):
                gr.Markdown("## 🌐 Language & API")
                
                language = gr.Dropdown(
                    choices=[
                        ("Hebrew", "heb"),
                        ("English", "en"),
                        ("Spanish", "es"),
                        ("French", "fr"),
                        ("German", "de"),
                        ("Italian", "it"),
                        ("Portuguese", "pt"),
                        ("Russian", "ru"),
                        ("Chinese", "zh"),
                        ("Japanese", "ja"),
                        ("Korean", "ko")
                    ],
                    label="Language",
                    value="heb",
                    info="Select the primary language of your podcast"
                )
                
                api_key = gr.Textbox(
                    label="ElevenLabs API Key",
                    type="password",
                    placeholder="Enter your API key here",
                    info="Required for video/audio transcription"
                )
        
        with gr.Row():
            with gr.Column():
                file_input = gr.File(
                    label="Upload File",
                    file_types=[".mp4", ".avi", ".mov", ".mp3", ".wav", ".m4a", ".json"],
                    visible=True
                )
                
                url_input = gr.Textbox(
                    label="File URL",
                    placeholder="https://drive.google.com/... or https://dropbox.com/...",
                    visible=False,
                    info="Supports Google Drive, Dropbox, WeTransfer"
                )
        
        # Show/hide inputs based on delivery method
        def update_inputs(delivery_method):
            if delivery_method == "File Upload":
                return gr.update(visible=True), gr.update(visible=False)
            else:
                return gr.update(visible=False), gr.update(visible=True)
        
        delivery_method.change(
            fn=update_inputs,
            inputs=[delivery_method],
            outputs=[file_input, url_input]
        )
        
        with gr.Row():
            process_btn = gr.Button("🚀 Start Processing", variant="primary", size="lg")
            clear_btn = gr.Button("🗑️ Clear All", variant="secondary")
        
        with gr.Row():
            with gr.Column():
                status_output = gr.Textbox(
                    label="Status",
                    lines=15,
                    interactive=False
                )
            
        with gr.Tabs():
            with gr.TabItem("📝 TXT Transcript"):
                txt_output = gr.Textbox(
                    label="TXT Transcript",
                    lines=15,
                    interactive=False,
                    show_copy_button=True
                )
            
            with gr.TabItem("📺 SRT Subtitles"):
                srt_output = gr.Textbox(
                    label="SRT Subtitles",
                    lines=15,
                    interactive=False,
                    show_copy_button=True
                )
        
        # Download selection section
        gr.Markdown("## 📥 Download Files")
        gr.Markdown("*Select files → Click 'Prepare Download' → Click the download link that appears*")
        
        with gr.Row():
            txt_checkbox = gr.Checkbox(label="📝 Transcript (.txt)", value=True)  # Selected by default
            srt_checkbox = gr.Checkbox(label="📺 Subtitles (.srt)", value=False)
            mp3_checkbox = gr.Checkbox(label="🎵 Audio (.mp3)", value=False)
            json_checkbox = gr.Checkbox(label="💾 Raw Data (.json)", value=False)
        
        with gr.Row():
            download_btn = gr.Button("📦 Prepare Download", variant="primary", size="lg")
        
        with gr.Row():
            download_status = gr.Textbox(label="Step 2: Click the download link below", lines=2, interactive=False)
        
        with gr.Row():
            download_file = gr.File(label="⬇️ Click here to download your files", interactive=False)
        
        # Hidden components to store file paths
        txt_path_store = gr.State()
        srt_path_store = gr.State()
        mp3_path_store = gr.State()
        json_path_store = gr.State()
        
        # Event handlers
        process_btn.click(
            fn=process_transcript_complete,
            inputs=[
                episode_name,
                source_type,
                delivery_method,
                file_input,
                url_input,
                language,
                api_key
            ],
            outputs=[status_output, txt_output, srt_output, txt_path_store, srt_path_store, mp3_path_store, json_path_store],
            show_progress=True
        )
        
        download_btn.click(
            fn=handle_download_selection,
            inputs=[
                txt_checkbox, srt_checkbox, mp3_checkbox, json_checkbox,
                txt_path_store, srt_path_store, mp3_path_store, json_path_store,
                episode_name
            ],
            outputs=[download_file, download_status]
        )
        
        def clear_all():
            return ("", "Audio File", "File Upload", None, "", "heb", "", "", "", "", None, None, None, None, "", None)
        
        clear_btn.click(
            fn=clear_all,
            outputs=[
                episode_name, source_type, delivery_method, file_input,
                url_input, language, api_key, status_output, txt_output, srt_output, 
                txt_path_store, srt_path_store, mp3_path_store, json_path_store, download_status, download_file
            ]
        )

    return interface

# Launch the interface
if __name__ == "__main__":
    print("🔔 Starting Valuebell Transcriber...")
    print("=" * 50)
    
    interface = create_interface()
    interface.launch(
        server_name="0.0.0.0",  # Required for Hugging Face Spaces
        server_port=7860,       # Required for Hugging Face Spaces
        share=False,            # Don't need share link on Spaces
        show_error=True
    )
    
    print("\n" + "="*60)
    print("✅ Valuebell Transcriber is now running!")
    print("=" * 60)