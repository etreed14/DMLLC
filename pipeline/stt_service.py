"""
Google Speech‑to‑Text service wrapper.

This module encapsulates interaction with the Google Cloud Speech API.  The
``transcribe`` function takes a Cloud Storage URI for a WAV file and
returns the API response as a dictionary.  It also exposes sensible
defaults for diarisation and word‑level metadata.

Usage::

    from pipeline.stt_service import transcribe

    response = transcribe("gs://my-bucket/Audios/example.wav", diarisation_speakers=4)
    print(response["results"])
"""

import logging
from typing import Any, Dict, Optional

from google.cloud import speech_v1p1beta1 as speech
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger(__name__)


def transcribe(
    gcs_uri: str,
    *,
    language_code: str = "en-US",
    diarisation_speakers: int = 2,
    enable_automatic_punctuation: bool = True,
    enable_word_confidence: bool = True,
    enable_word_time_offsets: bool = True,
) -> Dict[str, Any]:
    """Transcribe an audio file stored in Cloud Storage.

    Args:
        gcs_uri: A ``gs://`` URI pointing to the WAV file to transcribe.
        language_code: BCP‑47 language tag (default: ``en-US``).
        diarisation_speakers: Maximum number of speakers to detect.  The
            recogniser will attempt to diarise the audio into up to this many
            distinct speakers.
        enable_automatic_punctuation: Whether to insert punctuation marks.
        enable_word_confidence: Whether to include per‑word confidence scores.
        enable_word_time_offsets: Whether to include start/end times for each
            recognised word.

    Returns:
        A dictionary representation of the full Speech‑to‑Text response.
    """
    client = speech.SpeechClient()
    diarisation_config = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=1,
        max_speaker_count=diarisation_speakers,
    )
    
    # Explicitly set encoding and sample rate for the 16‑kHz LINEAR16 WAV file.
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
        enable_automatic_punctuation=enable_automatic_punctuation,
        enable_word_confidence=enable_word_confidence,
        enable_word_time_offsets=enable_word_time_offsets,
        diarization_config=diarisation_config,
    )

    audio = speech.RecognitionAudio(uri=gcs_uri)
    logger.info("Starting STT job for %s", gcs_uri)
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result()
    logger.info("STT job complete for %s", gcs_uri)
    return MessageToDict(response._pb)
