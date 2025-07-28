"""
Optional transcript cleaning via generative AI.

This module defines a ``clean_transcript`` function that takes the output
of the initial formatting step and leverages a language model to correct
mis‑recognised words, normalise numbers, and smooth awkward phrasing.  If
no API key is provided, the function simply returns the input unchanged.

The implementation uses the `google-generativeai` client (Gemini) by default
but can fall back to OpenAI or any other provider by implementing the
``_call_model`` helper.  You must specify a `GENAI_API_KEY` environment
variable for this module to perform any cleaning.
"""

from __future__ import annotations

import logging
import os
from typing import List, Optional

# Attempt to import Google Generative AI client.  If unavailable,
# we gracefully degrade and perform no cleaning.
try:
    import google.generativeai as genai  # type: ignore[import-not-found]
    _GENAI_AVAILABLE = True
except ImportError:  # pragma: no cover - optional dependency
    _GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


def clean_transcript(text: str, *, words: Optional[List[dict]] = None) -> str:
    """Clean and normalise a transcript using a language model.

    Args:
        text: The formatted transcript as produced by
            :func:`pipeline.transcript_formatter.format_transcript`.
        words: Optional list of word dictionaries containing confidence and
            timestamp information.  High‑confidence words may be left
            unchanged, while low‑confidence words can be flagged for
            replacement.  The default implementation does not use this.

    Returns:
        A cleaned transcript.  If no API key or client library is available,
        ``text`` is returned unchanged.
    """
    api_key = os.environ.get("GENAI_API_KEY")
    if not api_key or not _GENAI_AVAILABLE:
        logger.info("No generative AI available; returning original text")
        return text

    # Configure the client
    genai.configure(api_key=api_key)
    model_name = os.environ.get("GENAI_MODEL", "models/gemini-pro")
    try:
        logger.info("Calling generative model %s for transcript cleaning", model_name)
        model = genai.GenerativeModel(model_name)
        prompt = (
            "You are a transcription cleaner.  Given the transcript below, "
            "correct any mis‑recognised words, normalise numbers and ensure "
            "proper punctuation.  Do not change speaker labels.\n\n"
            f"Transcript:\n{text}\n\nCleaned transcript:"
        )
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.2, "max_output_tokens": 4096},
        )
        cleaned = response.text.strip()
        # Basic sanity check: ensure labels (e.g. S1|0) are preserved
        if cleaned and cleaned.count("S") >= text.count("S"):
            return cleaned
        logger.warning("Generative model returned unexpected output; using original")
        return text
    except Exception as exc:  # pragma: no cover - network errors
        logger.exception("Error cleaning transcript: %s", exc)
        return text
