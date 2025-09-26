"""
File service for packaging and download preparation
"""
import os
import zipfile
import tempfile


def handle_download_selection(txt_selected, srt_selected, audio_selected, json_selected,
                              txt_path, srt_path, audio_path, json_path, episode_name):
    """Handle the download based on checkbox selection"""
    from utils.file_utils import clean_filename

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

    if audio_selected and audio_path and os.path.exists(audio_path):
        selected_files.append(os.path.basename(audio_path))
        selected_paths.append(audio_path)

    if json_selected and json_path and os.path.exists(json_path):
        selected_files.append(os.path.basename(json_path))
        selected_paths.append(json_path)

    if not selected_files:
        return None, "❌ No files selected for download"

    # Clean episode name for file naming
    clean_episode_name = clean_filename(episode_name)

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