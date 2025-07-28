"""
Google Speech‑to‑Text service wrapper.

This module encapsulates interaction with the Google Cloud Speech API.  The
``transcribe`` function takes a Cloud Storage URI for a WAV file and
returns the API response as a dictionary.  It also exposes sensible
defaults for diarisation and word‑level metadata.
"""

import logging
from typing import Any, Dict

from google.cloud import speech_v1p1beta1 as speech
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger(__name__)


def transcribe(
    gcsUri: str,
    *,
    languageCode: str = "en-US",
    diarisationSpeakers: int = 2,
    enableAutomaticPunctuation: bool = True,
    enableWordConfidence: bool = True,
    enableWordTimeOffsets: bool = True,
) -> Dict[str, Any]:
    """Transcribe an audio file stored in Cloud Storage.

    Args:
        gcsUri: A ``gs://`` URI pointing to the WAV file to transcribe.
        languageCode: BCP‑47 language tag (default: ``en-US``).
        diarisationSpeakers: Maximum number of speakers to detect.
        enableAutomaticPunctuation: Whether to insert punctuation marks.
        enableWordConfidence: Whether to include per‑word confidence scores.
        enableWordTimeOffsets: Whether to include start/end times for each
            recognised word.

    Returns:
        A dictionary representation of the full Speech‑to‑Text response.
    """
    client = speech.SpeechClient()
    diarisationConfig = speech.SpeakerDiarizationConfig(
        enable_speaker_diarization=True,
        min_speaker_count=1,
        max_speaker_count=diarisationSpeakers,
    )
    config = speech.RecognitionConfig(
        language_code=languageCode,
        enable_automatic_punctuation=enableAutomaticPunctuation,
        enable_word_confidence=enableWordConfidence,
        enable_word_time_offsets=enableWordTimeOffsets,
        diarization_config=diarisationConfig,
    )
    audio = speech.RecognitionAudio(uri=gcsUri)
    logger.info("Starting STT job for %s", gcsUri)
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result()
    logger.info("STT job complete for %s", gcsUri)
    return MessageToDict(response._pb)
