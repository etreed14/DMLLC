"""
Audio conversion utilities.

This module provides functions to convert incoming audio files to a
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


def convertToWav(inputPath: str, *, targetSampleRate: int = 16_000) -> str:
    """Convert an audio file to a 16 kHz mono WAV file.

    Args:
        inputPath: Path to the source audio file.  Supported extensions are
            defined in :data:`SUPPORTED_EXTENSIONS`.
        targetSampleRate: Desired sample rate for the output WAV.

    Returns:
        The path to the converted WAV file.  The file lives in a temporary
        directory and should be cleaned up by the caller.

    Raises:
        ValueError: If the file extension is unsupported.
    """
    ext = Path(inputPath).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported audio type: {ext}")
    audio = AudioSegment.from_file(inputPath)
    audio = audio.set_channels(1).set_frame_rate(targetSampleRate)
    fd, tmpPath = tempfile.mkstemp(suffix=".wav")
    os.close(fd)
    audio.export(tmpPath, format="wav")
    return tmpPath


def isSupportedAudio(path: str) -> bool:
    """Check whether the file at ``path`` has a supported audio extension."""
    return Path(path).suffix.lower() in SUPPORTED_EXTENSIONS


def cleanupTempFile(path: Optional[str]) -> None:
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
