#!/usr/bin/env python3
"""
Valuebell Transcriber - Modular Version
Professional transcription tool for podcasts, interviews, and meetings

This is the new modular version that orchestrates all the separate modules.
Once tested, this will replace the original app.py.
"""
import os
import json
import shutil
import tempfile
import gradio as gr

# Import our modular components
from config.settings import HF_SERVER_NAME, HF_SERVER_PORT
from utils.file_utils import clean_filename, detect_file_source
from services.download_service import download_file_from_source
from services.audio_service import get_audio_duration, process_audio_file
from services.transcription_service import TranscriptionService
from processors.transcript_processor import analyze_transcript_quality, count_unique_speakers
from processors.output_generator import generate_txt_transcript, generate_srt_subtitles, save_transcript_files
from services.file_service import handle_download_selection
from ui.interface import create_interface, get_clear_function


def process_transcript_complete(episode_name, source_type, delivery_method, file_input, url_input, language, api_key, progress=gr.Progress()):
    """Complete processing function that orchestrates all modules"""

    try:
        # Step 1: Validate inputs
        progress(0.05, desc="Validating inputs...")

        if not episode_name.strip():
            return "❌ Error: Episode name is required", "", "", "", None, None, None, None

        if delivery_method == "File Upload" and not file_input:
            return "❌ Error: Please upload a file", "", "", "", None, None, None, None

        if delivery_method == "URL" and not url_input.strip():
            return "❌ Error: Please provide a URL", "", "", "", None, None, None, None

        if source_type in ["Video File", "Audio File"] and not api_key.strip():
            return "❌ Error: ElevenLabs API key is required for transcription", "", "", "", None, None, None, None

        # Step 2: Setup
        progress(0.1, desc="Setting up processing...")

        # Clean episode name
        clean_episode_name = clean_filename(episode_name.strip())

        # Create temp directory for this session
        temp_dir = tempfile.mkdtemp()

        # File paths
        base_filename = clean_episode_name
        target_audio_path = None
        downloaded_source_path = os.path.join(temp_dir, f"{base_filename}_source")
        raw_json_cache_path = os.path.join(temp_dir, f"{base_filename}_raw_transcript.json")

        # Variables
        words_data = []
        full_transcript_text = ""
        loaded_from_cache = False
        audio_file_ready = False
        source_file_path = None
        audio_duration = None
        quality_warnings = []

        # Step 3: Handle file input
        progress(0.15, desc="Processing file input...")

        if source_type == "JSON Transcript":
            # Handle JSON file
            if delivery_method == "File Upload":
                if file_input is None:
                    return "❌ Error: No JSON file uploaded", "", "", "", None, None, None, None

                # Save uploaded file
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
                    return "❌ Error: JSON doesn't appear to be in ElevenLabs format", "", "", "", None, None, None, None

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
                    return "❌ Error: Downloaded JSON doesn't appear to be in ElevenLabs format", "", "", "", None, None, None, None

        else:
            # Handle video/audio files
            progress(0.2, desc="Processing media file...")

            if delivery_method == "File Upload":
                if file_input is None:
                    return "❌ Error: No media file uploaded", "", "", "", None, None, None, None

                # Save uploaded file
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

            # Get audio duration before conversion
            audio_duration = get_audio_duration(source_file_path)

            # Process audio file (convert to WAV or MP3 based on size)
            progress(0.3, desc="Converting to optimal audio format...")
            target_audio_path = process_audio_file(source_file_path, temp_dir, base_filename)

            # Clean up original downloaded source file
            if os.path.exists(source_file_path):
                os.remove(source_file_path)

            audio_file_ready = True

            # Transcribe using ElevenLabs
            if not loaded_from_cache and audio_file_ready:
                progress(0.5, desc="Starting transcription...")

                try:
                    transcription_service = TranscriptionService(api_key)
                    transcription_response = transcription_service.transcribe_audio(
                        target_audio_path,
                        language_code=language,
                        diarize=True
                    )

                    full_transcript_text, words_data, response_dict = transcription_service.extract_transcription_data(transcription_response)

                    # Save to cache
                    with open(raw_json_cache_path, 'w', encoding='utf-8') as f:
                        json.dump(response_dict, f, ensure_ascii=False, indent=4)

                    progress(0.7, desc="Transcription completed!")
                    print("✅ Transcription successful!")

                except Exception as e:
                    return f"❌ Transcription error: {str(e)}", "", "", "", None, None, None, None

        # Step 4: Analyze transcript quality
        progress(0.72, desc="Analyzing transcript quality...")
        quality_warnings = analyze_transcript_quality(words_data, audio_duration)

        # Step 5: Generate outputs
        progress(0.75, desc="Generating transcript formats...")

        # Generate TXT transcript
        txt_content = generate_txt_transcript(words_data, full_transcript_text)

        # Generate SRT subtitles
        srt_content = generate_srt_subtitles(words_data)

        # Load JSON for display
        json_content = ""
        if os.path.exists(raw_json_cache_path):
            with open(raw_json_cache_path, 'r', encoding='utf-8') as f:
                json_content = f.read()

        # Step 6: Save files
        progress(0.95, desc="Saving files...")

        file_paths = save_transcript_files(temp_dir, base_filename, txt_content, srt_content, json_content)

        # Add audio file to paths
        file_paths['audio'] = target_audio_path if target_audio_path and os.path.exists(target_audio_path) else None

        progress(1.0, desc="Processing completed!")

        # Count speakers
        unique_speakers_count = count_unique_speakers(words_data)

        # Generate audio filename for display
        audio_filename = os.path.basename(target_audio_path) if target_audio_path else ""

        # Final status - include warnings
        status_parts = [f"""✅ Processing completed successfully!

📊 Summary:
• Episode: {clean_episode_name}
• Source: {source_type}
• Method: {delivery_method}
• Language: {language}
• Speakers found: {unique_speakers_count if words_data else 'N/A'}

📁 Generated files:
• TXT transcript: {base_filename}_transcript.txt
• SRT subtitles: {base_filename}_subtitles.srt
• Audio file: {audio_filename}
• JSON data: {base_filename}_raw_transcript.json"""]

        # Add quality warnings if any
        if quality_warnings:
            status_parts.append("\n")
            status_parts.extend(quality_warnings)

        status_parts.append("\n🎉 Select which files to download below!")

        status_message = "\n".join(status_parts)

        # Return file paths for download options
        return status_message, txt_content, srt_content, json_content, file_paths['txt'], file_paths['srt'], file_paths['audio'], file_paths['json']

    except Exception as e:
        return f"❌ Error during processing: {str(e)}", "", "", "", None, None, None, None


def main():
    """Main function to launch the application"""
    print("🔔 Starting Valuebell Transcriber (Modular Version)...")
    print("=" * 60)

    # Get the clear function
    clear_function = get_clear_function()

    # Create the interface with our processing functions
    interface = create_interface(
        process_function=process_transcript_complete,
        download_function=handle_download_selection,
        clear_function=clear_function
    )

    # Launch the interface
    interface.launch(
        server_name=HF_SERVER_NAME,
        server_port=HF_SERVER_PORT,
        share=False,
        show_error=True
    )

    print("\n" + "="*60)
    print("✅ Valuebell Transcriber is now running!")
    print("=" * 60)


if __name__ == "__main__":
    main()