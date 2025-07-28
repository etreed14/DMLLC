"""
Cloud Function entrypoints for the transcription pipeline.

This module exposes two functions:

* ``gcs_event`` – a background function triggered by Cloud Storage events.
  It inspects the file path to determine whether to process an audio upload
  or a transcript upload.
* ``http_trigger`` – an HTTP function you can invoke manually for testing.

Environment variables control optional features:

* ``ENABLE_CLEANING`` – Set to ``true`` to enable transcript cleaning.
* ``ENABLE_SUMMARISER`` – Set to ``true`` to enable summarisation.
* ``OUTPUT_BUCKET`` – Bucket name to write outputs (defaults to the event
  bucket).
* ``GENAI_API_KEY`` – API key for the generative model.  Required for
  cleaning and summarisation.

Deployment typically uses the ``gcs_event`` function as the entrypoint.
"""

import logging
import os
from typing import Dict, Any

from . import tasks

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def gcs_event(event: Dict[str, Any], context: Any) -> None:
    """Background function triggered by Cloud Storage.

    The event contains the ``bucket`` and ``name`` of the uploaded file.  This
    function decides whether the file is an audio file or a transcript and
    dispatches processing accordingly.
    """
    bucket = event.get("bucket")
    name = event.get("name")
    if not bucket or not name:
        logger.warning("Received event with missing bucket or name: %s", event)
        return
    # Use OUTPUT_BUCKET if defined, allowing outputs to be redirected to a
    # different bucket (useful for separating input and output buckets).
    output_bucket = os.environ.get("OUTPUT_BUCKET", bucket)
    if name.startswith(tasks.AUDIO_PREFIX):
        tasks.processAudioUpload(output_bucket, name)
    elif name.startswith(tasks.TRANSCRIPTS_PREFIX):
        tasks.processTranscriptUpload(output_bucket, name)
    else:
        logger.info("Unhandled upload path: %s", name)


def http_trigger(request) -> str:
    """HTTP entrypoint for manual invocation.

    You can call this function via HTTP with a JSON body containing ``bucket``
    and ``name`` fields to simulate a Cloud Storage event.  This is handy
    for local testing or manual reprocessing.
    """
    try:
        data = request.get_json(silent=True) or {}
        bucket = data.get("bucket")
        name = data.get("name")
        if not bucket or not name:
            return "Missing 'bucket' or 'name' in request", 400
        gcs_event({"bucket": bucket, "name": name}, context=None)
        return "OK", 200
    except Exception as exc:  # pragma: no cover
        logger.exception("Error in HTTP trigger: %s", exc)
        return f"Error: {exc}", 500
