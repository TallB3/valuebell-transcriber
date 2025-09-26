"""
Transcript processing and quality analysis
"""
import numpy as np
from utils.file_utils import get_word_attr
from utils.format_utils import format_txt_timestamp
from config.settings import (
    OUTLIER_Z_SCORE_THRESHOLD,
    ABNORMAL_FINAL_TOKEN_DURATION,
    INCOMPLETE_TRANSCRIPT_THRESHOLD
)


def analyze_transcript_quality(words_data, audio_duration=None):
    """Analyze transcript for potential issues and return warnings"""
    warnings = []

    if not words_data:
        return warnings

    # Calculate durations for all tokens
    token_durations = []
    token_info = []

    for i, word_obj in enumerate(words_data):
        start_time = get_word_attr(word_obj, 'start')
        end_time = get_word_attr(word_obj, 'end')
        text = get_word_attr(word_obj, 'text', '')

        if start_time is not None and end_time is not None:
            duration = end_time - start_time
            token_durations.append(duration)
            token_info.append({
                'index': i,
                'text': text,
                'start': start_time,
                'end': end_time,
                'duration': duration
            })

    if not token_durations:
        return warnings

    # Check final token
    final_token = token_info[-1]
    if final_token['duration'] > ABNORMAL_FINAL_TOKEN_DURATION:
        warnings.append(
            f"⚠️ Final token has abnormal duration: '{final_token['text']}' "
            f"spans {final_token['duration']:.1f} seconds "
            f"({format_txt_timestamp(final_token['start'])} - {format_txt_timestamp(final_token['end'])})"
        )

    # Calculate statistics
    durations_array = np.array(token_durations)
    mean_duration = np.mean(durations_array)
    std_duration = np.std(durations_array)

    # Calculate z-scores (only if std > 0 to avoid division by zero)
    if std_duration > 0:
        z_scores = (durations_array - mean_duration) / std_duration

        # Find outliers (z-score > threshold)
        outliers = []

        for i, z_score in enumerate(z_scores):
            if z_score > OUTLIER_Z_SCORE_THRESHOLD:
                token = token_info[i]
                outliers.append(token)

        # Report outliers (excluding the final token if already reported)
        for outlier in outliers:
            if outlier['index'] != len(token_info) - 1:  # Not the final token
                warnings.append(
                    f"⚠️ Potential error: Token '{outlier['text']}' at "
                    f"{format_txt_timestamp(outlier['start'])} has unusual duration "
                    f"of {outlier['duration']:.1f} seconds (z-score: {z_scores[outlier['index']]:.2f})"
                )

    # Check for premature ending (if we have audio duration)
    if audio_duration is not None:
        last_token_end = token_info[-1]['end']
        time_difference = audio_duration - last_token_end

        # If more than threshold seconds of audio remain after last token
        if time_difference > INCOMPLETE_TRANSCRIPT_THRESHOLD:
            warnings.append(
                f"⚠️ Transcript may be incomplete: Audio duration is "
                f"{format_txt_timestamp(audio_duration)} but transcript ends at "
                f"{format_txt_timestamp(last_token_end)} "
                f"({time_difference:.1f} seconds unaccounted)"
            )

    # Add statistics summary if there are warnings
    if warnings:
        warnings.insert(0, f"📊 Token duration statistics: mean={mean_duration:.2f}s, std={std_duration:.2f}s")
        warnings.insert(0, "=" * 60)
        warnings.insert(0, "🔍 TRANSCRIPT QUALITY ANALYSIS")
        warnings.append("=" * 60)

    return warnings


def group_words_by_speaker(words_data):
    """Group words by speaker for transcript generation"""
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

    return speaker_segments


def count_unique_speakers(words_data):
    """Count unique speakers in the transcript"""
    unique_speakers = set()
    if words_data:
        for word_obj in words_data:
            speaker_id = get_word_attr(word_obj, 'speaker_id', "speaker_unknown")
            unique_speakers.add(speaker_id)
    return len(unique_speakers)