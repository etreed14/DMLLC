"""
Cloud Function for transcribing audio files uploaded to Cloud Storage.

When an audio file is uploaded to the ``audios/`` folder in the ``dmllc``
bucket, this function is invoked.  It uses Google Cloud Speech‑to‑Text to
perform diarised transcription with word‑level time offsets and confidences.
The raw response is saved as a JSON file prefixed with ``JSON_`` in the
``transcripts/`` folder.  The function then imports the
``format_transcript`` module to convert the raw result into a human
readable transcript.  The formatted transcript is saved back to
``transcripts/`` with the same base name but without the ``JSON_`` prefix
and with a ``.txt`` extension.  This naming convention prevents the
formatter from reprocessing the finished transcript.

To deploy this function, ensure ``google-cloud-speech`` and
``google-cloud-storage`` are included in your ``requirements.txt``.
"""

import json
import os
import re
import logging
from typing import Any, Dict

from google.cloud import speech_v1p1beta1 as speech  # Use v1p1beta1 for advanced features
from google.cloud import storage
from google.protobuf.json_format import MessageToDict

import format_transcript  # Assumes this module is available in the same package

logging.basicConfig(level=logging.INFO, format="%(message)s")

OUTPUT_BUCKET = os.environ.get("OUTPUT_BUCKET", "dmllc")

# Folder prefixes
AUDIO_PREFIX = os.environ.get("AUDIO_PREFIX", "audios/")
TRANSCRIPTS_PREFIX = os.environ.get("TRANSCRIPTS_PREFIX", "transcripts/")


def transcribe_audio(event: Dict[str, Any], context: Any) -> None:
    """Background Cloud Function to process audio files as they are uploaded.

    Args:
        event: The dictionary with data specific to this type of event.  The
            ``event`` contains the bucket and name of the file.
        context: Metadata of triggering event.
    """
    bucket_name = event["bucket"]
    file_name = event["name"]
    logging.info(json.dumps({"event": "gcs_trigger", "bucket": bucket_name, "file": file_name}))

    try:

        # Only process files in the designated audio folder
        if not file_name.startswith(AUDIO_PREFIX):
            logging.info(json.dumps({"event": "skip_prefix", "file": file_name}))
            return
        # Only process supported audio file types
        if not re.search(r"\.(mp3|wav|flac|m4a|mp4)$", file_name, re.IGNORECASE):
            logging.info(json.dumps({"event": "skip_type", "file": file_name}))
            return

        audio_uri = f"gs://{bucket_name}/{file_name}"
        logging.info(json.dumps({"event": "start_transcription", "gcs_uri": audio_uri}))

        # Configure diarisation and word‑level features
        diarization_config = speech.SpeakerDiarizationConfig(
            enable_speaker_diarization=True,
            min_speaker_count=1,
            max_speaker_count=6,
        )
        recognition_config = speech.RecognitionConfig(
            enable_word_time_offsets=True,
            enable_word_confidence=True,
            enable_automatic_punctuation=True,
            diarization_config=diarization_config,
            language_code="en-US",
        )
        audio = speech.RecognitionAudio(uri=audio_uri)

        speech_client = speech.SpeechClient()
        operation = speech_client.long_running_recognize(config=recognition_config, audio=audio)
        response = operation.result()
        logging.info(json.dumps({"event": "transcription_complete"}))

        # Convert response to a serialisable dict
        response_dict = MessageToDict(response._pb)
        # Derive output names
        base_name = os.path.splitext(os.path.basename(file_name))[0]
        raw_json_name = f"{TRANSCRIPTS_PREFIX}JSON_{base_name}.json"
        formatted_name = f"{TRANSCRIPTS_PREFIX}{base_name}.txt"

        storage_client = storage.Client()
        bucket = storage_client.bucket(OUTPUT_BUCKET)

        # Save raw JSON
        raw_blob = bucket.blob(raw_json_name)
        raw_blob.upload_from_string(json.dumps(response_dict), content_type="application/json")
        logging.info(json.dumps({"event": "raw_saved", "path": raw_json_name}))

        # Format the transcript using the existing module
        words_info = format_transcript.flatten_word_info(response_dict)
        formatted_text = format_transcript.format_transcript(words_info)
        formatted_blob = bucket.blob(formatted_name)
        formatted_blob.upload_from_string(formatted_text, content_type="text/plain")
        logging.info(json.dumps({"event": "formatted_saved", "path": formatted_name}))

    except Exception:
        logging.exception("Error in transcribe_audio")

