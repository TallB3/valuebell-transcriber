"""
Formatting utilities for timestamps and text processing
"""


def format_txt_timestamp(seconds_float):
    """Format timestamp for TXT files"""
    if seconds_float is None:
        return "00:00:00"
    seconds_int = int(seconds_float)
    hours = seconds_int // 3600
    minutes = (seconds_int % 3600) // 60
    seconds = seconds_int % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def format_srt_time(seconds_float):
    """Format timestamp for SRT files"""
    if seconds_float is None:
        return "00:00:00,000"
    millis = round(seconds_float * 1000)
    hours = millis // (3600 * 1000)
    millis %= (3600 * 1000)
    minutes = millis // (60 * 1000)
    millis %= (60 * 1000)
    seconds = millis // 1000
    milliseconds = millis % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"