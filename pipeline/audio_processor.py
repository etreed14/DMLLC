"""
Audio conversion utilities.

This module provides a function to convert incoming audio files to a
standardised WAV format expected by the speech recogniser.  Audio
conversions are performed locally using the `pydub` library which in turn
relies on `ffmpeg`.  The pipeline ensures that audio is mono and
sampled at 16 kHz to meet Google Speech‑to‑Text best practices.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional

from pydub import AudioSegment


SUPPORTED_EXTENSIONS = {".mp3", ".m4a", ".flac", ".wav", ".mp4"}


def convert_to_wav(input_path: str, *, target_sample_rate: int = 16_000) -> str:
    """Convert an audio file to a 16 kHz mono WAV file.

    Args:
        input_path: Path to the source audio file.  Supported extensions are
            defined in :data:`SUPPORTED_EXTENSIONS`.
        target_sample_rate: Desired sample rate for the output WAV.

    Returns:
        The path to the converted WAV file.  The file lives in a temporary
        directory and should be cleaned up by the caller.

    Raises:
        ValueError: If the file extension is unsupported.
    """
    ext = Path(input_path).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported audio type: {ext}")
    # Load audio using pydub.  This will delegate to ffmpeg.
    audio = AudioSegment.from_file(input_path)
    # Convert to mono and the target sample rate.
    audio = audio.set_channels(1).set_frame_rate(target_sample_rate)
    # Write to a temporary file.
    fd, tmp_path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)  # Close the OS-level file descriptor; pydub will write to it.
    audio.export(tmp_path, format="wav")
    return tmp_path


def is_supported_audio(path: str) -> bool:
    """Check whether the file at ``path`` has a supported audio extension."""
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def cleanup_temp_file(path: Optional[str]) -> None:
    """Remove a temporary file if it exists.

    Args:
        path: Path to the temporary file.  Nothing happens if ``path`` is
            ``None`` or the file does not exist.
    """
    if path and os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass
