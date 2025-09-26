"""
Output generation for different transcript formats (TXT, SRT, JSON)
"""
from utils.file_utils import get_word_attr
from utils.format_utils import format_txt_timestamp, format_srt_time
from processors.transcript_processor import group_words_by_speaker
from config.settings import (
    TRANSCRIPT_DISCLAIMER,
    MAX_CUE_DURATION_SECONDS,
    MAX_CUE_CHARACTERS
)


def generate_txt_transcript(words_data, full_transcript_text=""):
    """Generate TXT format transcript with speaker identification"""
    txt_content = TRANSCRIPT_DISCLAIMER

    if words_data:
        speaker_segments = group_words_by_speaker(words_data)

        # Build TXT content - keeping original speaker IDs
        for segment in speaker_segments:
            txt_content += f"[{format_txt_timestamp(segment['start_time'])}] {segment['speaker']}:\n"
            txt_content += f"{' '.join(segment['text_parts'])}\n\n"
    else:
        txt_content = TRANSCRIPT_DISCLAIMER + full_transcript_text

    return txt_content


def generate_srt_subtitles(words_data):
    """Generate SRT format subtitles with speaker identification"""
    if not words_data:
        return ""

    srt_cues = []
    cue_number = 1
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
            srt_cues.append(
                f"{cue_number}\n"
                f"{format_srt_time(current_cue_start_time)} --> {format_srt_time(current_cue_words_info[-1]['end_time'])}\n"
                f"{current_cue_speaker}: {cue_text_str}\n"
            )
            cue_number += 1
            current_cue_words_info = []
            current_cue_speaker = speaker_id_val
            current_cue_start_time = word_start_val

        current_cue_words_info.append({'text': word_text_val, 'end_time': word_end_val})

    # Handle final cue
    if current_cue_words_info:
        cue_text_str = " ".join([w['text'] for w in current_cue_words_info])
        srt_cues.append(
            f"{cue_number}\n"
            f"{format_srt_time(current_cue_start_time)} --> {format_srt_time(current_cue_words_info[-1]['end_time'])}\n"
            f"{current_cue_speaker}: {cue_text_str}\n"
        )

    return "\n".join(srt_cues)


def save_transcript_files(temp_dir, base_filename, txt_content, srt_content, json_content):
    """
    Save all transcript formats to files

    Returns:
        dict: Dictionary with file paths for each format
    """
    import os
    from utils.file_utils import generate_output_filenames

    filenames = generate_output_filenames(base_filename)
    file_paths = {}

    # Save TXT file
    txt_path = os.path.join(temp_dir, filenames['txt'])
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    file_paths['txt'] = txt_path

    # Save SRT file (if content exists)
    if srt_content:
        srt_path = os.path.join(temp_dir, filenames['srt'])
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        file_paths['srt'] = srt_path
    else:
        file_paths['srt'] = None

    # Save JSON file (if content exists)
    if json_content:
        json_path = os.path.join(temp_dir, filenames['json'])
        with open(json_path, 'w', encoding='utf-8') as f:
            f.write(json_content)
        file_paths['json'] = json_path
    else:
        file_paths['json'] = None

    return file_paths