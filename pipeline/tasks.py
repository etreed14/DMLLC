"""
Orchestration layer for the transcription pipeline.

This module defines helper functions that are called from the Cloud
Function entrypoint in :mod:`pipeline.main`.  They coordinate the steps of
the pipeline:

* When an audio file is uploaded to the **Audios/** folder, the pipeline
  downloads it, converts it to WAV, uploads the converted file, runs
  speech‑to‑text, formats the transcript, optionally cleans it, and
  optionally summarises it.
* When a transcript is uploaded to **Transcripts/**, the pipeline can
  generate a summary.

The functions handle common edge cases such as unsupported file types,
missing transcripts or generative model failures.
"""

from __future__ import annotations

import json
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict

from google.cloud import storage

from . import audio_processor, sttService, transcriptFormatter, transcriptCleaner, summarizer

logger = logging.getLogger(__name__)

# Define folder prefixes
AUDIO_PREFIX = "Audios/"
TRANSCRIPTS_PREFIX = "Transcripts/"


def _downloadBlob(bucket: storage.Bucket, blob_name: str) -> str:
    """Download a blob from GCS to a temporary file and return the local path."""
    blob = bucket.blob(blob_name)
    fd, tmp_path = tempfile.mkstemp(suffix=Path(blob_name).suffix)
    os.close(fd)
    blob.download_to_filename(tmp_path)
    return tmp_path


def _uploadBlob(bucket: storage.Bucket, local_path: str, dest_name: str, *, content_type: str | None = None) -> None:
    """Upload a local file to GCS under ``dest_name``."""
    blob = bucket.blob(dest_name)
    blob.upload_from_filename(local_path, content_type=content_type)


def _deriveBaseName(file_name: str) -> str:
    """Derive a base name for transcripts from an audio file name.

    The audio files are expected to be named like ``YYYY‑MM‑DD_TICKER.mp3`` or
    similar.  This function strips the folder prefix and extension and returns
    the remainder.  You can customise this to parse additional metadata.
    """
    base = os.path.basename(file_name)
    # Remove known audio extensions
    base = re.sub(r"\.(mp3|m4a|wav|flac|mp4)$", "", base, flags=re.IGNORECASE)
    return base


def processAudioUpload(bucket_name: str, file_name: str) -> None:
    """Process an uploaded audio file.

    This function is intended to be called when a file is added to the
    **Audios/** folder in Cloud Storage.  It performs the following steps:

    1. Download the file locally.
    2. Convert it to a 16 kHz mono WAV file if necessary.
    3. Upload the converted file back to the bucket under the same name but
       with a ``.wav`` extension.
    4. Transcribe the audio using Google Speech‑to‑Text.
    5. Save the raw JSON response and formatted transcript to the
       **Transcripts/** folder.
    6. Optionally clean the transcript and generate a summary.

    Args:
        bucket_name: Name of the Cloud Storage bucket.
        file_name: Full path of the uploaded file relative to the bucket.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    if not file_name.startswith(AUDIO_PREFIX):
        logger.info("Ignoring file outside of %s: %s", AUDIO_PREFIX, file_name)
        return
    ext = Path(file_name).suffix.lower()
    if ext not in audio_processor.SUPPORTED_EXTENSIONS:
        logger.info("Unsupported audio extension %s for %s", ext, file_name)
        return
    logger.info("Processing audio upload %s", file_name)
    # Download original file
    local_path = _downloadBlob(bucket, file_name)
    converted_path = None
    try:
        # Convert to WAV if necessary
        if ext != ".wav":
            converted_path = audioProcessor.convertToWav(local_path)
            # Upload converted WAV back to the same folder with .wav suffix
            wav_name = re.sub(r"\.(mp3|m4a|flac|mp4)$", ".wav", file_name, flags=re.IGNORECASE)
            _uploadBlob(bucket, converted_path, wav_name, content_type="audio/wav")
            wav_uri = f"gs://{bucket_name}/{wav_name}"
        else:
            wav_uri = f"gs://{bucket_name}/{file_name}"
        # Transcribe
        response_dict = sttService.transcribe(wav_uri)
        # Save raw JSON
        base_name = _deriveBaseName(file_name)
        json_name = f"{TRANSCRIPTS_PREFIX}JSON_{base_name}.json"
        json_blob = bucket.blob(json_name)
        json_blob.upload_from_string(json.dumps(response_dict), content_type="application/json")
        logger.info("Saved raw transcript to %s", json_name)
        # Format transcript
        words = transcriptFormatter.flattenWordInfo(response_dict)
        formatted = transcriptFormatter.formatTranscript(words)
        # Optionally clean transcript
        if os.environ.get("ENABLE_CLEANING", "false").lower() == "true":
            formatted = transcriptCleaner.cleanTranscript(formatted, words=words)
        text_name = f"{TRANSCRIPTS_PREFIX}{base_name}.txt"
        txt_blob = bucket.blob(text_name)
        txt_blob.upload_from_string(formatted, content_type="text/plain")
        logger.info("Saved formatted transcript to %s", text_name)
        # Optionally summarise
        if os.environ.get("ENABLE_SUMMARISER", "false").lower() == "true":
            summary = summarizer.summarise(formatted)
            if summary:
                summary_name = f"{TRANSCRIPTS_PREFIX}{base_name}_summary.txt"
                summary_blob = bucket.blob(summary_name)
                summary_blob.upload_from_string(summary, content_type="text/plain")
                logger.info("Saved summary to %s", summary_name)
    finally:
        # Clean up temporary files
        audioProcessor.cleanupTempFile(local_path)
        audioProcessor.cleanupTempFile(converted_path)


def processTranscriptUpload(bucket_name: str, file_name: str) -> None:
    """Generate a summary for a newly uploaded transcript.

    This function is called when a user drops a transcript (a `.txt` file)
    directly into the **Transcripts/** folder.  It will skip files that
    already appear to be summaries or raw JSON responses.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    if not file_name.startswith(TRANSCRIPTS_PREFIX):
        logger.info("Ignoring non-transcript file %s", file_name)
        return
    base_name = os.path.basename(file_name)
    if base_name.startswith("JSON_") or base_name.endswith("_summary.txt"):
        logger.info("Ignoring auxiliary transcript file %s", file_name)
        return
    if not file_name.endswith(".txt"):
        logger.info("Ignoring non-text transcript file %s", file_name)
        return
    local_path = _downloadBlob(bucket, file_name)
    try:
        with open(local_path, "r", encoding="utf-8") as f:
            text = f.read()
        if not text.strip():
            logger.info("Transcript %s is empty; skipping summarisation", file_name)
            return
        summary = summarizer.summarise(text)
        if not summary:
            logger.info("No summary generated for %s", file_name)
            return
        name_no_ext = os.path.splitext(file_name)[0]
        summary_name = f"{name_no_ext}_summary.txt"
        blob = bucket.blob(summary_name)
        blob.upload_from_string(summary, content_type="text/plain")
        logger.info("Saved summary to %s", summary_name)
    finally:
        audioProcessor.cleanupTempFile(local_path)
